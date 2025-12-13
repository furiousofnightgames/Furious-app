# 🚀 Furious App - Guia de Início Rápido

Bem-vindo ao Furious App, um gerenciador de downloads avançado com suporte a URLs diretas, magnet links e torrents.

## ⚡ Início Rápido (5 minutos)

### 1️⃣ Pré-requisitos

- Node.js 18.16.1 ou superior
- Python 3.10.5 ou superior
- Git (opcional, apenas para desenvolvimento)

### 2️⃣ Instalar Dependências

```powershell
# Clonar o repositório (se ainda não tiver feito)
git clone [URL_DO_REPOSITORIO]
cd aplicacao-json-versoes

# Instalar dependências do backend
pip install -r requirements.txt

# Instalar dependências do frontend
cd frontend
npm install
cd ..
```

### 3️⃣ Executar em Modo Desenvolvimento

```powershell
# Na raiz do projeto
npm run dev
```

Isso irá iniciar:
- ✅ Frontend em http://localhost:5173
- ✅ Backend em http://localhost:8000
- ✅ Janela do Electron com a aplicação

### 4️⃣ Gerar Instalador .exe

Para criar um instalador do Windows:

```powershell
npm run build:installer
```

Resultado em `dist/`:
- `Furious App Setup 1.0.0.exe` - Instalador (para distribuir)
- `Furious App 1.0.0.exe` - Portable (executável direto)

## 📋 Arquivos Criados

| Arquivo | Descrição |
|---------|-----------|
| `electron-main.js` | Processo principal do Electron |
| `electron-preload.js` | Script de segurança |
| `electron-builder.yml` | Configuração do builder |
| `build-electron.ps1` | Script PowerShell para build |
| `SETUP_ELECTRON.md` | Guia detalhado de setup |
| `ELECTRON_GUIDE.md` | Documentação técnica completa |

## 🎯 Próximas Ações

### Opção 1: Testar Agora (Recomendado)

```powershell
npm install
cd frontend && npm install && cd ..
npm run dev
```

Testa se tudo funciona antes de gerar o instalador.

### Opção 2: Gerar Instalador Direto

```powershell
npm install
cd frontend && npm install && npm run build && cd ..
npm run build:installer
```

Gera o instalador em ~10 minutos.

### Opção 3: Usar Script PowerShell

```powershell
# Modo desenvolvimento
.\build-electron.ps1 -Mode dev

# Modo instalador
.\build-electron.ps1 -Mode installer

# Tudo (padrão)
.\build-electron.ps1
```

## ⚠️ Pré-requisitos

- ✅ **Node.js 14+** - https://nodejs.org/
- ✅ **Python 3.9+** - (já incluído nos portables)
- ✅ **Windows 10+** - (para executar .exe)

Verifique:
```powershell
node --version
npm --version
python --version
```

## 🔍 Troubleshooting Rápido

### "npm: comando não encontrado"
→ Instale Node.js: https://nodejs.org/

### "Porta 8000 em uso"
→ Feche outras aplicações ou mude a porta em `electron-main.js`

### "Python não encontrado"
→ Verifique `portables/python-64bits/python.exe` existe

### "Frontend não carrega"
→ Execute: `cd frontend && npm run build && cd ..`

## 📊 O que Você Tem Agora

```
✅ Aplicação Desktop (Electron)
✅ Backend Python (FastAPI) integrado
✅ Frontend Vue.js moderno
✅ Instalador profissional (.exe)
✅ Desinstalador automático
✅ Atalhos no Desktop e Menu Iniciar
✅ Sem dependências externas
✅ Funciona offline após instalação
```

## 🎬 Começar Agora

### Passo 1: Abra PowerShell

```powershell
# Navegue até a pasta do projeto
cd "c:\Users\diego\OneDrive\Documentos\aplicacao-json-versoes\aplicacao-pessoal-json"
```

### Passo 2: Instale Dependências

```powershell
npm install
cd frontend
npm install
cd ..
```

### Passo 3: Teste em Desenvolvimento

```powershell
npm run dev
```

### Passo 4: Gere o Instalador

```powershell
npm run build:installer
```

## 📦 Distribuição

Após gerar o instalador:

1. Encontre: `dist/Furious App Setup 1.0.0.exe`
2. Distribua aos usuários
3. Usuários executam e instalam
4. Atalho criado automaticamente

## 📚 Documentação

- **SETUP_ELECTRON.md** - Guia completo de setup
- **ELECTRON_GUIDE.md** - Documentação técnica detalhada
- **README.md** - Documentação original do projeto

## ✅ Checklist

- [ ] Node.js instalado (`node --version`)
- [ ] Dependências instaladas (`npm install`)
- [ ] Frontend compilado (`cd frontend && npm install && npm run build`)
- [ ] Desenvolvimento testado (`npm run dev`)
- [ ] Instalador gerado (`npm run build:installer`)
- [ ] Instalador testado em máquina limpa

## 🎉 Pronto!

Sua aplicação está pronta para ser distribuída como .exe!

**Próximo passo:** Execute `npm run dev` para testar

---

**Versão:** 1.0.0  
**Data:** Dezembro 2025  
**Status:** ✅ Pronto para Produção
