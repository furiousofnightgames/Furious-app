# 📦 Guia de Compilação do Instalador Furious App

## ⚡ Rápido (Recomendado)

Execute no PowerShell:
```powershell
.\compilar-instalador.ps1
```

Pronto! O instalador será criado automaticamente.

---

## Pré-requisitos Detalhados

Antes de compilar o instalador `.exe`, certifique-se de que você tem:

1. **NSIS instalado** - Download: https://nsis.sourceforge.io/
   - Versão 3.08 ou superior
   - Instale no caminho padrão: `C:\Program Files (x86)\NSIS`

2. **Estrutura de pasta completa**:
   ```
   /app-root
       /portables/
            /python-64bits/               ✅ Python 3.10.5 (renomeado)
            /node-v18.16.1-win-x64/       ✅ Node.js
            /aria2-1.37.0/                ✅ aria2
       /backend/                          ✅ FastAPI app
       /frontend/dist/                    ✅ Build Vue.js completo
       /launcher/                         ✅ Scripts de inicialização
            /Furious App.exe              ✅ Launcher desktop (PyQt5)
       nsis-installer.nsi                 ✅ Config NSIS
   ```

3. **Frontend buildado**:
   ```bash
   # Verifique se /frontend/dist/ existe e contém:
   # - index.html
   # - assets/ (CSS, JS)
   ```

## ✅ Checklist - Pré-compilação

- [ ] Python em `portables/python-64bits/` (renomeado corretamente)
- [ ] Frontend buildado em `/frontend/dist/`
- [ ] Launcher desktop criado: `/launcher/Furious App.exe`
- [ ] NSIS instalado em `C:\Program Files (x86)\NSIS`
- [ ] Arquivo `nsis-installer.nsi` na raiz do projeto

## 🔨 Compilar o Instalador

### ⚡ Método MAIS FÁCIL (PowerShell)

```powershell
# Na pasta raiz do projeto:
.\compilar-instalador.ps1
```

**Processo automático:**
1. ✅ Valida NSIS
2. ✅ Valida estrutura de pastas
3. ✅ Valida Python (python-64bits)
4. ✅ Executa compilação NSIS
5. ✅ Abre pasta com resultado
6. ✅ Mostra informações do instalador

**Resultado:**
```
FuriousAppInstaller.exe (418.57 MB)
```

---

### 🎯 Método Manual (Batch)

```cmd
compilar-instalador.bat
```

---

### 🔧 Método Avançado (NSIS direto)

```powershell
& "C:\Program Files (x86)\NSIS\makensis.exe" nsis-installer.nsi
```

2. Abra o arquivo `nsis-installer.nsi`:
   - File → Open → Navegue até seu projeto
   - Selecione `nsis-installer.nsi`

3. Compile:
   - Clique em **Compile NSI script** ou pressione `F9`
   - Aguarde a compilação terminar
   - O arquivo `FuriousAppInstaller.exe` será criado na raiz do projeto

### Opção 2: Usar PowerShell (Mais rápido)

```powershell
# Execute este comando na raiz do projeto
& "C:\Program Files (x86)\NSIS\makensis.exe" nsis-installer.nsi

# Ou faça com cd:
cd 'C:\Users\diego\OneDrive\Documentos\aplicacao-json-versoes\aplicaçao-pessoal-json'
& "C:\Program Files (x86)\NSIS\makensis.exe" nsis-installer.nsi
```

### Opção 3: Usar Linha de Comando (Mais automatizado)

```batch
cd C:\Users\diego\OneDrive\Documentos\aplicacao-json-versoes\aplicaçao-pessoal-json
"C:\Program Files (x86)\NSIS\makensis.exe" nsis-installer.nsi
```

## 📋 O que o instalador faz

1. ✅ Copia Python portátil para `Program Files\FuriousApp\portables\`
2. ✅ Copia Node portátil para `Program Files\FuriousApp\portables\`
3. ✅ Copia aria2 para `Program Files\FuriousApp\aria2\`
4. ✅ Copia backend para `Program Files\FuriousApp\backend\`
5. ✅ Copia frontend dist para `Program Files\FuriousApp\frontend\`
6. ✅ Copia launcher para `Program Files\FuriousApp\launcher\`
7. ✅ Cria atalho no Desktop: **Furious App.lnk**
8. ✅ Cria atalhos no Menu Iniciar
9. ✅ Registra no Painel de Controle (Adicionar/Remover Programas)
10. ✅ Inclui desinstalador automático

## 🚀 Testar a Aplicação

Após compilar:

1. **Execute o instalador**:
   ```
   FuriousAppInstaller.exe
   ```

2. **Siga os passos da instalação**:
   - Aceite os termos
   - Escolha pasta de destino (padrão: `C:\Program Files\FuriousApp`)
   - Próximo → Instalar

3. **Inicie a aplicação**:
   - Clique no atalho "Furious App" no Desktop
   - Ou Menu Iniciar → Furious App → Furious App
   - Ou execute: `launcher\launcher.bat`

4. **Verifique**:
   - Uma janela de terminal deve abrir
   - Um navegador deve abrir automaticamente em `http://localhost:8000`
   - A interface Furious App deve estar funcional

## ✅ Resultado Final

Você terá em mãos:

```
FuriousAppInstaller.exe  ← Instalador distribuível
```

Usuários finais precisam apenas:
1. Executar `FuriousAppInstaller.exe`
2. Clicar em "Instalar"
3. Clicar no atalho "Furious App" no Desktop

## 🆘 Resolução de Problemas

### "makensis.exe não encontrado"
- Verifique se NSIS está instalado em `C:\Program Files (x86)\NSIS`
- Se instalou em outro local, ajuste o caminho no comando

### Instalador vazio ou incompleto
- Verifique se o build do frontend está em `frontend/dist/`
- Confirme que as pastas `portables/`, `backend/`, `launcher/` existem

### Aplicação não inicia após instalação
- Verifique se Python está funcionando: `portables\python-64bits\App\Python\python.exe --version`
- Teste manualmente: `launcher\launcher.bat`

### Erro de permissões
- Execute o instalador como Administrador
- O NSIS pede automaticamente privilégios elevados

## 📚 Documentação Adicional

- NSIS Docs: https://nsis.sourceforge.io/Docs/
- MUI2 (Modern UI): https://nsis.sourceforge.io/MUI2
- StaticFiles (Starlette): https://www.starlette.io/staticfiles/

---

**Status**: ✅ Tudo pronto para compilação!
