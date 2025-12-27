# Guia de Desenvolvimento

## Configuração do Ambiente

### Pré-requisitos

- Windows 10/11 (64-bit)
- Git
- Node.js 18+ (incluindo npm)
- Python 3.10+
- Aria2 (já incluído no projeto)

### Configuração Inicial

1. **Clonar o repositório**
   ```bash
   git clone https://github.com/seu-usuario/aplicacao-pessoal-json.git
   cd aplicacao-pessoal-json
   ```

2. **Configurar Ambiente Virtual Python**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # Linux/macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instalar Dependências do Backend**
   ```bash
   pip install -r requirements.txt
   ```

4. **Instalar Dependências do Frontend**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

## Estrutura do Projeto

```
.
├── backend/               # Código-fonte do backend (FastAPI)
│   ├── __init__.py
│   ├── main.py           # Ponto de entrada da API
│   ├── config.py         # Configurações
│   ├── db.py             # Configuração do banco de dados
│   ├── models/           # Modelos de dados
│   ├── services/         # Lógica de negócios
│   └── utils/            # Utilitários
├── frontend/             # Aplicação Vue.js
│   ├── public/           # Arquivos estáticos
│   ├── src/
│   │   ├── assets/       # Recursos estáticos
│   │   ├── components/   # Componentes Vue
│   │   ├── router/       # Configuração de rotas
│   │   ├── stores/       # Gerenciamento de estado (Pinia)
│   │   ├── views/        # Páginas/rotas
│   │   ├── App.vue       # Componente raiz
│   │   └── main.js       # Ponto de entrada
│   ├── package.json
│   └── vite.config.js
├── engine/               # Motor de downloads
├── launcher/             # Saída do build/instalador (electron-builder)
├── docs/                 # Documentação
├── electron-main.js      # Entrada do Electron
├── electron-preload.js   # Preload do Electron
└── run.py                # Modo local (backend+frontend) em 8000
```

## Desenvolvimento

### Iniciar Backend

```bash
# No diretório raiz do projeto (modo local)
py run.py
```

O servidor estará disponível em `http://127.0.0.1:8000`

### Iniciar Frontend

```bash
# No diretório frontend
cd frontend
npm run dev
```

O frontend estará disponível em `http://localhost:5173`

### Executar Testes

Atualmente não há suíte de testes automatizada configurada por padrão.

### Padrões de Código

#### Python
- Siga o PEP 8
- Use type hints
- Documente funções e classes com docstrings
- Mantenha as importações organizadas

#### JavaScript/Vue
- Siga o Standard JS
- Use a Composition API com `<script setup>`
- Componentes em PascalCase (ex: `MyComponent.vue`)
- Nomes de eventos em kebab-case (ex: `@item-selected`)

## Fluxo de Trabalho com Git

1. Crie uma branch para sua feature/correção:
   ```bash
   git checkout -b feature/nova-funcionalidade
   ```

2. Faça commits atômicos com mensagens descritivas:
   ```
   feat: adiciona suporte a múltiplos downloads
   fix: corrige vazamento de memória no gerenciador de downloads
   docs: atualiza documentação da API
   refactor: melhora organização dos componentes
   ```

3. Envie suas alterações:
   ```bash
   git push origin feature/nova-funcionalidade
   ```

4. Abra um Pull Request no GitHub

## Depuração

### Backend

Ative o modo debug para ver logs detalhados:
```bash
DEBUG=1 uvicorn backend.main:app --reload
```

Logs são salvos em `backend.log`

### Frontend

Use as DevTools do navegador (F12) para:
- Ver erros no console
- Inspecionar o estado do Vue
- Monitorar requisições de rede

## Construção para Produção

### Backend
```bash
py run.py
```

### Frontend
```bash
cd frontend
npm run build
```

## Dicas para Desenvolvimento

1. **HMR (Hot Module Replacement)**
   - O Vite oferece HMR para desenvolvimento rápido
   - As alterações no código são refletidas instantaneamente

2. **Mock de Dados**
  - O frontend consome a API real do backend local.

3. **Variáveis de Ambiente**
   - Backend: `.env` na raiz do projeto
   - Frontend: `.env` no diretório `frontend`

4. **Extensões Úteis para VSCode**
   - Python
   - Vue Language Features (Volar)
   - ESLint
   - Prettier
   - Tailwind CSS IntelliSense

## Solução de Problemas Comuns

### Erro ao instalar dependências Python
- Certifique-se de ter o Python 3.10+ instalado
- Atualize o pip: `python -m pip install --upgrade pip`

### Erros de CORS
- Verifique se as URLs estão corretas no `backend/config.py`
- Certifique-se de que o frontend está acessando a URL correta da API

### Problemas com o Aria2
- Verifique se o executável tem permissões de execução
- Confira se não há outra instância do Aria2 em execução

## Recursos Adicionais

- [Documentação do FastAPI](https://fastapi.tiangolo.com/)
- [Documentação do Vue 3](https://vuejs.org/guide/introduction.html)
- [Documentação do Tailwind CSS](https://tailwindcss.com/docs)
- [Documentação do Aria2](https://aria2.github.io/manual/en/html/)

## Contribuição

1. Leia o [Código de Conduta](CODE_OF_CONDUCT.md)
2. Abra uma issue para discutir sua proposta
3. Envie um Pull Request com suas alterações
4. Aguarde a revisão e feedback

## Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.
