# 🛡️ Pré-flight Check & Segurança

O **Pré-flight Check** (Checagem Pré-voo) é uma camada de segurança e validação adicionada na versão 3.1 para garantir que seus downloads tenham a maior chance possível de sucesso antes mesmo de serem iniciados.

## 🚀 O que ele faz?

Ao clicar em "Baixar" (ou configurar um download), o sistema executa automaticamente:

### 1. Verificação de Backend (aria2)
- Confirma se o motor de download `aria2c` está rodando e respondendo via RPC.
- Evita o erro comum de "Download falhou ao iniciar" por falta de comunicação com o backend.

### 2. Análise da URL
- **Links HTTP/HTTPS**:
  - Faz uma requisição `HEAD`.
  - Verifica o status code (esperado 200 ou 206).
  - Verifica o tamanho do arquivo (`content-length`).
  - Confirma suporte a **Resume** (`accept-ranges: bytes`).

- **Magnet Links**:
  - Usa uma implementação de **DHT/UDP Tracker Probe** customizada.
  - Tenta contatar os trackers listados no magnet link via protocolo UDP.
  - Retorna a contagem real de **Seeders** e **Leechers** ativos no momento.
  - Classifica a saúde do torrent:
    - 🟢 **Saudável**: 20+ seeds
    - 🟡 **Ok**: 5-19 seeds
    - 🔴 **Baixa**: 1-4 seeds
    - ☠️ **Crítica**: 0 seeds

### 3. Feedback Visual
O resultado é exibido no modal de configuração de download:
- Se houver erro (ex: 404 Not Found), um alerta vermelho aparece.
- Se o torrent estiver morto (0 seeds), você é avisado para não perder tempo.

## 🔄 Análise Inteligente (Pré-Job)

Além do check passivo, existe o sistema ativo de recomendação:
1. Se você tenta baixar um item que tem saúde ruim.
2. O sistema busca na **Biblioteca Global** se existem outras versões do mesmo jogo.
3. Se encontrar uma versão com mais seeds ou melhor saúde, ele sugere a troca automática ("Switch Source").
