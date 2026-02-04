# 🐧 Análise de Portabilidade: Furious App no Linux (Estratégia Self-Contained)

Este documento detalha o plano para criar uma versão Linux do Furious App que seja tão fácil de usar quanto a versão Windows: **Baixar e Rodar (AppImage)**, sem exigir que o usuário instale nada no terminal.

## 📊 Diagnóstico e Estratégia

| Componente | Windows (Atual) | Linux (Nova Estratégia) | Benefício |
| :--- | :--- | :--- | :--- |
| **Formato** | Instalador .exe (NSIS) | **AppImage** | Roda em qualquer distro (Ubuntu, Fedora, Arch, SteamDeck) sem instalação. |
| **Python** | Portable Python (Embed) | **Standalone Python Build** | Evita o "inferno de dependências" e problemas com GLIBC. Usaremos builds do `indygreg`. |
| **Aria2** | Portable aria2c.exe | **Static Binary aria2c** | Executável estático que roda em qualquer lugar. |

---

## 🛠️ O Roteiro de Migração (Passo a Passo)

### 1. Obter os Binários Portáteis para Linux

Em vez de usar o `python` do sistema, vamos baixar versões portáteis e colocar na pasta `portables/linux/`.

*   **Python**: Baixar release do [python-build-standalone](https://github.com/indygreg/python-build-standalone).
    *   *Recomendado:* `cpython-3.10.x-x86_64-unknown-linux-gnu-install_only.tar.gz`
    *   Extrair em: `portables/linux/python/`
*   **Aria2**: Baixar binário estático.
    *   *Fonte:* [q3aql/aria2-static-builds](https://github.com/q3aql/aria2-static-builds)
    *   Colocar em: `portables/linux/aria2c`

### 2. Configurar `electron-builder.yml` para Multi-Plataforma

Vamos configurar o build para incluir a pasta `portables/linux` apenas quando estiver construindo para Linux, e `portables/windows` apenas para Windows.

```yaml
# Configuração base
files:
  - electron-main.js
  - backend/**/*
  - ...

# Especialização Windows
win:
  target: nsis
  files:
    - from: portables/windows
      to: portables/windows
    - "!portables/linux"  # Não incluir linux no exe

# Especialização Linux
linux:
  target: AppImage
  category: Game
  files:
    - from: portables/linux
      to: portables/linux
    - "!portables/windows" # Não incluir exe no AppImage
```

### 3. Lógica de Detecção no `electron-main.js`

O código precisa saber qual executável chamar dependendo do SO.

```javascript
/* Lógica Híbrida (Windows + Linux Portable) */
let PYTHON_EXECUTABLE;
let ARIA2_PATH;

if (process.platform === 'win32') {
  // Windows: Usa os .exe
  PYTHON_EXECUTABLE = path.join(process.resourcesPath, 'portables', 'windows', 'python', 'python.exe');
  ARIA2_PATH = path.join(process.resourcesPath, 'portables', 'windows', 'aria2c.exe');
} else {
  // Linux: Usa os binários da pasta linux (DENTRO do AppImage)
  PYTHON_EXECUTABLE = path.join(process.resourcesPath, 'portables', 'linux', 'python', 'bin', 'python3');
  ARIA2_PATH = path.join(process.resourcesPath, 'portables', 'linux', 'aria2c');
  
  // Garantir permissão de execução (chmod +x) na primeira execução
  const fs = require('fs');
  try {
    fs.chmodSync(PYTHON_EXECUTABLE, '755');
    fs.chmodSync(ARIA2_PATH, '755');
  } catch(e) { /* Ignorar se já tiver permissão */ }
}
```

---

## 🏎️ Experiência do Usuário (Steam Deck / Linux Desktop)

1. Usuário baixa `FuriousApp-3.3.1.AppImage`.
2. Clica com botão direito -> "Permitir execução" (ou `chmod +x`).
3. Dois cliques -> O App abre.
4. **Sem `sudo`, sem `apt install`, sem config.**

## 🧪 Próximos Passos Reais

1.  **Baixar os "Assets"**: Preciso de alguém com acesso à internet para baixar os `.tar.gz` do Python Linux e o binário do Aria2 e colocar na pasta do projeto.
2.  **Organizar Pastas**:
    *   Renomear `portables/python-64bits` -> `portables/windows/python`
    *   Criar `portables/linux/python`
3.  **Atualizar Scripts**: Aplicar as mudanças no código JS e YAML acima.

Essa abordagem garante que seu app rode no **Steam Deck (SteamOS)**, que é baseado em Linux (Arch) e tem sistema de arquivos imutável (você não consegue instalar dependências facilmente lá). AppImage é a solução perfeita para o Deck.
