# 🎉 Bem-vindo ao Furious App!

## ✅ Instalação Completa

Sua aplicação foi instalada com sucesso em:
```
C:\Program Files\FuriousApp
```

Incluindo:
- ✅ Python 3.10.5 (python-64bits)
- ✅ Node.js 18.16.1
- ✅ aria2 1.37.0
- ✅ Backend FastAPI
- ✅ Frontend Vue.js
- ✅ Furious App.exe (Desktop Launcher)

---

## 🚀 Como Usar

### Iniciando a Aplicação

**Opção 1: Atalho no Desktop** ⭐ RECOMENDADO
- Clique duplo no ícone "Furious App" no seu Desktop
- Uma janela desktop nativa abrirá
- Sem navegador externo necessário

**Opção 2: Menu Iniciar**
- Menu Iniciar → Furious App → Furious App
- Mesma experiência desktop

**Opção 3: Executável Direto**
- Navegue até: `C:\Program Files\FuriousApp\launcher`
- Execute: `Furious App.exe`

### Interface da Aplicação

Quando clica em "Furious App":

1. 🔄 Uma janela abre (não há terminal visível)
2. 🔧 Backend Python inicia automaticamente em background
3. 🎨 Interface Vue.js renderiza em janela nativa PyQt5
4. ✅ Sistema pronto para usar em segundos

**Tela Principal:**
```
┌─────────────────────────────────────┐
│  Furious App - Desktop Nativo       │
├─────────────────────────────────────┤
│                                     │
│  [Dashboard] [Downloads] [Fontes]   │
│                                     │
│  Estatísticas em tempo real         │
│                                     │
└─────────────────────────────────────┘
```

---

## 📖 Funcionalidades Principais

### 🏠 Dashboard
- Visualize estatísticas de downloads
- Gráficos animados do progresso
- Veja downloads ativos, pausados e concluídos
- Monitore velocidade e progresso em tempo real

### 📥 Downloads
- Gerencie todos os seus downloads
- Pause, retome e cancele downloads
- Visualize detalhes, peers, seeders e velocidade
- Status em fila → rodando → concluído

### 🔗 Fontes JSON
- Carregue fontes JSON customizadas
- Selecione itens para download
- Suporte a magnets e URLs diretas
- Gerenciar fontes salvas

### ⚙️ Configurações
- Escolha pasta de destino
- Configure velocidade máxima de upload
- Gerenciar conexões simultâneas

---

## 🔧 Componentes Instalados

✅ **Python 3.10.5 Portável**
- Totalmente independente do sistema
- Sem necessidade de instalação adicional

✅ **Node.js 18.16.1 Portável**
- Ambiente de execução portátil
- Incluído para compatibilidade futura

✅ **aria2 1.37.0**
- Motor de downloads profissional
- Suporta magnets, torrents e URLs

✅ **Backend FastAPI**
- API robusta e escalável
- Gerenciamento de filas de download

✅ **Frontend Vue.js**
- Interface moderna e responsiva
- Experiência de usuário profissional

---

## 📂 Estrutura de Pastas

```
C:\Program Files\FuriousApp\
├── portables/
│   ├── python-64bits/                   (Python portátil)
│   ├── node-v18.16.1-win-x64/           (Node portátil)
│   └── aria2-1.37.0/                    (aria2 binário)
├── backend/                              (API Python/FastAPI)
├── frontend/                             (Interface Vue.js)
├── launcher/                             (Scripts de inicialização)
├── README.md                             (Documentação)
└── Uninstall.exe                         (Desinstalador)
```

---

## ❓ Dúvidas Frequentes

### P: A aplicação não inicia?
**R:** Verifique se a porta 8000 não está em uso:
```powershell
Get-NetTCPConnection -LocalPort 8000
```
Se estiver ocupada, feche o programa que está usando.

### P: Onde os arquivos são salvos?
**R:** Por padrão em `C:\Users\[Seu Usuário]\Downloads`
Você pode escolher outra pasta ao criar um download.

### P: Como faço backup dos meus downloads?
**R:** Os downloads estão em uma pasta que você escolheu.
Copie essa pasta para um local seguro.

### P: Posso usar offline?
**R:** Sim! Após instalar, a aplicação funciona completamente offline.
Não precisa de conexão com internet (exceto para downloads).

### P: Como atualizar para uma versão nova?
**R:** Desinstale a versão atual e instale a nova versão.

---

## 🛑 Desinstalação Segura

### Opção 1: Painel de Controle
1. Painel de Controle → Programas → Programas e Recursos
2. Procure por "Furious App"
3. Clique em "Desinstalar"
4. Confirme a desinstalação

### Opção 2: Menu Iniciar
1. Menu Iniciar → Todos os Programas → Furious App → Desinstalar
2. Confirme a desinstalação

### Opção 3: Pasta de Instalação
1. Navegue até: `C:\Program Files\FuriousApp`
2. Execute: `Uninstall.exe`
3. Confirme a desinstalação

**Importante:** 
- ✅ A desinstalação remove APENAS a aplicação
- ✅ Seus downloads são preservados
- ✅ Não há perda de dados do usuário
- ✅ Registro do Windows é limpado automaticamente

---

## 🔐 Privacidade e Segurança

- ✅ Nenhum dado é enviado para servidores externos
- ✅ Aplicação 100% local
- ✅ Sem rastreamento
- ✅ Seus downloads são seus

---

## 📞 Suporte e Ajuda

Para mais informações, consulte:
- `README.md` - Documentação técnica
- `COMECE_AQUI.md` - Guia rápido
- Interface da aplicação - Ajuda integrada

---

## 🎊 Pronto para Começar!

Sua aplicação está completamente funcional e pronta para uso.

**Próximos passos:**
1. Abra a aplicação (clique no atalho do Desktop)
2. Explore o Dashboard
3. Carregue uma fonte JSON ou comece um download direto
4. Aproveite! 🚀

---

**Obrigado por usar Furious App!**

Versão: 1.0.0  
Data: Dezembro 2025
