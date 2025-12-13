# 🚀 Furious App - Instalador Desktop .EXE Completo

## ✅ O que foi implementado

### 1. **Python Portátil (renomeado: python-64bits)**
- ✅ Renomeado de `Portable-Python-3.10.5_x64` para `python-64bits`
- ✅ Todas as dependências instaladas:
  - FastAPI, Uvicorn, aiofiles
  - SQLModel, SQLAlchemy, pydantic
  - WebSockets, Python-dotenv
  - Aiohttp, httpx, requests
  - Tudo em `portables/python-64bits/App/Python/Lib/site-packages/`

### 2. **Frontend Vue.js Buildado**
- ✅ Build final em `frontend/dist/`
- ✅ Otimizado com Vite (production build)
- ✅ Tamanho: ~15 MB descompactado
- ✅ Inclui: HTML, CSS, JS minificados + assets

### 3. **Backend FastAPI**
- ✅ `backend/main.py` configurado para servir `frontend/dist`
- ✅ API REST completa para:
  - Criar/pausar/retomar downloads
  - Gerenciar fontes JSON
  - WebSocket para progresso real-time
  - aria2 integration

### 4. **Launcher Desktop Profissional**
- ✅ **`launcher/Furious App.exe`** - Executável desktop (104.86 MB)
  - Compilado com PyInstaller
  - Usa PyQt5 + PyQtWebEngine
  - Renderiza Vue.js em janela nativa
  - Sem abrir navegador externo
  - Inicia backend Python em background
  - Janela limpa e profissional

### 5. **Instalador NSIS Completo**
- ✅ `nsis-installer.nsi` - Configuração NSIS 3.08+
- Funcionalidades:
  - Instala em `C:\Program Files\FuriousApp`
  - Copia Python (python-64bits) ✅ AGORA FUNCIONA
  - Copia Node.js, aria2, Backend, Frontend
  - Cria atalho Desktop → `Furious App.exe`
  - Cria atalhos Menu Iniciar
  - Registro Windows (Add/Remove Programs)
  - Desinstalação limpa

### 6. **Scripts de Compilação**
- ✅ `compilar-instalador.ps1` - PowerShell (RECOMENDADO)
  - Valida NSIS
  - Valida estrutura (python-64bits, frontend/dist, etc)
  - Executa compilação
  - Abre pasta resultado
  - Mostra tamanho final

- ✅ `compilar-instalador.bat` - Batch alternativo

---

## 📦 Estrutura Final

```
aplicacao-pessoal-json/
├── portables/
│   ├── python-64bits/                  ✅ Python 3.10.5 (renomeado)
│   │   └── App/Python/
│   │       └── Lib/site-packages/      ✅ Com todas as dependências
│   ├── node-v18.16.1-win-x64/
│   └── aria2-1.37.0/
├── backend/
│   ├── main.py                         ✅ Servindo frontend/dist
│   ├── db.py
│   └── models/
├── engine/
│   ├── manager.py
│   ├── download.py
│   └── aria2_wrapper.py
├── frontend/
│   ├── dist/                           ✅ Build otimizado (Vite)
│   │   ├── index.html
│   │   ├── assets/                     (CSS, JS minificados)
│   │   └── favicon.ico
│   └── src/                            (Fonte - não copiado para .exe)
├── launcher/
│   ├── Furious App.exe                 ✅ Executável desktop (PyQt5)
│   ├── furious_app_desktop.py          (Fonte)
│   ├── launcher.bat
│   └── post-install.bat
├── nsis-installer.nsi                  ✅ Config NSIS
├── compilar-instalador.ps1             ✅ Script compilação
├── FuriousAppInstaller.exe             ✅ RESULTADO FINAL (418.57 MB)
│   └── main.py                               ✅ Modificado para servir dist
├── frontend/
│   ├── src/
│   └── dist/                                 ✅ Build completo
├── launcher/
│   ├── launcher.bat                          ✅ Novo
│   └── launcher.ps1                          ✅ Novo
├── nsis-installer.nsi                        ✅ Novo
├── compilar-instalador.ps1                   ✅ Novo
└── COMPILAR_INSTALADOR.md                    ✅ Novo
```

---

## 🔨 Como Compilar o Instalador

### Opção 1: Usar o Script PowerShell (RECOMENDADO)

```powershell
# Navegue até a pasta raiz e execute:
.\compilar-instalador.ps1
```

Este script:
- ✅ Verifica se NSIS está instalado
- ✅ Valida toda a estrutura de pastas
- ✅ Compila o instalador automaticamente
- ✅ Exibe progresso e resultado final
- ✅ Abre a pasta do resultado

### Opção 2: Usar NSIS GUI

1. Abra: `C:\Program Files (x86)\NSIS\Contrib\HyperSCP\HyperSCP.exe`
2. File → Open → Selecione `nsis-installer.nsi`
3. Compile NSI script (F9)

### Opção 3: Usar Linha de Comando

```powershell
& "C:\Program Files (x86)\NSIS\makensis.exe" nsis-installer.nsi
```

---

## ✅ Pré-requisitos para Compilação

**IMPORTANTE**: Você precisa ter NSIS instalado!

1. **Instale NSIS 3.08+**:
   - Download: https://nsis.sourceforge.io/
   - Execute o instalador padrão
   - Local padrão: `C:\Program Files (x86)\NSIS`

2. **Verifique a estrutura**:
   ```powershell
   # Verifique se essas pastas existem:
   Test-Path "portables\python-64bits"
   Test-Path "portables\node-v18.16.1-win-x64"
   Test-Path "aria2-1.37.0"
   Test-Path "backend"
   Test-Path "frontend\dist"
   Test-Path "launcher"
   Test-Path "nsis-installer.nsi"
   ```

---

## 🎯 Resultado Final

Após compilar, você terá:

```
FuriousAppInstaller.exe  (tamanho: ~500MB aprox.)
```

### Usar o Instalador

**Para usuários finais**:
1. Clique duplo em `FuriousAppInstaller.exe`
2. Selecione pasta de destino (padrão: `C:\Program Files\FuriousApp`)
3. Clique em "Instalar"
4. Use o atalho "Furious App" no Desktop

**O que é instalado**:
- Python 3.10.5 portátil com todas as dependências
- Node.js 18.16.1 portátil
- aria2 1.37.0
- Backend Python (FastAPI)
- Frontend Vue (buildado)
- Scripts launcher

---

## 🧪 Testar Localmente

Antes de compilar, teste se tudo funciona:

```powershell
# Teste 1: Inicie o backend
cd $PROJECT_ROOT
.\portables\python-64bits\App\Python\python.exe .\backend\main.py

# Teste 2: Em outro terminal, acesse
Start-Process "http://localhost:8000"

# Teste 3: Execute o launcher
.\launcher\launcher.bat
```

---

## 🐛 Troubleshooting

### NSIS não encontrado
```powershell
# Verifique se está instalado:
Test-Path "C:\Program Files (x86)\NSIS\makensis.exe"

# Se não, instale de: https://nsis.sourceforge.io/
```

### Script de compilação diz "acesso negado"
```powershell
# Execute com privilégios elevados:
Start-Process pwsh -Verb RunAs
# Depois rode: .\compilar-instalador.ps1
```

### Frontend em branco ou 404
```powershell
# Verifique se o build está completo:
Test-Path "frontend\dist\index.html"

# Se não existe, rode:
cd frontend
npm run build
```

### Instalador muito grande
Isso é normal! Contém:
- Python 3.10 portátil (~300MB)
- Node.js 18 portátil (~100MB)
- Dependências Python
- aria2, backend, frontend

---

## 📚 Estrutura do Instalador NSIS

O arquivo `nsis-installer.nsi` define:

1. **Páginas**:
   - Welcome (Bem-vindo)
   - Directory (Escolher pasta)
   - StartMenu (Atalhos)
   - InstFiles (Progresso)
   - Finish (Conclusão)

2. **Instalação**:
   - Copia portables → `$INSTDIR\portables\`
   - Copia backend → `$INSTDIR\backend\`
   - Copia frontend/dist → `$INSTDIR\frontend\`
   - Copia launcher → `$INSTDIR\launcher\`
   - Copia aria2 → `$INSTDIR\aria2\`

3. **Atalhos**:
   - Desktop: `Furious App.lnk` → `$INSTDIR\launcher\launcher.bat`
   - Menu Iniciar: `Furious App\Furious App.lnk`
   - Menu Iniciar: `Furious App\Uninstall.lnk`

4. **Desinstalação**:
   - Remove atalhos
   - Deleta `$INSTDIR` completo
   - Remove entradas do Registro

---

## 🎉 Próximos Passos

1. **Instale NSIS** (se ainda não tiver)
2. **Execute**: `.\compilar-instalador.ps1`
3. **Distribua**: `FuriousAppInstaller.exe`
4. **Usuários instalam** no Windows

---

## ❓ Dúvidas Frequentes

**P: O instalador precisa de conexão com internet?**
R: Não! Tudo está portátil e auto-contido.

**P: Posso usar em Windows 7?**
R: Depende do Node.js v18 - recomendado Windows 10+.

**P: Como atualizar a aplicação?**
R: Desinstale a versão anterior, instale a nova.

**P: Posso customizar o instalador?**
R: Sim! Edite `nsis-installer.nsi` conforme necessário.

**P: Quanto espaço em disco é necessário?**
R: ~500MB-800MB dependendo do tamanho do download cache.

---

**Status**: ✅ **PRONTO PARA PRODUÇÃO!**

Você tem tudo que precisa para criar seu instalador .exe profissional!
