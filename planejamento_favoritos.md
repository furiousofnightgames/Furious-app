# Planejamento – Sistema de Favoritos com Menu Hambúrguer

## Visão Geral
Implementar um **sistema de itens favoritos** acessível por um **menu hambúrguer (☰)** no lado esquerdo da navbar, **sem impactar funcionalidades existentes**.  
O objetivo é permitir acesso rápido aos itens favoritos e permitindo o usuário iniciar o download com mais facilidade.

---

## Objetivos do Recurso
- Permitir favoritar itens de jogos (por fonte).
- Centralizar favoritos em um painel lateral (drawer).
- Reduzir o fluxo de navegação para downloads recorrentes.
- Não quebrar nem refatorar o código atual.

---

## Escopo Funcional
✔ Botão de favoritar em cada item  
✔ Menu hambúrguer na navbar (lado esquerdo)  
✔ Aba lateral com largura fixa (~5 dedos ≈ 320px)  
✔ Lista simples: **nome principal do item limpo para nao ficar muito grande na lista de favoritos**  
✔ Clique no item:
  - Carrega automaticamente a fonte correta
  - Abre a página de detalhes do item
✔ Persistência local dos favoritos  

---

## Arquitetura de Alto Nível

### Frontend (Vue + Vite + Electron)
- Estado local + persistência
- Drawer lateral controlado por estado global
- Navegação programática para detalhes

### Backend
- **Nenhuma alteração obrigatória**
- Sistema funciona apenas com IDs existentes
- Backend continua stateless para favoritos

---

## Estrutura de Dados (Frontend)

### Modelo Favorito
```ts
FavoriteItem {
  id: string
  name: string
  source: string
}
```

### Persistência
- `localStorage` usando o banco de dados local ja existente na aplicação
- Chave sugerida: `favorites.items`

---

## Componentes a Criar (Isolados)

### 1. HamburgerButton.vue
- Ícone ☰
- Local: Navbar (lado esquerdo)
- Emite evento `toggleFavorites`

### 2. FavoritesDrawer.vue
- Drawer lateral esquerdo
- Largura fixa (~320px)
- Lista simples (`v-for`)
- Scroll vertical independente

### 3. FavoriteToggleButton.vue
- Ícone ⭐ em svg nada de emots
- Acoplado ao card do item
- Não altera layout existente

---

## Fluxo de Interação

### Favoritar Item
1. Usuário clica ⭐ no card
2. Item salvo no storage local
3. Estado global atualizado

### Abrir Favoritos
1. Usuário clica ☰
2. Drawer abre suavemente
3. Lista renderizada

### Selecionar Favorito
1. Clique no nome do item
2. App:
   - Seleciona a fonte correta
   - Navega para página de detalhes
3. Usuário inicia download imediatamente

---

## Integração com Navegação
- Usar `router.push()`
- Passar:
  - `source`
  - `itemId`
- Página de detalhes reutilizada (sem duplicação)

---

## Requisitos Não-Funcionais
- Zero impacto no fluxo atual
- Código isolado e removível
- Sem chamadas extras ao backend
- Performance instantânea

---

## Estratégia de Implementação (Segura)

### Fase 1 – UI
- Criar botão ☰
- Criar drawer estático

### Fase 2 – Favoritar
- Botão ⭐ nos itens
- Persistência local

### Fase 3 – Navegação
- Linkar favoritos → detalhes
- Testar troca automática de fonte

---

## Riscos e Mitigações
| Risco | Mitigação |
|-----|----------|
| Quebrar layout | Componentes isolados |
| Estado inconsistente | Fonte como chave obrigatória |
| UX poluído | Lista apenas com nome |

---

## Critério de Sucesso
- Favoritar em 1 clique
- Acessar item favorito em 2 cliques
- Nenhuma regressão detectada

---

## Status
📌 Planejamento aprovado para implementação incremental.
