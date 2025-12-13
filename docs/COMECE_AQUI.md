# 🚀 Furious App - Guia de Início Rápido

## ✅ Pré-requisitos

### Para Desenvolvedores (quem vai compilar o instalador):
- **Node.js 18.16.1+**
- **Python 3.10.5+**
- **NSIS 3.08+** (para criar o instalador Windows)
- **Git** (recomendado para controle de versão)

### Para Usuários Finais:
- Windows 10/11 (64-bit)
- 4GB RAM (8GB recomendado)
- 2GB de espaço em disco

---

## 🛠️ Instalação para Desenvolvimento

### 1. Clonar o Repositório

```bash
git clone [URL_DO_REPOSITORIO]
cd aplicacao-json-versoes
```

### 2. Instalar Dependências

```bash
# Instalar dependências do backend
pip install -r requirements.txt

# Instalar dependências do frontend
cd frontend
npm install
cd ..
```

### 3. Iniciar em Modo Desenvolvimento

```bash
npm run dev
```

Isso irá iniciar:
- Frontend em http://localhost:5173
- Backend em http://localhost:8000
- Janela do Electron com a aplicação

---

## 📦 Compilando o Instalador

### 1. Instalar o NSIS (se ainda não tiver)

1. Acesse: https://nsis.sourceforge.io/
2. Baixe a versão mais recente
3. Execute o instalador
4. Use o caminho padrão: `C:\Program Files (x86)\NSIS`

### 2. Compilar o Projeto

```bash
# Construir frontend
npm run build:frontend

# Criar instalador
npm run build:installer
```

### 3. Encontrar o Instalador

O instalador estará em `dist/Furious App Setup X.Y.Z.exe`

---

## 🚀 Instalação para Usuários Finais

1. Execute `Furious App Setup X.Y.Z.exe`
2. Siga o assistente de instalação
3. Acesse pelo Menu Iniciar ou atalho na área de trabalho

---

## 📚 Documentação Adicional

| Documento | Descrição |
|-----------|-----------|
| [Guia do Desenvolvedor](ELECTRON_GUIDE.md) | Documentação técnica detalhada |
| [Configuração](SETUP_ELECTRON.md) | Guia de configuração do ambiente |
| [Compilação](COMPILAR_INSTALADOR.md) | Instruções detalhadas de build |
| [Pós-Instalação](POS_INSTALACAO.md) | Guia do usuário final |
| [Troubleshooting](LAUNCHER_CONFIGURACAO.md) | Solução de problemas comuns |

## 🤝 Suporte

Para suporte, por favor:
1. Verifique a [documentação](docs/)
2. Consulte as [issues abertas](https://github.com/seu-usuario/seu-repositorio/issues)
3. Se não encontrar uma solução, abra uma nova issue

---

Desenvolvido com ❤️ pela Equipe Furious App

```powershell
# Abra PowerShell e execute:
.\compilar-instalador.ps1
```

**O que acontece:**
- ✅ Valida Python, Node, aria2, arquivos
- ✅ Copia Python (python-64bits)
- ✅ Compila com NSIS
- ✅ Cria: **FuriousAppInstaller.exe** (418 MB)
- ✅ Abre a pasta automaticamente

---

### 🎯 Opção SIMPLES (Batch)

```cmd
# Abra CMD e execute:
compilar-instalador.bat
```

---

## 📦 O que o Instalador Contém

✅ **Python 3.10.5** (renomeado: python-64bits)  
✅ **Node.js 18.16.1**  
✅ **aria2 1.37.0** (download de torrents/magnets)  
✅ **FastAPI Backend** (API REST + WebSocket)  
✅ **Vue.js 3 Frontend** (interface moderna)  
✅ **Furious App.exe** (Desktop native com PyQt5)  

**Tamanho:** 418.57 MB

---

## 🎯 Resultado: `FuriousAppInstaller.exe`

Após compilar, você terá:

```
FuriousAppInstaller.exe (418.57 MB)
```

### Distribuir para Usuários:

```
1. Envie: FuriousAppInstaller.exe
2. Usuário executa o instalador
3. Seleciona pasta (ex: C:\Program Files\FuriousApp)
4. Clica "Instalar"
5. Cria atalho no Desktop: "Furious App"
6. Usuário clica no atalho
7. Interface abre em janela desktop nativa
```

---

## 🚀 Próximos Passos

### Para Desenvolvedores:

1. **Modificar a aplicação:**
   - Backend: Edite `backend/main.py`
   - Frontend: Edite `frontend/src/`

2. **Recompilar:**
   - Frontend: `cd frontend && npm run build`
   - Instalador: `.\compilar-instalador.ps1`

3. **Distribuir:**
   - Novo `FuriousAppInstaller.exe` está pronto!

---

## ❓ Perguntas Frequentes

**P: Preciso instalar Python?**  
R: NÃO! Tudo está incluído no instalador.

**P: Posso compilar em Mac/Linux?**  
R: NSIS é apenas Windows. Use WSL2 ou máquina virtual.

**P: Como desinstalar?**  
R: Painel de Controle → Programas → "Furious App" → Desinstalar

**P: Onde os downloads são salvos?**  
R: Usuário escolhe durante cada download. Padrão: `C:\Users\[User]\Downloads`

---

## 📞 Suporte

- Documentação: `docs/` (COMPILAR_INSTALADOR.md, EXECUTAVEL_README.md)
- Logs: `C:\Program Files\FuriousApp\INSTALACAO.txt`
- Código: `backend/`, `frontend/`, `engine/`
- ✅ Compila o instalador
- ✅ Mostra sucesso ou erro

---

### 🎯 Opção MANUAL (Linha de Comando)

```powershell
# Abra PowerShell e execute:
& "C:\Program Files (x86)\NSIS\makensis.exe" nsis-installer.nsi
```

---

## 3️⃣ Resultado

Você terá:

```
FuriousAppInstaller.exe    (tamanho: ~475 MB)
```

**Pronto para distribuir!** 🎉

---

## ⚡ QUICK START

```powershell
# 1. Abra PowerShell
Start-Process pwsh

# 2. Navegue até o projeto
cd 'C:\Users\diego\OneDrive\Documentos\aplicacao-json-versoes\aplicaçao-pessoal-json'

# 3. Execute a compilação
.\compilar-instalador.ps1

# 4. Aguarde ~1-2 minutos
# 5. Arquivo será criado: FuriousAppInstaller.exe
```

---

## 📋 Checklist Rápido

- [ ] NSIS instalado em `C:\Program Files (x86)\NSIS`
- [ ] PowerShell aberto como administrador (opcional mas recomendado)
- [ ] Na pasta raiz do projeto
- [ ] Pronto para executar `compilar-instalador.ps1`

---

## 🐛 Algo deu errado?

### Erro: "NSIS não encontrado"
→ Instale NSIS de: https://nsis.sourceforge.io/

### Erro: "Acesso negado"
→ Abra PowerShell como administrador:
```powershell
Start-Process pwsh -Verb RunAs
# Depois rode:
.\compilar-instalador.ps1
```

### Erro: "Frontend não encontrado"
→ Verrifique se `frontend\dist\index.html` existe
→ Se não, execute: `npm run build` na pasta frontend

### Erro: "Alguma pasta está faltando"
→ Veja `CHECKLIST_FINAL.md` para validar tudo

---

## ✅ Sucesso!

Quando a compilação terminar:

1. Uma janela se abre com a pasta do instalador
2. Você verá: `FuriousAppInstaller.exe`
3. Pode distribuir este arquivo
4. Usuários executam e instalam
5. Pronto! Aplicação funcionando

---

## 🎁 O Instalador Faz:

- ✅ Copia Python 3.10.5 portátil
- ✅ Copia Node 18.16.1 portátil
- ✅ Copia aria2
- ✅ Copia backend (FastAPI)
- ✅ Copia frontend (Vue)
- ✅ Cria atalho no Desktop
- ✅ Cria atalhos no Menu Iniciar
- ✅ Registra para desinstalar depois

**Tudo auto-contido. Zero dependências!**

---

## 📖 Mais Informações

| Arquivo | Descrição |
|---------|-----------|
| `RESUMO_EXECUCAO.md` | Visão geral do que foi feito |
| `COMPILAR_INSTALADOR.md` | Guia detalhado com troubleshooting |
| `EXECUTAVEL_README.md` | Documentação técnica completa |
| `CHECKLIST_FINAL.md` | Validação e testes |

---

## 🎯 Resumo

```
Instale NSIS
    ↓
Execute: .\compilar-instalador.ps1
    ↓
Aguarde 1-2 minutos
    ↓
FuriousAppInstaller.exe criado
    ↓
Distribua e pronto!
```

---

**Tudo pronto? Execute agora:**

```powershell
.\compilar-instalador.ps1
```

**Boa compilação! 🚀**
