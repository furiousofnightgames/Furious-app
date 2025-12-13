# Script para Compilar Instalador NSIS - Furious App
# Autor: Agent Antigravity
# Descrição: Compila o instalador NSIS customizado a partir do build Electron existente

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -Path $ScriptDir

Function Write-Header {
    Param([string]$Text)
    Write-Host ""
    Write-Host ("=" * 50) -ForegroundColor Cyan
    Write-Host "  $Text" -ForegroundColor Cyan
    Write-Host ("=" * 50) -ForegroundColor Cyan
    Write-Host ""
}

# --- Início ---
Write-Header ">> COMPILANDO INSTALADOR NSIS"

# Verifica se o build Electron existe
if (-not (Test-Path "launcher\win-unpacked\Furious App.exe")) {
    Write-Error "[X] Build do Electron nao encontrado!"
    Write-Host "    Execute primeiro: .\compilar-launcher.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host "[OK] Build do Electron encontrado." -ForegroundColor Green

try {
    # Verifica se o NSIS está instalado
    $nsisPath = $null
    $possiblePaths = @(
        "C:\Program Files (x86)\NSIS\makensis.exe",
        "C:\Program Files\NSIS\makensis.exe",
        "$env:ProgramFiles\NSIS\makensis.exe",
        "$env:ProgramFiles(x86)\NSIS\makensis.exe"
    )
    
    foreach ($path in $possiblePaths) {
        if (Test-Path $path) {
            $nsisPath = $path
            break
        }
    }
    
    if (-not $nsisPath) {
        Write-Error "[X] NSIS nao encontrado!"
        Write-Host "    Instale o NSIS de: https://nsis.sourceforge.io/Download" -ForegroundColor Yellow
        exit 1
    }
    
    Write-Host "[OK] NSIS encontrado: $nsisPath" -ForegroundColor Green
    Write-Host ""
    Write-Host "   Compilando instalador..." -ForegroundColor Gray
    
    # Compila o instalador
    & $nsisPath "nsis-installer-electron.nsi"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Header ">> SUCESSO!"
        Write-Host "[OK] Instalador criado com sucesso!" -ForegroundColor Green
        
        if (Test-Path "launcher\Furious App Setup 2.0.0.exe") {
            $installerSize = [math]::Round((Get-Item "launcher\Furious App Setup 2.0.0.exe").Length / 1MB, 2)
            Write-Host "   Arquivo: launcher\Furious App Setup 2.0.0.exe" -ForegroundColor White
            Write-Host "   Tamanho: $installerSize MB" -ForegroundColor White
        }
    } else {
        Write-Error "[X] Falha ao compilar instalador NSIS (codigo $LASTEXITCODE)"
        exit 1
    }
} catch {
    Write-Error "[X] Erro ao compilar instalador NSIS: $_"
    exit 1
}

Write-Host ""
