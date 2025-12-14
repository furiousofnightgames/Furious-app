# Script de Compilação Robusto - Furious App
# Autor: Agent Antigravity
# Descrição: Compila Frontend, prepara backend portable e gera instalador/executable com Electron Builder.

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -Path $ScriptDir

# --- Configurações ---
$FrontendDir = Join-Path $ScriptDir "frontend"
$OutputDir = Join-Path $ScriptDir "launcher"
$DistDir = Join-Path $ScriptDir "dist"

Function Write-Header {
    Param([string]$Text)
    Write-Host ""
    Write-Host ("=" * 50) -ForegroundColor Cyan
    Write-Host "  $Text" -ForegroundColor Cyan
    Write-Host ("=" * 50) -ForegroundColor Cyan
    Write-Host ""
}

Function Check-Command {
    Param([string]$Cmd, [string]$Name)
    if (-not (Get-Command $Cmd -ErrorAction SilentlyContinue)) {
        Write-Error " $Name não encontrado! Por favor instale dependências."
        exit 1
    }
}

# --- Início ---
# --- Início ---
Write-Header ">> INICIANDO COMPILACAO FURIOUS APP"

# 0. Verificar Administrador (Necessário para symlinks do Electron Builder)
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Header "ATENCAO: PRIVILEGIOS DE ADMINISTRADOR NECESSARIOS"
    Write-Host "[!] O Electron Builder precisa criar links simbolicos (symlinks)." -ForegroundColor Yellow
    Write-Host "    Por favor, feche este terminal e abra o PowerShell como ADMINISTRADOR." -ForegroundColor Red
    Write-Host "    (Clique direito no PowerShell -> Executar como Administrador)" -ForegroundColor Gray
    Write-Host ""
    Write-Error "Abortando: Requer privilegios de administrador."
    exit 1
}
Write-Host "[OK] Executando como Administrador." -ForegroundColor Green

# 1. Verificações
Check-Command "npm" "Node.js/NPM"
Write-Host "[OK] Ambiente verificado." -ForegroundColor Green

# 2. Limpeza (preservando launcher/images)
Write-Host "[*] Limpando builds anteriores..." -ForegroundColor Yellow
# Remove apenas os arquivos de build, mantendo a pasta images
if (Test-Path "$OutputDir\*.exe") { Remove-Item "$OutputDir\*.exe" -Force -ErrorAction SilentlyContinue }
if (Test-Path "$OutputDir\win-unpacked") { Remove-Item "$OutputDir\win-unpacked" -Recurse -Force -ErrorAction SilentlyContinue }
if (Test-Path "$OutputDir\builder-*.yml") { Remove-Item "$OutputDir\builder-*.yml" -Force -ErrorAction SilentlyContinue }
if (Test-Path "$OutputDir\builder-*.yaml") { Remove-Item "$OutputDir\builder-*.yaml" -Force -ErrorAction SilentlyContinue }
if (Test-Path $DistDir) { Remove-Item $DistDir -Recurse -Force -ErrorAction SilentlyContinue }
if (Test-Path "$FrontendDir\dist") { Remove-Item "$FrontendDir\dist" -Recurse -Force -ErrorAction SilentlyContinue }

# 3. Build Frontend
Write-Header ">> COMPILANDO FRONTEND (Vite)"
Push-Location $FrontendDir
try {
    Write-Host "   Instalando dependencias frontend..." -ForegroundColor Gray
    cmd /c "npm install --silent"
    if ($LASTEXITCODE -ne 0) { throw "npm install failed with code $LASTEXITCODE" }
    
    Write-Host "   Compilando assets..." -ForegroundColor Gray
    cmd /c "npm run build"
    if ($LASTEXITCODE -ne 0) { throw "npm run build failed with code $LASTEXITCODE" }
    
    if (-not (Test-Path "dist\index.html")) {
        throw "Build do frontend falhou: dist\index.html nao encontrado."
    }
    Write-Host "[OK] Frontend compilado com sucesso." -ForegroundColor Green
} catch {
    Write-Error "[X] Falha no build do frontend: $_"
    Pop-Location
    exit 1
}
Pop-Location

# 4. Build Electron
Write-Header ">> COMPILANDO ELECTRON"
try {
    Write-Host "   Instalando dependencias root..." -ForegroundColor Gray
    cmd /c "npm install --silent"
    if ($LASTEXITCODE -ne 0) { throw "npm install root failed with code $LASTEXITCODE" }

    Write-Host "   Gerando executavel e instalador (Windows x64)..." -ForegroundColor Gray
    
    # Usando npx para chamar o electron-builder localmente com retry
    $Env:ELECTRON_BUILDER_ALLOW_UNRESOLVED_DEPENDENCIES="true"
    
    # Retry logic para lidar com falhas de rede (503, timeouts, etc)
    $maxRetries = 3
    $retryCount = 0
    $buildSuccess = $false
    
    while (-not $buildSuccess -and $retryCount -lt $maxRetries) {
        if ($retryCount -gt 0) {
            Write-Host "   [!] Tentativa $($retryCount + 1) de $maxRetries..." -ForegroundColor Yellow
            Start-Sleep -Seconds 10
        }
        
        cmd /c "npx electron-builder --win --x64 -c.extraMetadata.main=electron-main.js"
        
        if ($LASTEXITCODE -eq 0) {
            $buildSuccess = $true
        } else {
            $retryCount++
            if ($retryCount -lt $maxRetries) {
                Write-Host "   [!] Falha no build. Aguardando antes de tentar novamente..." -ForegroundColor Yellow
            }
        }
    }
    
    if (-not $buildSuccess) {
        throw "electron-builder failed after $maxRetries attempts"
    }

    Write-Host "[OK] Build Electron concluido." -ForegroundColor Green
} catch {
    Write-Error "[X] Falha no build do Electron: $_"
    exit 1
}

# 5. Organização Final
Write-Header ">> FINALIZANDO"

$rootExePattern = Join-Path $OutputDir "*.exe"
$unpackedExe = Join-Path $OutputDir "win-unpacked\Furious App.exe"

if (Test-Path $rootExePattern) {
    $Exes = Get-ChildItem $rootExePattern
    Write-Host "Arquivos gerados em: $OutputDir" -ForegroundColor Green
    foreach ($exe in $Exes) {
        $SizeMB = [math]::Round($exe.Length / 1MB, 2)
        Write-Host "   [EXE] $($exe.Name) ($SizeMB MB)" -ForegroundColor White
    }
} elseif (Test-Path $unpackedExe) {
    $exe = Get-Item $unpackedExe
    $SizeMB = [math]::Round($exe.Length / 1MB, 2)
    Write-Host "Arquivos gerados em: $($exe.DirectoryName)" -ForegroundColor Green
    Write-Host "   [EXE] $($exe.Name) ($SizeMB MB)" -ForegroundColor White
} else {
    Write-Warning "[!] Nenhum .exe encontrado na pasta de saida esperada."
}

Write-Header ">> SUCESSO! APLICACAO PRONTA."
Write-Host "Executavel portable gerado:" -ForegroundColor Green
Write-Host "   $OutputDir\win-unpacked\Furious App.exe" -ForegroundColor White
Write-Host ""
Write-Host "Para criar o instalador NSIS, execute:" -ForegroundColor Gray
Write-Host "   .\compilar-instalador.ps1" -ForegroundColor Cyan
Write-Host ""
