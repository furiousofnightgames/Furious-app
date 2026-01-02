# Documentação da API

## Visão Geral

A API do Furious App é baseada em REST e utiliza JSON para troca de dados. A aplicação é **local-first**: por padrão roda em `localhost` (ou `127.0.0.1`) e **não exige autenticação**.

Para a documentação sempre atualizada, consulte o Swagger/OpenAPI do próprio servidor:

- `http://127.0.0.1:8000/docs` (modo local via `py run.py`)
- `http://localhost:8001/docs` (quando executando via Electron)

## Endpoints Principais

## Endpoints (inventário completo)

Observação: os endpoints abaixo refletem o que existe no `backend/main.py`.

### 1. Gerenciamento de Fontes

#### Listar Fontes
```http
GET /api/sources
```
**Resposta de Sucesso (200 OK):**
```json
[
  {
    "id": 1,
    "title": "Minha Fonte",
    "url": "https://exemplo.com/fonte.json",
    "created_at": "2023-01-01T00:00:00"
  }
]
```

#### Adicionar Fonte
```http
POST /api/sources
Content-Type: application/json

{
  "name": "Nova Fonte",
  "url": "https://exemplo.com/nova-fonte.json"
}
```

> Nota: na implementação atual, os itens da fonte são carregados sob demanda via `GET /api/sources/{source_id}/items`.
**Resposta de Sucesso (201 Created):**
```json
{
  "id": 2,
  "name": "Nova Fonte",
  "url": "https://exemplo.com/nova-fonte.json",
  "created_at": "2023-01-02T00:00:00"
}
```

#### Remover Fonte
```http
DELETE /api/sources/{source_id}
```
**Resposta de Sucesso (204 No Content)**

#### Listar Itens de uma Fonte (carregamento sob demanda)
```http
GET /api/sources/{source_id}/items
```

#### Buscar 1 Item específico de uma Fonte
```http
GET /api/sources/{source_id}/items/{item_id}
```

### 2. Gerenciamento de Itens

#### Listar Itens de uma Fonte
```http
GET /api/sources/{source_id}/items
```
**Parâmetros de Consulta:**
- `page` (opcional, padrão: 1)
- `per_page` (opcional, padrão: 50)
- `search` (opcional, texto para busca)

**Resposta de Sucesso (200 OK):**
```json
{
  "items": [
    {
      "id": 1,
      "source_id": 1,
      "name": "Item de Exemplo",
      "url": "https://exemplo.com/download",
      "size": 10485760,
      "is_favorite": false
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 50
}
```

### 3. Análise de Fontes (Pré-Job)

#### Analisar Fontes
Verifica a saúde de um item em todas as fontes disponíveis e retorna sugestões.

```http
POST /api/analysis/pre-job
Content-Type: application/json

{
  "item": {
    "id": 123,
    "source_id": 1,
    "name": "Nome do Jogo",
    "url": "magnet:?xt=urn:...",
    "size": 123456789,
    "uploadDate": "2025-12-27T00:00:00Z"
  }
}
```

**Resposta de Sucesso (200 OK):**
```json
{
  "original_health": { "score": 25, "seeders": 1, "label": "Fraco" },
  "candidates": [
    {
      "source_title": "DODI",
      "item": { "name": "Game v1.0", "size": 123456789, "uploadDate": "2025-12-27T00:00:00Z" },
      "health": { "score": 100, "seeders": 140, "label": "Excelente" }
    }
  ]
}
```

### 3.1 Telemetria do Resolver (diagnóstico)

#### Ler contadores
```http
GET /api/resolver/telemetry
```

#### Resetar contadores
```http
POST /api/resolver/telemetry/reset
```

### 3.2 Biblioteca (deduplicada)

```http
GET /api/library
```

### 3.3 Resolver / Steam / Detalhes

#### Resolver de imagens
```http
POST /api/resolver?game_name=...
```

#### Imagens Steam (arte)
```http
GET /api/steam/artes?term=...
```

#### Detalhes completos (imagens + vídeos + screenshots)
```http
GET /api/game-details/{app_id_or_name}
```

### 3.4 Cache

#### Limpar caches
```http
POST /api/cache/clear
```

### 4. Gerenciamento de Downloads

#### Listar Jobs
```http
GET /api/jobs
```
**Parâmetros de Consulta:**
- `status` (opcional, filtrar por status: "downloading", "paused", "completed", "error")

**Resposta de Sucesso (200 OK):**
```json
[
  {
    "id": 1,
    "item_id": 1,
    "name": "Arquivo Grande",
    "status": "downloading",
    "progress": 42.5,
    "speed": 1024,
    "size": 10485760,
    "downloaded": 4456448,
    "created_at": "2023-01-01T00:00:00",
    "updated_at": "2023-01-01T00:10:00"
  }
]
```

#### Iniciar Download
```http
POST /api/jobs
Content-Type: application/json

{
  "item_id": 1,
  "url": "https://exemplo.com/arquivo.iso",
  "name": "Arquivo Grande",
  "size": 10485760,
  "k": 4,
  "n_conns": 4,
  "resume_on_start": true
}
```
**Resposta de Sucesso (201 Created):**
```json
{
  "id": 1,
  "status": "queued",
  "message": "Download adicionado à fila"
}
```

#### Pausar Download
```http
POST /api/jobs/{job_id}/pause
```
**Resposta de Sucesso (200 OK):**
```json
{
  "status": "success",
  "message": "Download pausado"
}
```

#### Continuar Download
```http
POST /api/jobs/{job_id}/resume
```
**Resposta de Sucesso (200 OK):**
```json
{
  "status": "success",
  "message": "Download retomado"
}
```

#### Cancelar Download
```http
DELETE /api/jobs/{job_id}
```
**Resposta de Sucesso (200 OK):**
```json
{
  "status": "success",
  "message": "Download cancelado"
}
```

#### Pausar
```http
POST /api/jobs/{job_id}/pause
```

#### Retomar
```http
POST /api/jobs/{job_id}/resume
```

#### Cancelar (mantém no histórico como cancelado)
```http
POST /api/jobs/{job_id}/cancel
```

#### Listar partes do job (quando segmentado)
```http
GET /api/jobs/{job_id}/parts
```

#### Abrir pasta do download no Explorer
```http
POST /api/jobs/open-folder
Content-Type: application/json

{"path": "C:\\..."}
```

#### Limpezas (apenas IDs visíveis enviados pelo frontend)
```http
DELETE /api/jobs/completed/clear
DELETE /api/jobs/failed/clear
DELETE /api/jobs/canceled/clear
```

### 4.1 Suporte a Range (downloads diretos)

```http
GET /api/supports_range?url=...
```

### 4. Gerenciamento de Favoritos

#### Listar Favoritos
```http
GET /api/favorites
```
**Resposta de Sucesso (200 OK):**
```json
[
  {
    "id": 1,
    "source_id": 1,
    "item_id": 1,
    "name": "Meu Jogo Favorito",
    "url": "https://exemplo.com/jogo",
    "created_at": "2023-01-01T00:00:00"
  }
]
```

#### Adicionar Favorito
```http
POST /api/favorites
Content-Type: application/json

{
  "source_id": 1,
  "item_id": 123,
  "name": "Meu Jogo Favorito",
  "url": "magnet:?xt=...",
  "image": "https://cdn.akamai.steamstatic.com/steam/apps/123/header.jpg"
}
```
**Resposta de Sucesso (201 Created):**
```json
{
  "id": 1,
  "source_id": 1,
  "item_id": 123,
  "name": "Meu Jogo Favorito",
  "url": "magnet:?xt=...",
  "image": "https://cdn.akamai.steamstatic.com/steam/apps/123/header.jpg",
  "created_at": "2026-01-02T12:00:00Z"
}
```

> **Novidade v3.1.0**: Campo `image` agora é salvo e retornado. Se não fornecido, a gaveta de favoritos resolve automaticamente via Steam/SteamGridDB.

#### Remover Favorito
```http
DELETE /api/favorites/{favorite_id}
```
**Resposta de Sucesso (204 No Content)**

#### Remover Favorito por item
```http
DELETE /api/favorites/by_item?source_id=...&item_id=...
```

### 5. WebSocket para Atualizações em Tempo Real

**Endpoint WebSocket:**
```
ws://localhost:8000/ws
```

Mensagem keep-alive do client: qualquer texto (o servidor responde `{ "type": "ack" }`).

**Mensagens Enviadas pelo Servidor:**
```json
{
  "type": "job_progress",
  "data": {
    "job_id": 1,
    "status": "downloading",
    "progress": 45.2,
    "speed": 1048576,
    "eta": 120
  }
}

{
  "type": "job_complete",
  "data": {
    "job_id": 1,
    "status": "completed",
    "download_path": "C:/Users/Usuario/Downloads/item.bin"
  }
}

{
  "type": "job_error",
  "data": {
    "job_id": 1,
    "status": "error",
    "error": "Failed to download: connection timeout"
  }
}
```

## Códigos de Status HTTP

- `200 OK`: Requisição bem-sucedida
- `201 Created`: Recurso criado com sucesso
- `204 No Content`: Recurso excluído com sucesso
- `400 Bad Request`: Dados inválidos na requisição
- `401 Unauthorized`: Autenticação necessária
- `403 Forbidden`: Acesso negado
- `404 Not Found`: Recurso não encontrado
- `409 Conflict`: Conflito (ex: recurso já existe)
- `500 Internal Server Error`: Erro interno do servidor

## Tratamento de Erros

Todas as respostas de erro seguem o formato:
```json
{
  "detail": "Mensagem de erro descritiva",
  "code": "codigo_do_erro",
  "status_code": 400
}
```

## Limites e Cotas

- Tamanho máximo do corpo da requisição: 10MB
- Máximo de conexões simultâneas por IP: 20
- Taxa de requisições: 100 por minuto por IP

## Versão da API

A versão atual da API é `v1`. Todas as rotas estão prefixadas com `/api`.

## Endpoints auxiliares (diagnóstico/proxy)

#### Proxy de imagens (para contornar limitações de carregamento em alguns ambientes)
```http
GET /api/proxy/image?url=...
```

#### Proxy de vídeo
```http
GET /api/proxy/video?url=...
```

#### Diagnóstico de vídeos
```http
GET /api/debug/videos
```

#### Status do aria2 (detecção de binário)
```http
GET /api/aria2/status
```

#### Dialog nativo de selecionar pasta
```http
POST /api/dialog/select_folder
```

## Exemplo de Uso com JavaScript

```javascript
// Listar fontes
async function getSources() {
  const response = await fetch('http://localhost:8000/api/sources');
  return await response.json();
}

// Iniciar download
async function startDownload(item) {
  const response = await fetch('http://localhost:8000/api/jobs', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      item_id: item.id,
      url: item.url,
      name: item.name,
      size: item.size
    })
  });
  return await response.json();
}

// Conectar ao WebSocket para atualizações em tempo real
function connectWebSocket() {
  const ws = new WebSocket('ws://localhost:8000/ws');
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    switch (data.type) {
      case 'job_progress':
        console.log('Atualização de progresso:', data.data);
        break;
      case 'job_complete':
        console.log('Download concluído:', data.data);
        break;
      case 'job_error':
        console.error('Erro no download:', data.data);
        break;
    }
  };
  
  return ws;
}
```
