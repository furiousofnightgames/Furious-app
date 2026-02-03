 # 🚀 Furious App - Acelerador de Downloads Profissional v3.3.1

<div align="center">
  <img src="launcher/images/icone.png" alt="Furious App Logo" width="160" height="160" style="border-radius: 50%;">

  [**🌐 BAIXAR AGORA (Landing Page)**](https://furiousofnightgames.github.io/Furiousapp/)
</div>

Sistema completo de gerenciamento de downloads com interface web moderna. Suporta URLs diretas, magnets, torrents e JSON com fontes customizadas.

**Versão 3.3 estável disponível!** - Com suporte completo a Windows e interface otimizada.

## 🆕 Novidades na Versão 3.3.1
- ✅ **Repacks e Placeholders**: Detecção automática de jogos Repack e arquivos "Placeholder" para evitar erros de espaço em disco.
- ✅ **Segurança Aprimorada**: Verificação SSL opcional por fonte e proteção contra deleção acidental.
- ✅ **Interface Refinada**: Novos modais com design premium, animações e feedback visual melhorado.
- ✅ **Gerenciamento de Cache**: Melhorias na limpeza automática e persistência de dados.

## 🌟 Destaques da Versão 3.3.1
- ✅ **Biblioteca Global Unificada**: Nova interface "Biblioteca" que agrega todos os itens de todas as fontes JSON. Inclui busca rápida, paginação otimizada, agrupamento inteligente de versões e cache de imagens.
- ✅ **Pré-flight Check (Sondagem)**: Analisador pré-download que verifica saúde do link, disponibilidade do aria2, status HTTP e conta seeds/peers reais (UDP) antes de iniciar o download.
- ✅ **Engine de Download Ultra-Robusto**: Sistema aprimorado com fallback automático e headers de navegador
  - Headers browser-like (User-Agent, Accept) para evitar bloqueios de servidores restritivos
  - Fallback inteligente: se download segmentado falhar, tenta automaticamente download serial
  - Tratamento de erro aprimorado: downloads falhados são marcados corretamente como "failed"
- ✅ **Detalhes de Itens Premium**: Página de detalhes totalmente refeita com carrosseis de vídeos/screenshots, requisitos de sistema detalhados (mín/rec), suporte a idiomas e descrições ricas.
- ✅ **Seleção de Versões**: Para jogos com múltiplos uploads, escolha qual versão baixar (botão "Escolher versão").
- ✅ **Data de Upload**: Visualização clara da data de upload dos itens (`uploadDate`) para identificar novidades.
- ✅ **Análise Inteligente de Fontes (Pré-Job)**: Intercepta o download para sugerir fontes com mais seeds/saúde.
- ✅ **Estabilidade Steam API**: Novo sistema de fila (Semáforo) para evitar erros 503.
- ✅ Nova tela de inicialização holográfica com tema cyberpunk.
- ✅ Melhorias de estabilidade e performance.
- ✅ IDs de itens estáveis (favoritos continuam marcados após reiniciar servidor).

---

## ✨ Recursos Principais

### 📦 Portabilidade Total
- ✅ **Instalador automático** (.EXE com um clique)
- ✅ **100% independente**: Python e Node.js portáteis + aria2 inclusos (sem depender de instalações no sistema)
- ✅ **Sem dependências externas**: Funciona offline após instalação (exceto downloads)
- ✅ **Desinstalação segura**: Remove apenas a aplicação, preserva downloads

## 🎮 Integração com Steam

### 🎯 Busca Automática
- 🔍 **Biblioteca Steam**: Busca automática de jogos instalados
- 👥 **Perfil local**: cache local de AppList/metadata para resolver imagens
- 📦 **Metadados Ricos**: Capas, banners, descrições e vídeos

### 🖼️ SteamGridDB
- 🖼️ **Capas Personalizadas**: Download automático de capas de alta qualidade
- 🏷️ **Organização**: Tags e categorias personalizáveis
- 🌍 **Interface PT-BR**: foco em experiência local

## ⚡ Recursos Avançados

### 📚 Biblioteca Global
- 🔍 **Busca Unificada**: Pesquise em todas as fontes JSON simultaneamente.
- 📦 **Agrupamento Inteligente**: Itens repetidos ou versões diferentes do mesmo jogo são agrupados em um único card.
- ⚡ **Performance**: Paginação virtual e cache agressivo de imagens para navegação fluida.
- 🛠️ **Gestão de Cache**: Controles para limpar/recarregar metadados e imagens.

### 🛡️ Pré-flight Check & Segurança
- 🛑 **Validação Prévia**: Verifica se o link (HTTP/Magnet) está acessível antes de criar o job.
- 📡 **Sondagem de Trackers**: (Magnets) Conecta via UDP para descobrir seeders/leechers reais, sem depender da API da fonte.
- 🏥 **Health Check**: Exibe visualmente se o torrent está "Saudável" ou "Crítico".

### 🔄 WebSockets
- Atualizações em tempo real de progresso de downloads
- Notificações instantâneas
- Reconexão automática (quando aplicável)

### 💾 Cache Inteligente
- Armazenamento em memória para dados frequentes
- Cache em disco para persistência
- Invalidação automática

Observação:
- O cache grande (ex.: `Cache/Cache_Data`) é do Electron/Chromium e fica em `%LOCALAPPDATA%\furious-app\Cache`.

## ♿ Acessibilidade

### 🎨 Interface
- Temas claro/escuro (Cyberpunk)
- Alto contraste para melhor legibilidade
- Tamanho de fonte ajustável

### ⌨️ Navegação
- Navegação completa por teclado
- Atalhos personalizáveis
- Foco visível em elementos interativos

## 📁 Estrutura do Projeto

```
📦 aplicacao-pessoal-json
├── 📁 backend/             # API FastAPI
├── 📁 docs/               # Documentação (opcional)
│   ├── 📁 features/      # Documentação de features (Global Library, Pre-flight)
├── 📁 engine/             # Motor de downloads
├── 📁 frontend/           # Aplicação Vue.js
├── 📁 launcher/           # Tela de inicialização
├── 📁 node_modules/       # Dependências Node.js (Raiz)
├── 📁 portables/          # Dependências portáteis
│   ├── python-64bits/            # Python 3.10.5
│   ├── node-v18.16.1-win-x64/    # Node.js Portátil
│   └── aria2-1.37.0/             # Aria2c
├── 📄 .gitignore
├── 📄 COMECE_AQUI_ELECTRON.md
├── 📄 ELECTRON_GUIDE.md
├── 📄 README.md
├── 📄 SETUP_ELECTRON.md
├── 📄 aria2.session       # Sessão do aria2
├── 📄 backend.log         # Logs do backend
├── 📄 build-electron.ps1  # Script de build
├── 📄 compilar-*.ps1      # Scripts de compilação
├── 📄 electron-*.js       # Configurações do Electron
├── 📄 nsis-*.nsi         # Scripts do instalador
├── 📄 package.json        # Configuração do projeto
├── 📄 requirements.txt    # Dependências Python
└── 📄 run.py             # Ponto de entrada (Python Puro)
```

### 📥 Downloads Avançados
- ✅ **URLs diretas** com suporte a resumo (range requests)
- ✅ **Magnet links e torrents** via aria2
- ✅ **Downloads segmentados** (paralelo com múltiplas conexões)
- ✅ **Fila automática** (downloads sequenciais)
- ✅ **Controle completo**: Pause, Resume, Cancel
- ✅ **Monitoramento real-time**: Peers, seeders, velocidade

### 🎨 Interface Web
- ✅ **Design cyberpunk profissional** com TailwindCSS
- ✅ **Detalhes Imersivos**: Página de item com carrosseis (vídeos/prints), badges de idiomas e requisitos de sistema.
- ✅ **Dashboard** com estatísticas animadas
- ✅ **Responsivo** (funciona em desktop, tablet, mobile)
- ✅ **Notificações** para eventos (criação, conclusão, erro)
- ✅ **Menu intuitivo** e fácil de navegar

### 📊 Gerenciamento
- ✅ **Fontes JSON** customizadas
- ✅ **Histórico completo** de downloads
- ✅ **Filtros por status** (rodando, pausado, concluído, erro)
- ✅ **Banco de dados** SQLite para persistência

### 🎮 Integração com Steam
- 🔍 **Busca automática** de jogos na biblioteca Steam
- 🖼️ **Metadados ricos**: Capas, banners, descrições e vídeos
- 🏷️ **Tags e categorias** automáticas
- 🌐 **Suporte a múltiplos idiomas**
- 🖼️ **SteamGridDB**: Fallback para imagens de jogos

### ⚡ Recursos Avançados
- 🌐 **WebSockets** para atualizações em tempo real
- 🛡️ **Segurança**: Validação de entrada e HTTPS
- 💾 **Cache inteligente** para reduzir tráfego
- 🔄 **Sincronização automática** entre sessões
- ⚙️ **API RESTful** para integração com outros sistemas

### ♿ Acessibilidade
- ⌨️ **Navegação por teclado** completa
- 📱 **Design responsivo** para todos os dispositivos
- 🔍 **Alto contraste** para melhor legibilidade

---

## 🚀 Como Começar

### Windows - Instalador (.EXE)

1. **Baixe** o instalador mais recente (`Furious App Setup.exe`)
2. **Execute** o instalador com privilégios de administrador
3. **Siga** o assistente de instalação
4. **Inicie** o Furious App pelo menu Iniciar ou atalho na área de trabalho

### Desenvolvimento

```bash
# 1. Clonar o repositório
git clone [URL_DO_REPOSITORIO]
cd Furious-app

# 2. Instalar dependências do backend
pip install -r requirements.txt

> [!IMPORTANT]
> **Configuração da API Key**: Para que as capas e imagens dos jogos funcionem, você deve obter sua chave em [SteamGridDB API](https://www.steamgriddb.com/profile/api) e inseri-la no arquivo `backend/config.py` (variável `STEAMGRIDDB_API_KEY`).

# 3. Instalar dependências do frontend
cd frontend
npm install

# 4. Iniciar em modo desenvolvimento (Electron + Vite + Backend)
npm run dev
```

### Compilando para produção

```bash
# 1. Construir frontend
npm run build:frontend

# 2. Criar instalador
npm run build:installer

# O instalador é gerado em 'launcher/' (configuração atual)
```

---

## ⭐ Favoritos

**Novidade v3.1.0**: Sistema de favoritos completamente reformulado com visual premium inspirado no Hydra Launcher!

- **Gaveta lateral ampliada** (420px de largura) para melhor visualização
- **Ícones de jogos automáticos**: Cada favorito exibe a capa/ícone do jogo (56x40px)
  - Resolução automática de imagens via Steam/SteamGridDB ao abrir a gaveta
  - Imagens persistidas no banco de dados para carregamento instantâneo
- **Limpeza inteligente de nomes**: Remove automaticamente versões, DLCs, repacks, builds, etc.
  - Exemplo: "GTA V - Premium Edition v1.5 + DLC" → "GTA V"
- **Acesso rápido**: Botão ☰ no menu superior
  - Clique no item para ir direto aos detalhes
  - Botão `X` remove o favorito instantaneamente
- **Persistência robusta**: `item_id` determinístico por URL - favoritos mantidos após reiniciar

## 🛠️ Requisitos do Sistema

- Windows 10/11 (64-bit)
- 4GB RAM (8GB recomendado)
- 2GB de espaço livre em disco
- Conexão com a internet (apenas para downloads)

## 🔧 Solução de Problemas

### Erro de Codificação
Se encontrar erros de codificação de caracteres, certifique-se de que:
- O sistema está configurado para usar UTF-8
- Os arquivos de configuração estão salvos em UTF-8 sem BOM

### Problemas de Instalação
- Execute o instalador como administrador
- Verifique se há versões antigas do aplicativo e desinstale-as primeiro
- Verifique se o Windows Defender não está bloqueando a instalação

### Problemas de Rede
- Verifique se as portas 8000 (py run.py) / 8001 (Electron) e 5173 (frontend em desenvolvimento) estão liberadas
- Certifique-se de que o firewall não está bloqueando o aplicativo

### Teste limpo (banco zerado)
Se você quer testar sem dados antigos (favoritos/jobs/etc), rode com um DB temporário:

```powershell
$env:DB_PATH = "$env:TEMP\furious-test.db"
py run.py
```

## 🤝 Como Contribuir

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Faça commit das suas alterações (`git commit -m 'Adiciona nova feature'`)
4. Faça push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## ✉️ Contato

Para suporte ou dúvidas, entre em contato:
- Email: furiousofnightgames@gmail.com
- Issues do GitHub: [URL do repositório]/issues
- Leia a documentação existente em [COMECE_AQUI_ELECTRON.md](COMECE_AQUI_ELECTRON.md), [SETUP_ELECTRON.md](SETUP_ELECTRON.md) e [ELECTRON_GUIDE.md](ELECTRON_GUIDE.md) para obter ajuda.
- O cache do aplicativo está localizado em `%LOCALAPPDATA%\furious-app\Cache`.

## 📚 Documentação Adicional
- 📖 [COMECE_AQUI_ELECTRON.md](COMECE_AQUI_ELECTRON.md) - Início rápido (Electron)
- 🔧 [SETUP_ELECTRON.md](SETUP_ELECTRON.md) - Setup do ambiente e build
- 📄 [ELECTRON_GUIDE.md](ELECTRON_GUIDE.md) - Documentação técnica do Electron

---

## 📖 Interface da Aplicação

### 🏠 Dashboard
- Estatísticas de downloads (total, rodando, pausado, concluído, erro)
- Gráficos animados
- Status geral do sistema

### 📥 Downloads
- Lista completa de downloads com status
- Controle (pause, resume, cancel)
- Detalhes (velocidade, peers, seeders)
- Exibição de itens em fila

### 🔗 Fontes JSON
- Carregue de URL ou cole JSON
- Visualize items disponíveis
- Selecione múltiplos itens
- Selecione versões específicas (se disponível)
- Configure pasta de destino

### ⚙️ Novo Download
- URL direta para arquivos
- Detecção automática de nome
- Configurações avançadas (k, n_conns, verificar SSL)

---

## 🛠️ Componentes Técnicos

### Backend (Python FastAPI)
```
backend/
├── main.py              # API Rest + WebSocket
├── db.py                # SQLite + migrations
├── config.py            # Configurações
└── models/
    └── models.py        # SQLModel schemas
```

### Engine (Download Manager)
```
engine/
├── manager.py           # JobManager - fila sequencial
├── download.py          # Downloader serial/segmentado
└── aria2_wrapper.py     # Interface com aria2
```

### Frontend (Vue.js 3)
```
frontend/
├── dist/                # Build final (servido pelo backend)
├── src/
│   ├── components/      # Vue components
│   ├── stores/          # Pinia (estado global)
│   ├── views/           # Páginas (Dashboard, Downloads, etc)
│   ├── services/        # Cliente HTTP
│   └── styles/          # TailwindCSS + cyberpunk theme
```

### Portables Inclusos
```
portables/
├── python-64bits/            # Python 3.10.5
├── node-v18.16.1-win-x64/    # Node.js LTS (para build/electron)
└── aria2-1.37.0/             # aria2 (download engine)
```

**Nota importante:** Python foi renomeado de `Portable-Python-3.10.5_x64` para `python-64bits` para evitar problemas de compilação NSIS com nomes muito longos.

---

## 📊 Status do Projeto

| Aspecto | Status |
|---------|--------|
| Backend API | ✅ Completo |
| Frontend UI | ✅ Completo |
| Downloads | ✅ Funcionando |
| Magnet/Torrent | ✅ Funcionando |
| Real-time Updates | ✅ WebSocket |
| Persistência | ✅ SQLite |
| Instalador NSIS | ✅ Pronto |
| Documentação | ✅ Completa |
| **Produção** | ✅ **PRONTO** |

---

## 🔧 Instalação do Desenvolvedor

### Pré-requisitos
- Python 3.9+
- Node.js 14+
- Git

### Setup

```bash
# 1. Clone ou extraia o projeto
cd Furious-app

# 2. Backend
pip install -r requirements.txt

# 3. Frontend
cd frontend
npm install
npm run build
cd ..

# 4. Execute
python run.py
```

Abra: http://localhost:8000

---

## 🎯 Compilar Instalador .EXE

### Pré-requisitos
- NSIS 3.08+ (https://nsis.sourceforge.io/)

### Compilação

```powershell
# Verifique se NSIS está instalado
Test-Path "C:\Program Files (x86)\NSIS\makensis.exe"

# Compile o instalador
.\compilar-instalador.ps1

# Resultado: launcher/Furious App Setup.exe
```

---

## 📁 Estrutura de Pastas

```
Furious-app/
├── portables/
│   ├── python-64bits/                (Python portátil)
│   ├── node-v18.16.1-win-x64/        (Node.js portátil)
│   └── aria2-1.37.0/                 (aria2 binário)
├── backend/                          (API Python/FastAPI)
├── engine/                           (Download manager)
├── frontend/                         (Vue.js app)
├── launcher/                         (Scripts de inicialização)
├── nsis-installer.nsi                (Config do instalador)
├── compilar-instalador.ps1           (Script de compilação)
└── README.md                         (Este arquivo)
```

---

## 🔌 API Endpoints

### Downloads
- `POST /api/jobs` - Criar download
- `GET /api/jobs` - Listar downloads
- `GET /api/jobs/{id}` - Detalhes
- `POST /api/jobs/{id}/pause` - Pausar
- `POST /api/jobs/{id}/resume` - Retomar
- `POST /api/jobs/{id}/cancel` - Cancelar
- `DELETE /api/jobs/{id}` - Deletar arquivo

### Fontes
- `POST /api/load-json` - Carregar de URL
- `POST /api/load-json/raw` - Carregar JSON direto
- `GET /api/sources` - Listar fontes
- `DELETE /api/sources/{id}` - Deletar fonte

### Sistema
- `WS /ws` - WebSocket (progresso real-time)
- `GET /api/aria2/status` - Status do aria2

### Favoritos
- `GET /api/favorites` - Listar favoritos
- `POST /api/favorites` - Criar/atualizar favorito
- `DELETE /api/favorites/by_item` - Remover favorito por `(source_id, item_id)`

### Documentação Interativa
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

---

## 🎨 Temas e Personalizações

### Cyberpunk Theme
- Cores: Cyan (#06b6d4), Pink (#ec4899), Purple (#8b5cf6)
- Animações: Pulsing, bouncing, glowing effects
- Ícones: SVG customizados com gradientes

### Customização
Edite: `frontend/src/styles/cyberpunk.css`

---

## 🚀 Performance

- **Backend**: FastAPI (async/await)
- **Frontend**: Vue 3 (composition API)
- **Downloads**: aria2 (motor profissional)
- **Banco**: SQLite (rápido e leve)
- **Tamanho do .EXE**: ~475MB (Python + Node inclusos)

---

## 🔐 Segurança e Privacidade

- ✅ **Offline first**: Funciona sem conexão (após instalação)
- ✅ **Sem rastreamento**: Nenhum dado enviado
- ✅ **Código aberto**: Audite conforme necessário
- ✅ **SSL/TLS**: Suporte a HTTPS para downloads

---

## 📝 Notas Importantes

### Pasta de Downloads
Por padrão: `C:\Users\[Seu Usuário]\Downloads`  
Pode ser customizada ao criar cada download

### aria2
- Baixado de: https://aria2.github.io/
- Versão incluída: 1.37.0
- Localização: `portables/aria2-1.37.0/`

### Banco de Dados
- Localização (dev / padrão): `%LOCALAPPDATA%\furious-app\data.db`
- Localização (Electron): `%APPDATA%\furious-app\data.db`
- Override: variável de ambiente `DB_PATH`
- Tipo: SQLite 3
- Backup recomendado antes de desinstalar

---

## ❓ Dúvidas Frequentes

**P: Preciso de Python/Node instalados?**  
R: Não! Tudo está incluído no .EXE.

**P: Funciona offline?**  
R: Sim, após instalação funciona 100% offline, necessario internet para downloads.

**P: Como atualizar?**  
R: Desinstale a versão antiga e instale a nova.

**P: Onde são salvos os downloads?**  
R: Você escolhe ao criar cada download.

**P: Posso usar em Mac/Linux?**  
R: Sim, execute via Python. O instalador .EXE é apenas Windows.

---

## 🎓 Tecnologias Utilizadas

**Backend**
- Python 3.10.5
- FastAPI
- SQLModel
- Uvicorn
- aria2

**Frontend**
- Vue 3
- Pinia (state management)
- TailwindCSS
- Vite
- Axios

**DevOps**
- NSIS (instalador)
- PowerShell (scripts)
- Batch (launcher)

---

## 📄 Licença e Créditos

Desenvolvido por FURIOUSOFNIGHTGAMES 

**Data de Lançamento**: Janeiro 2026
**Versão**: 3.3.1
**Status**: ✅ Produção

---

## 📞 Suporte

Para dúvidas ou problemas:
1. Consulte `COMECE_AQUI_ELECTRON.md`
2. Consulte `SETUP_ELECTRON.md`
3. Verifique os logs em `%APPDATA%\furious-app\logs\backend.log` (quando rodando via Electron)
4. Acesse http://localhost:8000/docs (py run.py) ou http://localhost:8001/docs (Electron) para API docs

---

**Aproveite o Furious App! 🚀**
