# 🚀 Configuração do Ambiente - Furious App

Guia completo para configurar o ambiente de desenvolvimento e produção do Furious App.

## 📋 Pré-requisitos

### Desenvolvimento
- **Node.js 18.16.1+** (https://nodejs.org/)
- **Python 3.10.5+** (https://www.python.org/)
- **Git** (opcional, mas recomendado)
- **Yarn** (opcional, pode usar npm)

### Produção
- Windows 10/11 (64-bit)
- 4GB RAM (8GB recomendado)
- 2GB de espaço em disco

## 🔧 Configuração Inicial

### 1. Clonar o Repositório

```bash
git clone [URL_DO_REPOSITORIO]
cd aplicacao-json-versoes
```

### 2. Instalar Dependências do Backend

```bash
pip install -r requirements.txt
```

### 3. Instalar Dependências do Frontend

```bash
cd frontend
npm install  # ou yarn install
cd ..
```

### 4. Verificar Estrutura do Projeto

Certifique-se que a estrutura de diretórios está correta:

```
📦 aplicacao-pessoal-json
├── 📁 backend/             # API FastAPI
│   ├── main.py           # Ponto de entrada
│   ├── database/         # Modelos e migrações
│   ├── routes/           # Rotas da API
│   └── services/         # Lógica de negócio
│
├── 📁 docs/               # Documentação completa
├── 📁 engine/             # Motor de downloads
│   ├── downloader.py     # Lógica principal
│   ├── aria2_controller.py
│   └── torrent_handler.py
│
├── 📁 frontend/           # Aplicação Vue.js
│   ├── public/           # Arquivos estáticos
│   └── src/              # Código-fonte
│
├── 📁 launcher/           # Tela de inicialização
│   ├── furious_app_desktop.py
│   └── images/
│
├── 📁 portables/          # Dependências portáteis
│   ├── python-64bits/    # Python 3.10.5
│   ├── node-v18.16.1-win-x64/
│   └── aria2-1.37.0/
│
# Arquivos de configuração principais
├── 📄 .gitignore
├── 📄 electron-main.js
├── 📄 electron-preload.js
├── 📄 package.json
├── 📄 requirements.txt
└── 📄 run.py
```

**Arquivos de Build e Scripts:**
- `build-electron.ps1` - Script de build do Electron
- `compilar-instalador.ps1` - Gera o instalador Windows
- `compilar-launcher.ps1` - Compila o launcher personalizado
- `electron-builder.yml` - Configuração do electron-builder
- `nsis-*.nsi` - Scripts do instalador NSIS

**Arquivos de Dados:**
- `data.db` - Banco de dados SQLite
- `aria2.session` - Sessão do aria2
- `dht.dat` - Dados DHT para torrents
- `backend.log` - Logs da aplicação

## 🎮 Desenvolvimento

### Iniciando o Ambiente de Desenvolvimento

```bash
# Na raiz do projeto
npm run dev
```

Isso irá:
- Iniciar o servidor de desenvolvimento do frontend (Vite) em http://localhost:5173
- Iniciar o servidor Python (FastAPI) em http://localhost:8000
- Abrir a janela do Electron com a aplicação

### Estrutura de Desenvolvimento

- **Frontend**: Desenvolvido com Vue.js 3 e Vite
- **Backend**: API REST com FastAPI (Python 3.10+)
- **Banco de Dados**: SQLite (armazenado em `backend/database.sqlite`)
- **Estilização**: TailwindCSS + CSS personalizado

## 🏗️ Build e Compilação

### 1. Construir para Produção

```bash
# Construir frontend
npm run build:frontend

# Construir aplicação Electron
npm run build
```

### 2. Criar Instalador Windows

```bash
# Criar instalador NSIS
npm run build:installer
```

Arquivos gerados em `dist/`:
- `Furious App Setup X.Y.Z.exe` - Instalador para Windows
- `Furious App X.Y.Z.exe` - Versão portátil

## 🚀 Distribuição

### Requisitos do Sistema

- Windows 10/11 (64-bit)
- 4GB RAM (8GB recomendado)
- 2GB de espaço em disco

### Instalação

1. Execute o instalador `Furious App Setup X.Y.Z.exe`
2. Siga o assistente de instalação
3. A aplicação estará disponível no Menu Iniciar e na área de trabalho

### Atualização

1. Execute o novo instalador
2. A instalação anterior será atualizada automaticamente

## 🔧 Solução de Problemas

### Problemas Comuns

1. **Erro ao iniciar**
   - Verifique se todas as dependências foram instaladas corretamente
   - Verifique as permissões de arquivo
   - Consulte o arquivo de log em `%APPDATA%/furious-app/logs/`

2. **Problemas de Rede**
   - Verifique se as portas 8000 (backend) e 5173 (desenvolvimento) estão disponíveis
   - Desative temporariamente o firewall para testes

3. **Erros de Dependência**
   - Execute `npm install` e `pip install -r requirements.txt` novamente
   - Remova as pastas `node_modules` e `__pycache__` e reinstale as dependências

## 📚 Documentação Adicional

- [Guia do Desenvolvedor](ELECTRON_GUIDE.md) - Documentação técnica detalhada
- [Notas de Versão](CHANGELOG.md) - Histórico de alterações
- [Guia de Contribuição](.github/CONTRIBUTING.md) - Como contribuir para o projeto

## 📞 Suporte

Para suporte, abra uma issue no repositório do projeto ou entre em contato com a equipe de desenvolvimento.
### Modo Desenvolvimento (com Hot Reload)

```powershell
npm run dev
```

Isso inicia:
1. Frontend Vue.js em `http://localhost:5173`
2. Electron conectado ao frontend
3. Backend Python em `http://localhost:8000`

### Apenas Frontend

```powershell
cd frontend
npm run dev
```

### Apenas Backend

```powershell
python run.py
```

## 🏗️ Build e Empacotamento

### Build do Frontend

```powershell
cd frontend
npm run build
cd ..
```

Gera: `frontend/dist/` com arquivos otimizados

### Build Portable (.exe sem instalador)

```powershell
npm run build:electron
```

Resultado: `dist/Furious App.exe` (executável portátil)

### Build com Instalador NSIS (.exe installer)

```powershell
npm run build:installer
```

Resultado: 
- `dist/Furious App Setup 1.0.0.exe` - Instalador
- `dist/Furious App 1.0.0.exe` - Portable

## 📦 Estrutura de Saída

Após `npm run build:installer`, você terá:

```
dist/
├── Furious App Setup 1.0.0.exe    (Instalador com desinstalador)
├── Furious App 1.0.0.exe          (Executável portátil)
└── builder-effective-config.yaml  (Configuração usada)
```

## 🚀 Distribuição

### Para Usuários Finais

1. **Distribuir o instalador:**
   ```
   Furious App Setup 1.0.0.exe
   ```

2. **Usuário executa o instalador:**
   - Seleciona pasta de instalação (padrão: `C:\Program Files\Furious App`)
   - Clica em "Instalar"
   - Atalho criado no Desktop e Menu Iniciar

3. **Usuário clica em "Furious App":**
   - Aplicação abre em janela nativa Electron
   - Backend Python inicia automaticamente
   - Interface web carrega

### Para Testes Locais

```powershell
# Executar o portable diretamente
.\dist\Furious App 1.0.0.exe
```

## ⚙️ Configuração Avançada

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto para personalizar configurações:

```ini
# Backend
PORT=8000
DEBUG=true
LOG_LEVEL=info

# Frontend
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws

# Steam
STEAM_API_KEY=sua_chave_aqui
STEAMGRIDDB_KEY=sua_chave_aqui

# Downloads
MAX_CONCURRENT_DOWNLOADS=3
DOWNLOAD_SPEED_LIMIT=0  # 0 = ilimitado
MAX_RETRIES=3

# Cache
CACHE_TTL=3600  # 1 hora
MAX_CACHE_SIZE=1024  # MB
```

### Configuração do Aria2

O arquivo `aria2.conf` pode ser personalizado na pasta `portables/aria2-1.37.0/`:

```ini
# Limite de velocidade (0 = ilimitado)
max-overall-download-limit=0
max-overall-upload-limit=1M

# Conexões
max-concurrent-downloads=3
max-connection-per-server=16
split=16
min-split-size=1M

# Segurança
check-certificate=false
allow-overwrite=true
auto-file-renaming=false

# Logging
log-level=warn
log=aria2.log

# RPC
enable-rpc=true
rpc-listen-port=6800
rpc-allow-origin-all=true
rpc-listen-all=true
rpc-secret=seu_token_secreto
```

## 🔍 Solução de Problemas

### Diagnóstico Rápido

1. **Verificar serviços em execução**
   ```bash
   # Verificar processos do Electron
   tasklist | findstr electron
   
   # Verificar servidor Python
   netstat -ano | findstr :8000
   
   # Verificar Aria2
   tasklist | findstr aria2
   ```

2. **Logs importantes**
   - `backend.log` - Logs do servidor Python
   - `frontend/dist/error.log` - Erros do frontend
   - `%APPDATA%\Furious App\logs` - Logs da aplicação
   - `portables/aria2-1.37.0/aria2.log` - Logs do Aria2

### Problemas Comuns

#### 1. Erros de Inicialização
- **Sintoma**: Aplicação não inicia ou fecha imediatamente
- **Solução**:
  ```bash
  # Limpar cache do Electron
  rm -r %APPDATA%\Furious App\Cache
  
  # Reinstalar dependências
  npm ci
  pip install -r requirements.txt
  ```

#### 2. Downloads Parados
- **Sintoma**: Downloads não iniciam ou param no meio
- **Solução**:
  1. Verificar conexão com a internet
  2. Verificar espaço em disco
  3. Reiniciar o serviço Aria2:
     ```bash
     taskkill /f /im aria2c.exe
     start "" "portables/aria2-1.37.0/aria2c.exe" --conf-path=portables/aria2-1.37.0/aria2.conf
     ```

#### 3. Problemas de Interface
- **Sintoma**: Elementos da interface não carregam ou travam
- **Solução**:
  1. Limpar cache do navegador (Ctrl+Shift+Del)
  2. Reconstruir frontend:
     ```bash
     cd frontend
     npm run build
     cd ..
     ```

### Depuração Avançada

#### Habilitar Modo Desenvolvedor
1. Pressione `Ctrl+Shift+I` para abrir o DevTools
2. Navegue até "Console" para ver erros
3. Verifique a aba "Network" para requisições falhas

#### Logs Detalhados
Execute a aplicação em modo debug:
```bash
# Windows
set DEBUG=* & npm start

# Linux/macOS
DEBUG=* npm start
```

## 📊 Tamanho do Executável

- **Portable (.exe):** ~500MB (Python + Node.js + aria2 inclusos)
- **Instalador (.exe):** ~450MB (comprimido)

## 🔐 Segurança

- ✅ Sandbox ativado no Electron
- ✅ Context isolation habilitado
- ✅ Node integration desativado
- ✅ Sem acesso ao sistema de arquivos direto

## 📝 Próximos Passos

1. **Testar em desenvolvimento:**
   ```powershell
   npm run dev
   ```

2. **Testar build portable:**
   ```powershell
   npm run build:electron
   .\dist\Furious App 1.0.0.exe
   ```

3. **Gerar instalador final:**
   ```powershell
   npm run build:installer
   ```

4. **Distribuir:**
   - Envie `Furious App Setup 1.0.0.exe` aos usuários
   - Ou hospede em servidor de downloads

## 🎯 Checklist Final

- [ ] `npm install` executado com sucesso
- [ ] `npm run dev` funciona
- [ ] Frontend carrega em http://localhost:5173
- [ ] Backend responde em http://localhost:8000
- [ ] `npm run build:electron` gera .exe
- [ ] Executável portátil funciona
- [ ] `npm run build:installer` gera instalador
- [ ] Instalador funciona em máquina limpa

## 📞 Suporte

Para problemas:
1. Verifique os logs do console (F12 no Electron)
2. Verifique a porta 8000 (não deve estar em uso)
3. Reconstrua o frontend: `cd frontend && npm run build`
4. Limpe cache: `rm -r node_modules && npm install`

---

**Versão:** 1.0.0  
**Data:** Dezembro 2025  
**Status:** ✅ Pronto para Produção
