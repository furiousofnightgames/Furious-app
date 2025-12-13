# Configuração do Launcher - Furious App

## 📋 Resumo da Implementação

O launcher agora possui uma tela de inicialização moderna e holográfica com tema cyberpunk, desenvolvida com PyQt5 + QWebEngineView.

## 🎨 Features da Tela de Inicialização

- **Design Holográfico**: Gradiente roxo/azul escuro com borda de glow
- **Animações Suaves**: 
  - Logo com animação de bounce (pequeno movimento vertical)
  - Progress bar com efeito pulsante
  - Transição suave quando aplicação carrega
- **Status em Tempo Real**: Mensagens atualizáveis de progresso
- **Tema Ciberpunk**: Cores #7c00ff, #00d4ff, #00ff00, #ff00ff
- **Responsive**: Se adapta ao tamanho da janela

## ⚙️ Configuração Importante

### 1️⃣ Porta do Backend
O launcher assume que o backend escuta em **127.0.0.1:8000**

Se usar outra porta, edite em `launcher/furious_app_desktop.py`:
```python
def _check_backend_ready(self):
    try:
        url = "http://127.0.0.1:8000/"  # ← Ajuste aqui se necessário
```

### 2️⃣ Caminhos Portáveis
O `BackendThread` espera por padrão:
- **Python**: `portables/python-64bits/App/Python/python.exe`
- **Backend**: `backend/main.py`

Se sua estrutura for diferente, ajuste em `furious_app_desktop.py` no `BackendThread.__init__`:
```python
def __init__(self, install_dir: Path, python_rel_path=None, backend_main_rel="backend/main.py"):
    ...
    self.python_rel_path = python_rel_path or Path("portables/python-64bits/App/Python/python.exe")
```

### 3️⃣ Ícone da Janela
- **Com favicon**: Coloque `favicon.ico` em `frontend/dist/`
- **Sem favicon**: Usa o ícone padrão (método `_create_svg_icon` gera ícone SVG com tema ciberpunk)

Para forçar o SVG, descomentar em `__init__`:
```python
# Descomente se quiser sempre usar SVG:
# self._create_svg_icon()
```

### 4️⃣ Empacotamento em .exe com NSIS

Ao empacotar com PyInstaller/NSIS, certifique-se que:
1. A pasta `portables/` fica relativa ao `.exe`
2. A pasta `backend/` fica relativa ao `.exe`
3. A pasta `frontend/dist/` fica relativa ao `.exe`

O launcher detecta automaticamente com:
```python
if getattr(sys, 'frozen', False):
    exe_path = Path(sys.executable)  # Path do .exe
else:
    exe_path = Path(__file__).resolve()  # Path do script
```

## 📁 Estrutura Esperada

```
aplicacao-json-versoes/
├── launcher/
│   ├── furious_app_desktop.py      ← Launcher principal
│   ├── Furious App.exe             ← Compilado com PyInstaller
│   └── dist/
│       └── Furious App.exe         ← Cópia do executável
├── frontend/
│   ├── dist/
│   │   ├── index.html
│   │   └── favicon.ico             ← (opcional) Ícone da janela
│   └── ...
├── backend/
│   ├── main.py                     ← FastAPI server
│   └── ...
└── portables/
    ├── python-64bits/
    │   └── App/Python/python.exe
    ├── aria2-1.37.0/
    └── node-v18.16.1-win-x64/
```

## 🔧 API do Launcher

### Classe `HoloSplash`

```python
splash = HoloSplash()
splash.set_status("Carregando componentes...")  # Atualiza texto
splash.set_progress(50)                          # Atualiza progress (0-100)
```

### Classe `FuriousAppLauncher`

Herda de `QMainWindow`, detecta backend automaticamente e exibe tela de carregamento.

#### Métodos Principais

- `_check_backend_ready()`: Testa se servidor HTTP responde
- `_show_webview()`: Mostra aplicação web quando pronta
- `_fade_out_splash()`: Transição suave do splash para aplicação
- `_create_svg_icon()`: Gera ícone SVG com tema ciberpunk

## 🎯 Fluxo de Inicialização

1. **Janela abre** com splash screen
2. **Backend inicia** em thread separada
3. **Splash anima** enquanto aguarda servidor
4. **Backend responde** em `http://127.0.0.1:8000`
5. **Aplicação web carrega** no browser
6. **Splash faz fade-out** suavemente
7. **Aplicação fica visível**

## ⏱️ Timeouts

- **Verificação de backend**: 500ms (configurável em `_check_timer.setInterval()`)
- **Máximo de espera**: 55 segundos (configurável em `self._max_startup_ms`)
- **Fade-out do splash**: 600ms

## 🐛 Troubleshooting

### Problema: "Backend não encontrado"
✅ Verifique caminho em `BackendThread.python_rel_path`

### Problema: "Servidor não responde"
✅ Verifique se backend está rodando em `http://127.0.0.1:8000`
✅ Veja logs em `backend.log`

### Problema: Ícone não aparece
✅ Coloque `favicon.ico` em `frontend/dist/`
✅ Ou o SVG será usado automaticamente

### Problema: Janela muito lenta
✅ Aumente timeout em `_max_startup_ms`
✅ Verifique recursos do sistema

## 📝 Notas Técnicas

- **PyQt5**: Framework GUI com suporte a web engine
- **QWebEngineView**: Renderiza aplicação Vue.js
- **Backend Thread**: Roda backend em processo separado
- **Detecção automática**: Funciona como script e como .exe empacotado
- **Sem console**: Processo backend escondido, sem janela visível

## 🚀 Compilação

```bash
# Frontend
cd frontend
npm run build

# Launcher
cd ..
.\compilar-launcher.bat

# Instalador (opcional)
.\compilar-instalador.bat
```

## 📦 Dependências

- **PyQt5** >= 5.15
- **PyQtWebEngine** >= 5.15
- **FastAPI** (backend)
- **Uvicorn** (backend)
- **Python 3.10+**

---

**Última atualização**: 6 de dezembro de 2025
**Versão**: 1.0.0 - Holographic Launcher
