# Guia do Usuário do Furious App

## 🚀 Introdução

Bem-vindo ao Furious App, um poderoso gerenciador de downloads com suporte a múltiplas fontes, integração com Steam e interface moderna. Este guia irá ajudá-lo a começar e aproveitar ao máximo todos os recursos disponíveis.

## 📥 Instalação

### Requisitos Mínimos
- Windows 10/11 (64-bit)
- 4GB de RAM
- 2GB de espaço livre em disco

### Passo a Passo
1. Baixe o instalador mais recente da nossa página de lançamentos
2. Execute o arquivo `Furious App Setup.exe`
3. Siga as instruções na tela
4. O Furious App será instalado e um atalho será criado na área de trabalho

## 🖥️ Primeiros Passos

### Iniciando o Aplicativo
- Clique duas vezes no ícone do Furious App na área de trabalho
- Aguarde a inicialização (na primeira vez pode levar alguns segundos)
- A aplicação abre em uma janela (Electron). Em modo local (`py run.py`), você acessa via navegador.

### Interface Principal

#### Barra de Navegação Superior
- **Logo**: Clique para voltar à página inicial
- **Menu de Navegação**: Acesse as diferentes seções do aplicativo
- **Indicador de Status**: Mostra o estado da conexão com o servidor
- **Tema**: Alternar entre modo claro e escuro

### 🖥️ Navegação e Telas

### Telas Principais (rotas Vue.js)
- **Dashboard** (`/`): Visão geral com estatísticas e acesso rápido
- **Downloads** (`/downloads`): Lista de downloads ativos e concluídos com controles de pausa/continuar/cancelar
- **Fontes** (`/sources`): Gerenciar fontes JSON e importar da galeria
- **Biblioteca** (`/library`): Itens baixados com metadados Steam/imagens
- **Novo Download** (`/new-download` ou `/`): Fluxo para adicionar fontes e iniciar downloads
- **Detalhes do Item** (`/item/:id`): Página de detalhes com opções de download e análise

### Componentes e Modais
- **SourceAnalysisModal**: Análise pré-download com comparação de saúde de torrents
- **Favoritos**: Acesso rápido via menu lateral
- **Proxy de imagens/vídeos**: Para contornar limitações de carregamento
- **Dialog nativo**: Selecionar pasta de destino

## 🔄 Gerenciando Fontes

### Adicionando uma Fonte
1. Navegue até a seção **Fontes**
2. Clique em **Nova Fonte**
3. Insira um nome descritivo e a URL do arquivo JSON
4. Clique em **Salvar**

### Importando Fontes Populares
Oferecemos uma galeria de fontes populares. Para importar:
1. Vá para **Fontes** > **Galeria**
2. Navegue pela lista ou pesquise por uma fonte
3. Clique em **Adicionar** ao lado da fonte desejada
4. Confirme a adição

### Gerenciando Favoritos (v3.1.0 - Visual Premium)

- **Adicionar aos Favoritos**: Clique na estrela (⭐) em qualquer item
- **Acessar Favoritos**: Clique no ícone de menu (☰) no canto superior esquerdo
  - Gaveta lateral ampliada (420px) com visual inspirado no Hydra Launcher
  - Cada item exibe **ícone/capa do jogo** (resolução automática via Steam)
  - Nomes limpos sem versões/DLCs/repacks
- **Remover Favorito**: Clique no "X" ao lado do item na lista de favoritos
- **Resolução Automática de Imagens**: Ao abrir a gaveta, imagens faltantes são buscadas automaticamente e salvas

## ⬇️ Realizando Downloads

### Iniciando um Download
1. Navegue até a fonte desejada
2. Encontre o item que deseja baixar
3. Clique no botão **Baixar**

### Análise Inteligente (Novo!)
Ao clicar em Baixar, o sistema pode exibir **"Analisando..."**. Isso significa que ele está procurando fontes mais rápidas.
- **Se encontrar**: Uma janela abrirá mostrando opções com "Saúde" (Excelente, Bom, etc).
- **Sua escolha**: Você pode manter sua fonte original ou **Trocar** por uma recomendada.
- **Se não encontrar**: O download segue normalmente.

4. Escolha o local de destino (opcional)
5. Confirme para iniciar o download

### Gerenciando Downloads
- **Pausar/Continuar**: Clique no ícone de pausa/play ao lado do download
- **Cancelar**: Clique no ícone de lixeira para remover o download
- **Abrir Pasta**: Clique no ícone de pasta para abrir o local do download
- **Velocidade**: Ajuste a velocidade máxima nas configurações

### Download em 2º Plano
O Furious App continua baixando enquanto a aplicação estiver aberta.

## 🎮 Biblioteca / Imagens

O Furious App tenta associar capas/imagens automaticamente para jogos exibidos na Biblioteca.
Quando não há correspondência confiável, o app prefere mostrar placeholder em vez de uma imagem errada.

## ⚙️ Configurações

### Preferências de Download
- **Local de Download**: Onde os arquivos serão salvos
- **Limite de Velocidade**: Defina limites de velocidade de download/upload
- **Conexões Simultâneas**: Número de conexões por download
- **Iniciar com o Windows**: Habilite para iniciar automaticamente

### Aparência
- **Tema**: Escolha entre claro, escuro ou seguir configuração do sistema
- **Densidade**: Ajuste o espaçamento dos itens
- **Fonte**: Tamanho e família da fonte

### Notificações
- **Conclusão de Download**: Receba notificações quando um download for concluído
- **Erros**: Seja notificado sobre problemas nos downloads
- **Atualizações**: Receba avisos sobre novas versões

## 🔍 Dicas e Truques

### Atalhos de Teclado
- `Ctrl+R`: Recarregar a página
- `F5`: Atualizar lista de downloads

### Download em Lote
1. Na lista de itens, marque as caixas de seleção dos itens desejados
2. Clique em **Baixar Selecionados**
3. Ajuste as configurações conforme necessário
4. Confirme para iniciar todos os downloads

### Pausa Inteligente
O Furious App pode pausar downloads automaticamente quando você estiver usando a internet para outras atividades. Ative em **Configurações** > **Rede** > **Pausa Inteligente**.

## ❓ Solução de Problemas

### Downloads Lentos
1. Verifique sua conexão com a internet
2. Tente reduzir o número de conexões simultâneas
3. Verifique se há limitações no servidor de origem

### Erros Comuns
- **Conexão Recusada**: Verifique se o serviço está em execução
- **Sem Espaço em Disco**: Libere espaço ou altere o diretório de destino
- **Erro de Permissão**: Execute o aplicativo como administrador

### Obtendo Ajuda
- **Documentação**: Consulte os arquivos `.md` na pasta `docs/` do projeto
- **Fontes**: Exemplos e fontes populares podem ser encontradas na comunidade

## 🔄 Atualizações

O Furious App é distribuído via instalador. Para atualizar, execute o instalador da versão mais recente.

## 🤝 Suporte

### Canais de Atendimento
- Consulte a documentação do projeto e os logs locais.

### Horário de Atendimento
- Segunda a Sexta: 9h às 18h (GMT-3)
- Sábados: 9h às 13h
- Domingos e feriados: Plantão para emergências

## 🔒 Privacidade

A aplicação é **local-first**. Dados e configurações ficam no computador do usuário.

---

📅 **Última Atualização**: 27/12/2025 (v2.7.0)

© 2025 Furious App. Todos os direitos reservados.
