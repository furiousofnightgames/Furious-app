# Frontend - Launcher JSON Accelerator

Frontend Vue 3 com tema cyberpunk para gerenciar downloads acelerados.

## Setup

```bash
cd frontend
npm install
npm run build
npm run dev  # para desenvolvimento
```

## Build

```bash
npm run build
# Output: ./dist
```

## Estrutura

- `src/components/` - Componentes reutilizáveis
- `src/views/` - Páginas (Dashboard, Downloads, Sources, NewDownload)
- `src/stores/` - Pinia store para estado
- `src/services/` - Cliente API (Axios)
- `src/styles/` - CSS (Tailwind + Cyberpunk)

## Rotas

- `/` - Dashboard
- `/downloads` - Gerenciar downloads
- `/sources` - Fontes JSON
- `/new` - Novo download
