# Filtros de Elite e Navegação 🎨

O sistema de filtros transforma a biblioteca de uma lista simples em um catálogo organizado e explorável, similar a lojas profissionais como Steam ou Epic Games.

## 🌟 Recursos Principais

### 1. Modais de Seleção (Glassmorphic)
Substituímos os dropdowns nativos feios por modais de tela cheia com design **Glassmorphism** (efeito de vidro).
- **Busca Interna**: Cada modal (Gênero, Desenvolvedora) tem sua própria barra de busca ultra-rápida.
- **Multisseleção**: O usuário pode selecionar "RPG" + "Ação" simultaneamente.
- **Grid Visual**: Itens organizados em grid responsivo, não em listas textuais.

### 2. Lógica de Filtragem (Client-Side)
Toda a filtragem acontece instantaneamente no cliente (Vue.js), garantindo 60 FPS mesmo com milhares de itens.
- **Combinação de Critérios**: `(Gênero: RPG) AND (Dev: FromSoftware) AND (Busca: "Ring")`
- **Normalização**: Ignora acentos e maiúsculas/minúsculas para facilitar a busca.

### 3. Extração de Metadados
Os filtros são alimentados por metadados extraídos automaticamente:
- **Steam API**: O sistema coleta Gêneros e Desenvolvedoras via `SteamService`.
- **Persistência**: Esses dados são salvos no SQLite (`GameMetadata`) para que os filtros funcionem offline e instantaneamente na próxima sessão.

### 4. Ordenação Inteligente
- **Recentes**: Ordena pela data de adição à loja (padrão).
- **Alfabética (A-Z)**: Para navegar em catálogos grandes.
- **Tamanho**: Útil para encontrar jogos pequenos ou gigantes.

## 🛠️ Tecnologias

- **Componente**: `FilterSelectionModal.vue`
- **Estado**: `library.js` (Pinia Store)
- **Estilo**: Tailwind CSS (`backdrop-blur`, `bg-opacity`, `transition-all`)
