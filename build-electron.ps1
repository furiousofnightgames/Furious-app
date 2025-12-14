# Script para compilar a aplicação Electron com instalador
# Uso: .\build-electron.ps1

param(
    [ValidateSet("dev", "portable", "installer", "all")]
    [string]$Mode = "all"
)

$ErrorActionPreference = "Stop"

Write-Host "🚀 Furious App - Electron Builder" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se Node.js está instalado
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Node.js não encontrado. Instale em: https://nodejs.org/" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Node.js encontrado: $(npm --version)" -ForegroundColor Green
Write-Host ""

# Função para executar comando com tratamento de erro
function Run-Command {
    param([string]$Command, [string]$Description)
    Write-Host "📦 $Description..." -ForegroundColor Yellow
    Invoke-Expression $Command
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Erro ao executar: $Description" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ $Description concluído" -ForegroundColor Green
    Write-Host ""
}

# Desenvolvimento
if ($Mode -eq "dev" -or $Mode -eq "all") {
    Run-Command "npm install" "Instalando dependências Node.js"
    Run-Command "cd frontend && npm install && cd .." "Instalando dependências do Frontend"
    Write-Host "🎮 Iniciando modo desenvolvimento..." -ForegroundColor Cyan
    Write-Host "   Frontend: http://localhost:5173" -ForegroundColor Gray
    Write-Host "   Backend:  http://localhost:8000" -ForegroundColor Gray
    Write-Host "   Electron: Janela nativa" -ForegroundColor Gray
    Write-Host ""
    npm run dev
    exit 0
}

# Build Frontend
if ($Mode -eq "portable" -or $Mode -eq "installer" -or $Mode -eq "all") {
    Run-Command "npm install" "Instalando dependências Node.js"
    Run-Command "cd frontend && npm install && npm run build && cd .." "Build do Frontend"
}

# Build Portable
if ($Mode -eq "portable" -or $Mode -eq "all") {
    Run-Command "npm run build:electron" "Compilando Electron (Portable)"
    Write-Host "✅ App gerado em: launcher/win-unpacked/Furious App.exe" -ForegroundColor Green
    Write-Host ""
}

# Build Installer
if ($Mode -eq "installer" -or $Mode -eq "all") {
    Run-Command "npm run build:electron" "Compilando Electron (win-unpacked)"
    Write-Host "✅ Agora gere o instalador com: .\compilar-instalador.ps1" -ForegroundColor Green
    Write-Host ""
}

# Resumo Final
Write-Host "🎉 Build concluído com sucesso!" -ForegroundColor Green
Write-Host ""
Write-Host "📁 Arquivos gerados em: launcher/" -ForegroundColor Cyan
Write-Host ""

Get-ChildItem -Path "launcher" -Filter "*.exe" | ForEach-Object {
    $size = [math]::Round($_.Length / 1MB, 2)
    Write-Host "   📦 $($_.Name) - ${size}MB" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🚀 Próximos passos:" -ForegroundColor Cyan
Write-Host "   1. Testar: .\launcher\win-unpacked\Furious App.exe" -ForegroundColor Gray
Write-Host "   2. Gerar instalador: .\compilar-instalador.ps1" -ForegroundColor Gray
Write-Host ""
