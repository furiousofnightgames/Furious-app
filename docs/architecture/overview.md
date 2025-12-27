# Visão Geral da Arquitetura

## Diagrama de Alto Nível

```mermaid
graph TD
    A[Frontend Vue.js] <-->|WebSocket/HTTP| B[Backend FastAPI]
    B <--> C[(Banco de Dados SQLite)]
    B <--> D[Motor de Downloads]
    D <--> E[Steam API]
    D <--> F[SteamGridDB]
    D <--> G[Serviços Externos]
    H[Launcher Electron] -->|Inicia| B
    H -->|Contém| I[Python Embarcado]
    H -->|Contém| J[Aria2]
```

## Componentes Principais

### 1. Frontend (Vue.js 3 + Vite)
- **Tecnologias**: Vue 3, Pinia (gerenciamento de estado), Vue Router, TailwindCSS
- **Características**:
  - Interface reativa e responsiva
  - Atualizações em tempo real via WebSocket
  - Componentes modulares e reutilizáveis
  - Suporte a temas (claro/escudo)

### 2. Backend (FastAPI + SQLModel)
- **Tecnologias**: Python 3.10+, FastAPI, SQLModel, SQLAlchemy, Pydantic
- **Características**:
  - API RESTful com documentação automática (Swagger/OpenAPI)
  - WebSockets para atualizações em tempo real
  - Validação de dados com Pydantic
  - ORM moderno com SQLModel (combina SQLAlchemy + Pydantic)

### 3. Banco de Dados
- **Tecnologia**: SQLite
- **Estrutura**:
  - Tabelas principais: `source`, `item`, `job`, `jobpart`, `favorite`
  - Resolver: `resolveralias` (auto-aprendizado local: chave normalizada -> AppID)
  - Migrações manuais (sem sistema de migração automática atualmente)

### 4. Motor de Downloads
- **Tecnologias**: Aria2 (C++), Python (wrapper)
- **Funcionalidades**:
  - Gerenciamento de filas de download (estados: queued, running, paused, completed, failed, canceled)
  - Suporte a múltiplas conexões (segmentação automática)
  - Pausa/continuação/cancelamento seguros
  - Suporte a HTTP/HTTPS com Range requests
  - Suporte a Magnet e Torrent via Aria2 (trackers públicos embutidos)
  - Retentativas automáticas com backoff
  - Limpeza segura de arquivos temporários ao cancelar
  - Detecção automática do binário aria2c

### 5. Integração com Steam
- **APIs**: Steam Web API, SteamGridDB API
- **Funcionalidades**:
  - Busca de jogos na biblioteca Steam
  - Download de metadados (imagens, descrições)
  - Cache local de imagens

### 6. Serviço de Análise (New!)
- **Responsabilidade**: Comparar saúde de torrents antes do download.
- **Funcionalidades**:
  - **Live Probe**: Consulta UDP a até 40 rastreadores em tempo real.
  - **Heurística**: Normalização de nomes para encontrar equivalentes.
  - **Sanidade**: Filtro automático de dados falsos (seeds > 500k).

## Fluxo de Dados

1. **Inicialização**:
   - O Launcher inicia o backend FastAPI
   - O frontend se conecta via WebSocket
   - Dados iniciais são carregados (fontes, downloads ativos, favoritos)

2. **Adição de Nova Fonte**:
   - Usuário adiciona uma URL de fonte JSON
   - Backend valida e processa o JSON
   - Itens são armazenados no banco de dados
   - Frontend é notificado via WebSocket

3. **Início de Download**:
   - Usuário inicia um download
   - Backend cria um job no banco de dados
   - Motor de downloads é acionado
   - Progresso é enviado via WebSocket

4. **Atualização em Tempo Real**:
   - O motor de downloads atualiza o progresso
   - Backend propaga via WebSocket
   - Frontend atualiza a UI em tempo real

## Decisões de Design

1. **Arquitetura Híbrida**:
   - Combina SPA (Single Page Application) com backend API
   - Permite desenvolvimento e teste independentes
   - Facilita futuras migrações de frontend/backend

2. **Banco de Dados SQLite**:
   - Escolhido por simplicidade e portabilidade
   - Não requer servidor de banco de dados separado
   - Fácil backup (apenas copiar o arquivo)

3. **WebSockets para Atualizações em Tempo Real**:
   - Melhor experiência do usuário
   - Reduz chamadas HTTP desnecessárias
   - Atualizações em tempo real dentro da aplicação

4. **Contêinerização de Dependências**:
   - Python e Aria2 incluídos como binários portáteis
   - Sem necessidade de instalação no sistema
   - Facilita a distribuição

## Limitações Conhecidas

1. **Escalabilidade**:
   - SQLite pode ter problemas com alta concorrência
   - Aplicação local-first (uso típico: 1 usuário por máquina)

2. **Segurança**:
   - Aplicação local-first (localhost). Não foi projetada para exposição pública.

3. **Performance**:
   - Processamento de JSON grandes pode ser lento
   - Interface pode travar com muitas atualizações simultâneas

## Próximos Passos

1. Deduplicação/imagens: reduzir falsos positivos e melhorar consistência
2. Busca na biblioteca em grandes volumes (se necessário)
3. Resiliência de download: sugerir alternativas do mesmo grupo ao falhar
4. Melhorias na análise pré-download: mais fontes e heurísticas mais precisas
