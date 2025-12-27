# Guia de Implantação em Produção

## Visão Geral

O Furious App é uma aplicação **desktop/local-first**. O modo “produção” típico é distribuir o **instalador Windows (.exe)** que já inclui tudo necessário (Electron + backend Python + portables).

Para testes/manutenção em ambiente de desenvolvimento, também existe o modo local via `py run.py`.

## Requisitos do Sistema

- **Sistema Operacional**: Windows 10/11 (64-bit)
- **CPU**: 2+ núcleos (recomendado 4+)
- **Memória RAM**: 4GB (mínimo), 8GB+ recomendado
- **Armazenamento**: 10GB+ de espaço livre (depende do tamanho dos downloads)

## Opções de Execução

### 1. Instalador Windows (.exe)

#### Pré-requisitos
- Windows 10/11 (64-bit)
- 2GB de espaço livre em disco
- Acesso de administrador (para instalação)

#### Passos para Instalação

1. **Baixe o instalador** mais recente da página de releases
2. **Execute o instalador** como administrador
3. **Siga o assistente** de instalação
4. **Inicie o aplicativo** pelo menu Iniciar ou atalho na área de trabalho

#### Atualização
1. **Faça backup** da pasta de downloads (opcional)
2. **Execute o instalador** da versão mais recente (ele atualiza a instalação)

### 2. Implantação Manual

#### Pré-requisitos (somente para desenvolvimento/manutenção)
- Python 3.10+
- Node.js 18+

#### Passos para Instalação

1. **Clone o repositório**
   ```bash
   git clone https://github.com/seu-usuario/aplicacao-pessoal-json.git
   cd aplicacao-pessoal-json
   ```

2. **Configure o ambiente Python**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure o frontend**
   ```bash
   cd frontend
   npm install
   npm run build
   cd ..
   ```

4. **Inicie o servidor (modo local)**
  ```bash
  py run.py
  ```

5. **Acesse a aplicação**
  - UI: http://127.0.0.1:8000
  - API Docs: http://127.0.0.1:8000/docs

## Configuração de Rede

### Portas Necessárias
- **8000**: UI/API no modo local (`py run.py`)
- **8001**: Backend no modo Electron (instalador)
- **5173**: Frontend dev (somente desenvolvimento `npm run dev`)

### Configuração de Firewall
```powershell
# Permitir tráfego na porta 8000 (Windows)
New-NetFirewallRule -DisplayName "Furious App HTTP" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow

# Se estiver usando o Aria2 remotamente
New-NetFirewallRule -DisplayName "Aria2 RPC" -Direction Inbound -LocalPort 6800 -Protocol TCP -Action Allow
```

## Configuração de Serviço no Windows

### Criar um Serviço do Windows

1. **Instale o NSSM (Non-Sucking Service Manager)**
   ```powershell
   choco install nssm
   ```

2. **Crie o serviço**
   ```powershell
   nssm install FuriousAppBackend
   ```

3. **Configure o serviço**
   - Path: `C:\caminho\para\python.exe`
   - Startup directory: `C:\caminho\para\o\projeto`
   - Arguments: `-m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4`

4. **Inicie o serviço**
   ```powershell
   net start FuriousAppBackend
   ```

## Configuração de Logs

### Localização dos Logs
- **Modo local (`py run.py`)**: `%LOCALAPPDATA%\furious-app-dev\backend.log`
- **Electron**: `%APPDATA%\furious-app\logs\backend.log`

### Níveis de Log
- `DEBUG`: Informações detalhadas para desenvolvimento
- `INFO`: Informações gerais de operação
- `WARNING`: Avisos sobre problemas não críticos
- `ERROR`: Erros que afetam a funcionalidade
- `CRITICAL`: Falhas graves que impedem o funcionamento

## Backup e Recuperação

### Dados a serem copiados
- Banco de dados SQLite: `%APPDATA%\furious-app\app.db` (Electron) ou `./app.db` (local)
- Pasta de downloads: configurada pelo usuário (padrão em Downloads)
- Configurações: `%APPDATA%\furious-app\config.json` (Electron) ou `./config.json` (local)
- Logs importantes: `backend.log`, `aria2.log` em `%APPDATA%\furious-app\logs`

### Script de Backup (Windows)
```powershell
# backup.ps1
$date = Get-Date -Format "yyyyMMdd_HHmmss"
$backupDir = "C:\Backups\FuriousApp\$date"

# Criar diretório de backup
New-Item -ItemType Directory -Path $backupDir -Force

# Copiar arquivos importantes
Copy-Item -Path ".\app.db" -Destination "$backupDir\app.db"
Copy-Item -Path ".\.env" -Destination "$backupDir\env.backup"
Copy-Item -Path ".\backend.log" -Destination "$backupDir\backend.log" -ErrorAction SilentlyContinue

# Compactar pasta de downloads (opcional)
Compress-Archive -Path ".\downloads\*" -DestinationPath "$backupDir\downloads_$date.zip"

Write-Host "Backup concluído em $backupDir"
```

## Atualização

### Processo de Atualização
1. **Faça backup** dos dados importantes
2. **Pare o serviço** (se aplicável)
3. **Atualize o código**
   ```bash
   git pull origin main
   ```
4. **Atualize as dependências**
   ```bash
   pip install -r requirements.txt
   cd frontend
   npm install
   npm run build
   cd ..
   ```
5. **Execute migrações** (se houver)
   ```bash
   # Exemplo de migração futura
   # python -m alembic upgrade head
   ```
6. **Reinicie o serviço**

## Monitoramento

Monitoramento recomendado:
- Logs locais do backend
- Uso de CPU/Memória (Task Manager)
- Espaço em disco (pasta de downloads)

## Segurança

### Melhores Práticas
1. **Nunca exponha** a API publicamente sem autenticação
2. Use HTTPS em produção
3. Mantenha as dependências atualizadas
4. Monitore os logs regularmente
5. Use um firewall para restringir o acesso

### Atualizações de Segurança
- Assine nossa newsletter de segurança
- Siga as atualizações no GitHub
- Aplique patches de segurança assim que disponíveis

## Solução de Problemas

### Problemas Comuns

#### Aplicativo não inicia
- Verifique os logs em `backend.log`
- Confira se a porta 8000 está disponível
- Verifique se todas as dependências estão instaladas

#### Downloads lentos
- Verifique a velocidade da internet
- Aumente o número de conexões nas configurações
- Verifique se há limitações no servidor de origem

#### Erros de permissão
- Execute o aplicativo como administrador
- Verifique as permissões das pastas de download e logs

## Suporte

### Canais de Suporte
- **GitHub Issues**: Para relatar bugs e solicitar recursos
- **Email**: suporte@exemplo.com
- **Fórum**: https://forum.exemplo.com

### Horário de Atendimento
- Segunda a Sexta: 9h às 18h (GMT-3)
- Finais de semana e feriados: Plantão apenas para incidentes críticos

## Próximos Passos

1. Padronizar documentação e checklist de release
2. Melhorar diagnósticos locais (logs/telemetria) para troubleshooting
3. Ajustar UX de downloads (sugestão de alternativas ao falhar)
