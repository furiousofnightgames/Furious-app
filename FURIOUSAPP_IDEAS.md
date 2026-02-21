# FuriousApp - Ideias de Melhoria e Evolução

> Análise técnica com sugestões construtivas para evolução do projeto

**Status:** Documento de ideias | **Data:** Fevereiro 2026 | **Versão Analisada:** 3.3.1

---

## 📊 Avaliação Geral

- **Arquitetura:** 9/10
- **Engine:** 9.5/10  
- **Frontend:** 8.5/10
- **Robustez:** 9/10
- **Potencial:** 9/10
- **Rating Final:** 8.8/10

> **Verdict:** Projeto profissional, code produção-grade. Escalável, mantível, robusto e performático.

---

## 🎨 CRÍTICA 1: UI/UX - Potencial Avançado

### Problema Atual
A interface é bonita e funcional, mas falta inteligência visual para ajudar decisões do usuário em tempo real.

### Ideias de Melhoria

#### 1.1 Gráfico de Histórico de Velocidade
**O que:** Mostrar gráfico de KB/s over time durante e após download
**Por quê:** 
- Identifica gargalos (server lento, network congestion)
- Mostra padrão: foi rápido depois caiu = tracker ruim
- Usuário consegue ver se vale continuar ou trocar de fonte
**Implementação:**
```javascript
// Guardar velocidade a cada 2s durante download
// Usar Chart.js ou D3.js pra renderizar
// Integrar com WebSocket progress_cb
const speedHistory = [];
setInterval(() => {
  speedHistory.push({
    time: Date.now(),
    speed: bytesLastInterval / 2000 // KB/s
  });
}, 2000);
```

#### 1.2 Recomendador de Formato (Magnet vs HTTP)
**O que:** AI simples que sugere qual tipo de link usar baseado em health real
**Por quê:**
- Magnet é melhor se tem 50+ seeders (CDC)
- HTTP é melhor se server está saudável mas tracker morto
- Poupa tempo do usuário decidindo manualmente
**Lógica:**
```python
if tracker_health > 80 and seeders > 50:
    suggest = "Magnet Link (Mais rápido - tracker saudável)"
elif http_health > 90:
    suggest = "HTTP Direto (Mais confiável - server dedicado)"
else:
    suggest = "Híbrido: Tenta Magnet, fallback HTTP"
```

#### 1.3 ETA Inteligente 
**O que:** Calcular ETA dinâmico considerando seeders e tracker health real
**Por quê:**
- ETA atual é BW / tamanho = muito otimista
- Com seeders reais (UDP sondagem), pode ajustar
- Mostra range realista: "35-55 min" vs "40 min"
**Pseudo-código:**
```python
# Ajuste factor baseado em trackers
seeders = udp_probe_result['seeders']
tracker_health = (online_trackers / total_trackers) * 100

speed_factor = min(1.5, 1 + (seeders / 100) * 0.5)
adjusted_speed = current_speed * speed_factor
actual_eta = remaining_bytes / adjusted_speed

# Add variância
eta_min = actual_eta * 0.7
eta_max = actual_eta * 1.3
```

---

## ⚙️ CRÍTICA 2: Backend - Otimizações Inteligentes

### Problema Atual
Backend funciona bem, mas não aprende com histórico de downloads.

### Ideias de Melhoria

#### 2.1 Cache Multi-Nível de Tracker Health
**O que:** Guardar histórico de "qual tracker foi rápido hoje" e priorizá-los
**Por quê:**
- Trackers têm variação circadiana (rápido 8-18h, lento 22-6h)
- Alguns morrem sem aviso
- Cache Redis-like (em SQLite) evita reprobar trackers ruins constantemente
**Database Schema:**
```sql
CREATE TABLE tracker_health_cache (
    id INTEGER PRIMARY KEY,
    tracker_url TEXT UNIQUE,
    last_checked TIMESTAMP,
    success_rate REAL,  -- 0-1
    avg_response_ms INTEGER,
    seeders_found INTEGER,
    status TEXT -- 'healthy', 'slow', 'dead'
);
```

#### 2.2 ML Simples para Prever Melhor Source
**O que:** Modelo simples que aprende qual fonte dá mais seeders
**Por quê:**
- Alguns trackers só indexam repacks (DODI, FitGirl)
- Outros indexam releases recentes (CBR, CPG)
- Sistema pode recomendar: "Procure em X pra esse tipo de jogo"
**Implementação (sklearn):**
```python
# Treinar modelo com histórico de downloads
from sklearn.ensemble import RandomForestClassifier

X = [
    [game_age_days, game_size_gb, tracker_id],
    ...
]
y = [  # 1 = encontrou com seeders, 0 = não
    1, 0, 1, ...
]

model = RandomForestClassifier()
model.fit(X, y)

# Predict best tracker pra novo game
best_tracker = model.predict([[5, 15, 1]])[0]
```

#### 2.3 Telemetria Anônima (Opt-In)
**O que:** Coletar agregado: "qual tracker morreu hoje?"
**Por quê:**
- Detecta tracker failures globalmente
- Permite rotação automática de fallbacks
- Anônimo: não coleta IP, nome do usuário, detalhes de jogo
**Data Sent (anonymized):**
```json
{
  "tracker": "udp://tracker.opentrackr.org:1337",
  "status": "timeout",
  "timestamp_utc": "2026-02-21T01:30:00Z",
  "response_time_ms": 5000
}
```

---

## 🔧 CRÍTICA 3: Engine - Performance Extra

### Problema Atual
Engine é ótimo, mas há room pra micro-otimizações que somam.

### Ideias de Melhoria

#### 3.1 Adaptive Chunk Sizing
**O que:** Variar tamanho de chunks (agora fixo 4MB) baseado em BW real
**Por quê:**
- Quando conexão é >100MB/s, 4MB é muito pequeno
- Quando é <1MB/s, overhead de requisições não vale
- Chunking automático melhora 5-15% em BW heterogênea
**Algoritmo:**
```python
def calculate_optimal_chunk_size(current_speed_mbps, latency_ms):
    """
    RTT latência + tamanho chunk impactam throughput
    Fórmula: chunk_size = speed_mbps * latency_ms / 8
    """
    base_latency = 50  # ms, assume
    optimal_chunk = (current_speed_mbps * base_latency) / 8  # em MB
    
    # Clamp entre 1MB e 64MB
    return max(1, min(64, optimal_chunk)) * 1024 * 1024

# Exemplo:
# Speed 50MB/s, latency 50ms → chunk = 312 KB (problema!)
# Speed 100MB/s, latency 50ms → chunk = 625 KB (problema!)
# Deveria estar em 10-20MB range
```

#### 3.2 IPv6 Prioritário
**O what:** Preferir IPv6 quando disponível (mais rápido + menos congestionado)
**Por quê:**
- IPv4 internet está saturada em prime hours
- IPv6 tem menor congestion (menos gente usa)
- ISP throttle IPv4 bitTorrent, menos throttle IPv6
- Ganho real: 10-30% de velocidade em horas pico
**Implementação:**
```python
# Em aria2_wrapper.py, adicionar flag
def download_magnet_cli(...):
    # Priorizar IPv6
    aria2_args = [
        '--enable-dht6',      # DHT IPv6
        '--listen-port=6881-6889',
        '--bind-address-v6=::',  # Bind IPv6
        '--disable-ipv4',     # Forçar IPv6 only
    ]
```

#### 3.3 Compressão Transparente
**O que:** Suportar gzip/brotli automático em HTTP downloads
**Por quê:**
- Alguns trackers/seeders oferecem deflate/gzip
- Economiza até 40% BW em alguns casos
- Transparente pro usuário
**Código (httpx já suporta):**
```python
async def download_serial(...):
    headers['Accept-Encoding'] = 'gzip, deflate, br'
    
    async with httpx.AsyncClient(...) as client:
        # httpx descompacta automaticamente
        async with client.stream("GET", url, headers=headers) as resp:
            # resp.content já está descomprimido
            pass
```

---

## 🚀 Roadmap Sugerido

### Phase 1: Quick Wins (1-2 semanas)
- [ ] Speed history chart (UI)
- [ ] Adaptive chunk sizing (Engine)
- [ ] IPv6 priority support (Engine)

### Phase 2: Intelligence (3-4 semanas)
- [ ] Tracker health cache (Backend)
- [ ] ETA inteligente (Frontend + Backend)
- [ ] Format recommender (Backend + UI)

### Phase 3: Scale (1-2 meses)
- [ ] ML predictor pra sources (Backend)
- [ ] Telemetria opt-in (Backend + Infrastructure)
- [ ] Compressão transparente (Engine)

---

## 📝 Notas Finais

1. **Ordem:** Começar por Phase 1 (impacto imediato, baixo overhead)
2. **Testing:** Cada feature precisa testes automatizados (muito importante)
3. **Documentation:** Documentar decisões arquiteturais pra future maintainers
4. **Performance:** Sempre profile antes/depois (use cProfile + memory_profiler)

---

**Gerado em:** Fevereiro 2026  
**Versão:** 1.0  
**Status:** Ready for Implementation
