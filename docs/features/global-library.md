# 📚 Biblioteca Global Unificada

A **Biblioteca Global** é o coração da experiência de navegação do Furious App v3.1. Ela substitui a antiga lista simples por um gerenciador de conteúdo robusto e centralizado.

## 🌟 Principais Recursos

### 1. Agregação de Fontes
Ao contrário de listar itens por fonte individualmente, a Biblioteca Global:
- **Indexa** todos os itens de todos os arquivos JSON carregados (`sources/`).
- **Unifica** itens duplicados ou múltiplas versões do mesmo jogo em um único "Card".
- **Normaliza** nomes para facilitar a busca (ex: remove "GOTY Edition", "Repack", etc para agrupamento).

### 2. Interface "Netflix-like"
- **Paginação Virtual**: Suporta milhares de itens sem travar a interface.
- **Cache de Imagens**: As capas são cacheadas localmente no navegador (IndexedDB/LocalStorage) para carregamento instantâneo.
- **Design Cyberpunk**: Cards com efeitos de hover, gradientes e badges informativos.

### 3. Gestão de Versões
Quando um jogo possui múltiplas fontes (ex: FitGirl, Dodi, ElAmigos):
- O card exibe um botão **"Escolher versão"**.
- Ao clicar, um modal exibe todas as opções disponíveis com:
  - Nome do Release.
  - Tamanho.
  - Data de Upload (novidade v3.1).
  - Seeds/Leechers (se disponível).

### 4. Funcionalidades de Manutenção
No topo da biblioteca, você encontra controles para:
- **Atualizar**: Força o re-download dos JSONs das fontes originais.
- **Limpar Cache**: Remove imagens e metadados cacheados para liberar memória ou corrigir imagens quebradas.
- **Busca Global**: Filtra instantaneamente por nome em todo o catálogo.

## 🛠️ Como funciona (Técnico)
- **Frontend**: Vue.js + Pinia (`LibraryStore`).
- **Agrupamento**: Feito no frontend após carregar os JSONs "raw" do backend.
- **Performance**: Usa `v-show` e paginação manual para renderizar apenas o necessário no DOM.
