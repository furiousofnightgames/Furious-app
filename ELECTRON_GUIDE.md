# 📖 Guia Completo - Furious App Desktop

## Visão Geral

O Furious App foi transformado em uma aplicação **Desktop** completa com:

### Tecnologias Principais
- **Electron 27** - Framework desktop multiplataforma
- **Python 3.10.5** - Backend robusto com FastAPI
- **Vue.js 3 + Vite** - Frontend reativo de alta performance

### 🆕 Destaques v3.1.0
- **Biblioteca Global Premium**: Gestão unificada de itens.
- **Pré-flight Checks**: Validação de links e magnets antes do download.
- **Engine de Download Ultra-Robusto**: Fallback automático, headers de navegador, tratamento de erro aprimorado.
- **Steam Integration 2.0**: Nova página de detalhes com vídeos e requirements.
- **Favoritos Premium**: Sistema reformulado com ícones automáticos e resolução de imagens.
- **Análise Inteligente**: Sugestão automática de fontes com melhor saúde.ativo
- **TailwindCSS** - Estilização com design responsivo
- **SQLite** - Banco de dados integrado

### Arquitetura Técnica

### Backend (Python/FastAPI)
- **API RESTful** com documentação automática (Swagger/OpenAPI)
- **WebSockets** para atualizações em tempo real
- **SQLAlchemy** para ORM e gerenciamento do banco de dados
- **Aria2** para gerenciamento de downloads
- **Steam API** para integração com a plataforma Steam
- **Sistema de Cache** multi-camada para melhor desempenho
- **Validação de Dados** com Pydantic
- Aplicação local-first (localhost), sem autenticação por padrão
- **Logging** abrangente para diagnóstico de problemas

### Frontend (Vue.js/Electron)
- **Vue 3** com Composition API
- **Pinia** para gerenciamento de estado
- **TailwindCSS** para estilização
- **WebSockets** para atualizações em tempo real
- Tema escuro (Tailwind)
- **Componentes** reutilizáveis e acessíveis
- **Lazy loading** de rotas

### Sistema de Cache Inteligente
- **Memória** para dados frequentes
- **Disco** para persistência
- **HTTP Cache** para recursos estáticos
- **Invalidation** baseada em tempo e eventos
- **Compressão** para otimização

### Segurança
- Aplicação local-first (localhost)
- **CORS** configurado para ambiente local
- **Sanitização** básica de entradas
- Isolamento de processos no Electron (sandbox + contextIsolation)

### Funcionalidades Implementadas
- **Interface Desktop Nativa** - Janelas, menus e notificações do sistema
- **Gerenciador de Downloads** - Suporte a HTTP, HTTPS, magnet links e torrents
- **Sistema de Fontes** - Importação/exportação de fontes JSON
- **Interface Web Moderna** - Dashboard com métricas em tempo real
- **Instalador para Windows** - Fácil instalação e desinstalação

## 📁 Estrutura do Projeto

```
aplicacao-pessoal-json/
├── 📁 backend/                   # Backend Python (FastAPI)
│   ├── main.py                 # Ponto de entrada da API
│   ├── database/               # Modelos e migrações do banco de dados
│   ├── routes/                 # Rotas da API
│   └── services/               # Lógica de negócio
│
├── 📁 docs/                     # Documentação do projeto
│   ├── api/endpoints.md
│   ├── architecture/overview.md
│   ├── deployment/production.md
│   ├── development/setup.md
│   └── usage/user-guide.md
│
├── 📁 engine/                   # Motor de downloads
│   ├── downloader.py           # Lógica principal de download
│   ├── aria2_controller.py     # Controle do cliente aria2
│   ├── torrent_handler.py      # Gerenciamento de torrents
│   └── utils/                  # Utilitários diversos
│
├── 📁 frontend/                 # Frontend Vue.js
│   ├── public/                 # Arquivos estáticos
│   └── src/
│       ├── assets/             # Imagens, fontes, estilos
│       ├── components/         # Componentes Vue reutilizáveis
│       ├── router/             # Configuração de rotas
│       ├── services/           # Serviços (API, autenticação)
│       └── views/              # Páginas da aplicação
│
├── 📁 launcher/                 # Launcher personalizado
│   ├── furious_app_desktop.py  # Tela de inicialização
│   └── images/                 # Ícones e imagens
│
├── 📁 node_modules/             # Dependências do Node.js
├── 📁 portables/                # Dependências portáteis
│   ├── python-64bits/          # Python portátil
│   ├── node-v18.16.1-win-x64/  # Node.js portátil
│   └── aria2-1.37.0/           # aria2 portátil
│
├── 📄 .gitignore                # Arquivos ignorados pelo Git
├── 📄 COMECE_AQUI_ELECTRON.md   # Guia rápido de início
├── 📄 ELECTRON_GUIDE.md         # Este arquivo
├── 📄 README.md                 # Documentação principal
├── 📄 SETUP_ELECTRON.md         # Guia de configuração
├── 📄 aria2.session             # Sessão do aria2
├── 📄 backend.log               # Logs do backend
├── 📄 build-electron.ps1        # Script de build do Electron
├── 📄 compilar-instalador.ps1   # Script para criar instalador
├── 📄 compilar-launcher.ps1     # Script para compilar o launcher
├── 📄 data.db                   # Banco de dados SQLite
├── 📄 dht.dat                   # Dados DHT para torrents
├── 📄 electron-builder.yml      # Configuração do electron-builder
├── 📄 electron-main.js          # Ponto de entrada do Electron
├── 📄 electron-preload.js       # Script de preload
├── 📄 fontes-LINKS.txt          # Fontes de download
├── 📄 nsis-installer.nsi        # Script NSIS para o instalador
├── 📄 nsis-installer-electron.nsi # Script NSIS para o instalador Electron
├── 📄 package.json              # Configuração do projeto
├── 📄 requirements.txt          # Dependências Python
├── 📄 run.py                    # Script de inicialização
└── 📄 splash.html               # Tela de carregamento
```
```

## 🚀 Guia de Desenvolvimento

### Pré-requisitos

- Node.js 18.16.1 ou superior
- Python 3.10.5 ou superior
- Git (opcional)
- Yarn ou npm (recomendado o Yarn)

### Configuração do Ambiente

1. **Clonar o repositório**
   ```bash
   git clone [URL_DO_REPOSITORIO]
   cd aplicacao-json-versoes
   ```

2. **Instalar dependências do backend**
   ```bash
   pip install -r requirements.txt
   ```

3. **Instalar dependências do frontend**
   ```bash
   cd frontend
   npm install # ou yarn install
   cd ..
   ```

### Executando em Desenvolvimento

```bash
# Iniciar em modo desenvolvimento
npm run dev
```

Isso irá:
- Iniciar o servidor de desenvolvimento do frontend (Vite)
- Iniciar o servidor Python (FastAPI)
- Abrir a janela do Electron com a aplicação

### Criando um Build de Produção

1. **Construir o frontend**
   ```bash
   npm run build:frontend
   ```

2. **Criar instalador**
   ```bash
   npm run build:installer
   ```

O instalador será gerado na pasta `dist/`.

## 🛠️ Solução de Problemas Comuns

### Problemas de Compilação
- **Erro de dependências faltando**: Execute `npm install` e `pip install -r requirements.txt`
- **Erros de permissão**: Execute o terminal como administrador
- **Problemas com o Python**: Verifique se o Python 3.10.5 está instalado e no PATH

### Problemas de Execução
- **Aplicação não inicia**: Verifique os logs no console
- **Erros de API**: Certifique-se de que o backend está rodando na porta 8000
- **Problemas de interface**: Limpe o cache do navegador (Ctrl+F5)

## 📦 Distribuição

### Criando um Instalador

1. Atualize a versão no `package.json`
2. Execute `npm run build:installer`
3. O instalador será gerado em `dist/Furious App Setup X.Y.Z.exe`

### Atualizando a Aplicação

1. Crie uma nova tag de versão
2. Atualize o `CHANGELOG.md`
3. Gere um novo instalador
4. Atualize a documentação

## 🤝 Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Faça commit das suas alterações (`git commit -m 'Adiciona nova feature'`)
4. Faça push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 🔍 Recursos Detalhados

### Integração com Steam

#### Busca de Jogos
- Busca automática na biblioteca Steam
- Suporte a múltiplos perfis de usuário
- Cache local de metadados

#### Metadados Ricos
- Capas de jogos em alta resolução
- Banners e imagens de fundo
- Descrições detalhadas
- Vídeos de gameplay
- Avaliações da comunidade

#### SteamGridDB
- Upload automático de imagens
- Download de capas personalizadas
- Gerenciamento de coleções

### Sistema de Downloads

#### Gerenciamento de Filas
- Filas múltiplas
- Priorização de downloads
- Agendamento automático
- Limites de velocidade

#### Protocolos Suportados
- HTTP/HTTPS
- Magnet Links
- Torrents
- Metalinks
- FTP/FTPS

### Segurança

#### Autenticação
- Login com Steam
- Autenticação local
- Gerenciamento de sessões

#### Criptografia
- Dados em trânsito (TLS 1.3)
- Dados em repouso
- Chaves de criptografia gerenciadas

### Personalização

#### Temas
- Claro/Escuro
- Cores personalizáveis
- Ícones personalizáveis

#### Layout
- Modo compacto
- Modo detalhado
- Painéis redimensionáveis
- Atalhos personalizáveis

```powershell
# Desenvolvimento
.\build-electron.ps1 -Mode dev

# Apenas portable
.\build-electron.ps1 -Mode portable

# Apenas instalador
.\build-electron.ps1 -Mode installer

# Tudo (padrão)
.\build-electron.ps1
```

## 🔧 Como Funciona

### Arquitetura

```
┌─────────────────────────────────────────┐
│         Electron Window (Desktop)       │
│  ┌─────────────────────────────────┐   │
│  │   Frontend Vue.js (http://...)  │   │
│  │   - Dashboard                   │   │
│  │   - Downloads                   │   │
│  │   - Fontes JSON                 │   │
│  │   - Configurações               │   │
│  └─────────────────────────────────┘   │
└──────────────┬──────────────────────────┘
               │ HTTP/WebSocket
               ▼
┌─────────────────────────────────────────┐
│    Backend Python (localhost:8001)      │
│  ┌─────────────────────────────────┐   │
│  │   FastAPI + SQLModel            │   │
│  │   - API REST                    │   │
│  │   - WebSocket (real-time)       │   │
│  │   - SQLite Database             │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │   Engine (Download Manager)     │   │
│  │   - aria2 wrapper               │   │
│  │   - Job manager                 │   │
│  │   - Download controller         │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

### Fluxo de Inicialização

1. **Electron inicia** (`electron-main.js`)
2. **Python backend é iniciado** (processo filho)
3. **Aguarda backend estar pronto** (verifica porta 8000)
4. **Carrega frontend** (http://localhost:5173 em dev, file:// em prod)
5. **Frontend conecta ao backend** (API + WebSocket)
6. **Aplicação pronta para uso**

## 📦 Distribuição

### Para Usuários Finais

1. **Gere o instalador:**
   ```powershell
   npm run build:installer
   ```

2. **Distribua o arquivo:**
   ```
   Furious App Setup.exe
   ```

3. **Usuário executa:**
   - Clica em `Furious App Setup.exe`
   - Seleciona pasta de instalação
   - Clica em "Instalar"
   - Atalho criado no Desktop e Menu Iniciar

4. **Usuário usa:**
   - Clica em "Furious App" no Desktop
   - Aplicação abre em janela Electron
   - Backend inicia automaticamente
   - Interface carrega

### Para Testes Locais

```powershell
# Executar o portable diretamente
.\launcher\win-unpacked\Furious App.exe
```

## 🔍 Troubleshooting

### Problema: "Python não encontrado"

**Causa:** Falta de `portables/python-64bits/`

**Solução:**
```powershell
# Verifique se existe
Test-Path "portables/python-64bits/python.exe"

# Se não existir, copie do seu ambiente Python
# Ou use: python -c "import sys; print(sys.executable)"
```

### Problema: "Porta 8000 em uso"

**Causa:** Outra aplicação usando a porta

**Solução:**
```powershell
# No modo local (py run.py) usa 8000. No Electron usa 8001.
netstat -ano | findstr :8000

# Mate o processo (substitua PID)
taskkill /PID <PID> /F
```

### Problema: "Frontend não carrega"

**Causa:** `frontend/dist/` não foi gerado

**Solução:**
```powershell
cd frontend
npm run build
cd ..
npm run build:electron
```

### Problema: "Backend não inicia"

**Causa:** Dependências Python faltando

**Solução:**
```powershell
pip install -r requirements.txt
```

### Problema: "Aplicação lenta ao iniciar"

**Esperado:** Primeira inicialização leva 5-10 segundos (Python iniciando)

**Otimização:** Aumente timeout em `electron-main.js` se necessário

## 🎨 Customizações

### Mudar Nome da Aplicação

Edite `package.json`:
```json
{
  "name": "sua-app",
  "productName": "Seu Nome"
}
```

### Mudar Ícone

Substitua: `launcher/images/icone.ico`

Gere novo ícone em: https://icoconvert.com/

### Mudar Versão

Edite `package.json`:
```json
{
  "version": "1.0.1"
}
```

### Mudar Porta do Backend

Edite `electron-main.js`:
```javascript
const BACKEND_PORT = 8001; // Mude aqui
```

## 📊 Tamanhos

| Arquivo | Tamanho |
|---------|---------|
| Portable (.exe) | ~500MB |
| Instalador (.exe) | ~450MB (comprimido) |
| Instalado | ~1.2GB (descomprimido) |

## 🔐 Segurança

Implementado:
- ✅ Sandbox ativado
- ✅ Context isolation
- ✅ Node integration desativado
- ✅ Preload script com API limitada
- ✅ Sem acesso direto ao sistema de arquivos

## 📝 Scripts Disponíveis

```bash
npm run dev                  # Desenvolvimento com hot reload
npm run build:frontend       # Build apenas frontend
npm run build:electron       # Build portable
npm run build:installer      # Build com instalador NSIS
npm start                    # Executar Electron (produção)
```

## 🎯 Checklist de Deployment

- [ ] Testar em desenvolvimento: `npm run dev`
- [ ] Testar build portable: `npm run build:electron`
- [ ] Executar portable: `.\launcher\win-unpacked\Furious App.exe`
- [ ] Testar build instalador: `npm run build:installer`
- [ ] Executar instalador em máquina limpa
- [ ] Testar desinstalação
- [ ] Verificar atalhos no Desktop
- [ ] Verificar Menu Iniciar
- [ ] Testar downloads
- [ ] Testar WebSocket (real-time updates)

## 🚀 Próximos Passos

1. **Instalar dependências:**
   ```powershell
   npm install && cd frontend && npm install && cd ..
   ```

2. **Testar desenvolvimento:**
   ```powershell
   npm run dev
   ```

3. **Gerar instalador:**
   ```powershell
   npm run build:installer
   ```

4. **Distribuir:**
   - Envie `launcher/Furious App Setup.exe` aos usuários
   - Ou hospede em servidor

## 📞 Suporte

Para problemas:
1. Verifique console do Electron (F12)
2. Verifique logs do Python
3. Verifique porta 8000
4. Reconstrua frontend: `cd frontend && npm run build`
5. Limpe cache: `rm -r node_modules && npm install`

---

**Versão:** 3.1  
**Data:** Janeiro 2026  
**Status:** ✅ Pronto para Produção
