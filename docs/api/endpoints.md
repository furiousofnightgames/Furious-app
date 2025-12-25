# Documentação da API

## Visão Geral

A API do Furious App é baseada em REST e utiliza JSON para troca de dados. A maioria dos endpoints requer autenticação via token JWT no cabeçalho `Authorization`.

### Autenticação

```http
Authorization: Bearer <seu_token_aqui>
```

## Endpoints Principais

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
    "name": "Minha Fonte",
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
  "item_id": "string",
  "source_id": "string",
  "title": "Nome do Jogo",
  "uris": ["magnet:?xt=urn:...", "http://..."]
}
```

**Resposta de Sucesso (200 OK):**
```json
{
  "original_score": { "score": 25, "seeders": 1, "label": "Fraco" },
  "alternatives": [
    {
      "source_name": "DODI",
      "item": { "name": "Game v1.0", "size": "10 GB" },
      "score": { "score": 100, "seeders": 140, "label": "Excelente" }
    }
  ]
}
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
  "item_id": 1,
  "name": "Meu Jogo Favorito",
  "url": "https://exemplo.com/jogo"
}
```
**Resposta de Sucesso (201 Created):**
```json
{
  "id": 1,
  "source_id": 1,
  "item_id": 1,
  "name": "Meu Jogo Favorito",
  "url": "https://exemplo.com/jogo",
  "created_at": "2023-01-01T00:00:00"
}
```

#### Remover Favorito
```http
DELETE /api/favorites/{favorite_id}
```
**Resposta de Sucesso (204 No Content)**

### 5. WebSocket para Atualizações em Tempo Real

**Endpoint WebSocket:**
```
ws://localhost:8000/ws
```

**Mensagens Enviadas pelo Servidor:**
```json
{
  "type": "job_update",
  "data": {
    "job_id": 1,
    "status": "downloading",
    "progress": 42.5,
    "speed": 1024,
    "downloaded": 4456448
  }
}

{
  "type": "job_complete",
  "data": {
    "job_id": 1,
    "status": "completed",
    "path": "/caminho/para/arquivo"
  }
}

{
  "type": "job_error",
  "data": {
    "job_id": 1,
    "status": "error",
    "error": "Erro ao baixar o arquivo"
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

## Exemplo de Uso com JavaScript

```javascript
// Listar fontes
async function getSources() {
  const response = await fetch('http://localhost:8000/api/sources', {
    headers: {
      'Authorization': 'Bearer seu_token_aqui'
    }
  });
  return await response.json();
}

// Iniciar download
async function startDownload(item) {
  const response = await fetch('http://localhost:8000/api/jobs', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer seu_token_aqui'
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
      case 'job_update':
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
