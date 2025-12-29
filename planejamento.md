# Planejamento Estratégico – Evolução Furious App

## Visão Geral
A Furious App é uma aplicação **100% local, offline-first e independente de servidores**, entregue ao usuário final como um produto completo via instalador. Não há coleta de dados, contas, sincronização externa ou qualquer tipo de comunicação remota com serviços próprios. Esse é um **diferencial estratégico central** e deve ser preservado em todas as evoluções.

O objetivo deste planejamento é **superar o Hydra Launcher em todos os sentidos relevantes**, sem comprometer a estabilidade atual, priorizando apenas evoluções **compatíveis com a arquitetura existente** (Frontend + Backend + Engine desacoplados).

Princípio norteador:
> _Nenhuma feature nova deve quebrar, acoplar ou enfraquecer o que já funciona._

---

## Princípios Técnicos Inegociáveis

- Aplicação **totalmente local**
- Nenhuma dependência de servidores próprios
- Backend apenas como orquestrador local
- Engine isolada e substituível
- Frontend reativo, informativo e didático
- Evolução incremental, nunca disruptiva

---

## FASE 1 – Consolidação do que já existe (Alta Prioridade)

### 1. Motor de Decisão Automática de Fonte (Evolução do Resolver)

**Estado atual:**
- Resolver funcional
- Deduplicação implementada
- Escolha manual da fonte pelo usuário

**Evolução proposta (sem quebrar nada):**
- Introduzir um **score local por fonte**, calculado em tempo real
- Critérios possíveis:
  - seeds / peers
  - histórico local de sucesso
  - tempo médio até iniciar
  - estabilidade (pausas, quedas)

**Estratégia:**
- O usuário continua podendo escolher manualmente
- O sistema sugere a melhor opção por padrão

**Diferencial:**
O usuário escolhe **o jogo**, não a fonte.

---

### 2. Pré-download elevado a Pré-flight Check

**Estado atual:**
- Pré-download funcional
- Metadados e análise inicial

**Evolução proposta:**
- Transformar o pré-download em uma **etapa explícita de validação**
- Exibir ao usuário:
  - estimativa realista de início
  - disponibilidade atual
  - aviso de baixa saúde

**Importante:**
- Nenhuma verificação externa
- Tudo baseado em dados locais e do próprio swarm

**Diferencial:**
Redução drástica de downloads problemáticos.

---

## FASE 2 – Experiência de Biblioteca (Médio Prazo)

### 3. Biblioteca Viva Orientada a Jogos (não arquivos)

**Estado atual:**
- Biblioteca paginada
- Cards deduplicados
- Seleção de versões

**Evolução proposta:**
- Tratar cada jogo como uma entidade única
- Histórico local por jogo:
  - versões já baixadas
  - versões disponíveis
  - status (concluído, falhou, em andamento)

**Estratégia:**
- Nenhum banco externo
- Apenas persistência local

**Diferencial:**
A Furious App vira **biblioteca permanente**, não sessão temporária.

---

### 4. Comparador de Versões

**Funcionalidade:**
- Comparar versões do mesmo jogo
- Exibir diferenças relevantes:
  - tamanho
  - idioma
  - DLCs
  - multiplayer

**Benefício:**
Ajuda o usuário a escolher conscientemente, sem depender de fontes externas.

---

## FASE 3 – Controle Avançado (Power User sem complexidade)

### 5. Perfis de Download

**Estado atual:**
- Engine já suporta controle fino

**Evolução proposta:**
- Criar perfis locais:
  - padrão
  - rápido
  - estável
  - customizado

**Implementação segura:**
- Apenas presets
- Nenhuma lógica nova na engine

---

### 6. Fila Inteligente Condicional

**Funcionalidade:**
- Regras simples:
  - iniciar X somente após Y
  - limitar downloads simultâneos

**Importante:**
- Controle central no manager
- UI apenas reflete estado

---

## FASE 4 – Transparência Total (Confiança)

### 7. Log Visual Didático

**Objetivo:**
- Mostrar o que está acontecendo sem jargão técnico

**Exemplos:**
- "Conectando a peers"
- "Velocidade estabilizada"
- "Reconectando fontes"

**Diferencial:**
O usuário confia porque entende.

---

### 8. Métricas Reais de Qualidade

**Métricas sugeridas:**
- Tempo até iniciar (TTI)
- Estabilidade média
- Retomadas bem-sucedidas

**Uso:**
- Informativo
- Nunca comparativo público

---

## FASE 5 – Modularidade e Futuro

### 9. Arquitetura de Módulos Locais

**Visão:**
- Plugins locais
- Sem marketplace
- Sem servidor

**Exemplos futuros:**
- novos parsers
- novos motores
- pós-processamento

---

## Posicionamento Estratégico

- Ferramenta técnica
- Uso geral de downloads
- Nenhuma associação direta a conteúdo
- Documentação clara e neutra

---

## Conclusão

A Furious App já vence em velocidade.
Este planejamento transforma velocidade em **apenas um dos pilares**, ao lado de:

- Inteligência
- Controle
- Confiabilidade
- Independência total

O resultado é um produto **mais sólido, mais profissional e mais sustentável** que qualquer concorrente direto.

