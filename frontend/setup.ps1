#!/usr/bin/env powershell

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   Launcher JSON Accelerator - Frontend Setup              ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check if Node.js is installed
Write-Host "Verificando Node.js..." -ForegroundColor Yellow
$nodeVersion = node --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Node.js não encontrado. Por favor, instale Node.js 18+" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Node.js $nodeVersion encontrado" -ForegroundColor Green

# Check if npm is installed
Write-Host "Verificando npm..." -ForegroundColor Yellow
$npmVersion = npm --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ npm não encontrado" -ForegroundColor Red
    exit 1
}
Write-Host "✅ npm $npmVersion encontrado" -ForegroundColor Green
Write-Host ""

# Install dependencies
Write-Host "📦 Instalando dependências..." -ForegroundColor Yellow
npm install
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro ao instalar dependências" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Dependências instaladas" -ForegroundColor Green
Write-Host ""

# Build frontend
Write-Host "🔨 Compilando frontend..." -ForegroundColor Yellow
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro ao compilar" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Frontend compilado com sucesso" -ForegroundColor Green
Write-Host ""

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║        Setup Concluído com Sucesso! ✅                    ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "Próximos passos:" -ForegroundColor Cyan
Write-Host "  1. Inicie o backend: .\run_backend.ps1" -ForegroundColor White
Write-Host "  2. Para desenvolvimento: npm run dev" -ForegroundColor White
Write-Host "  3. Para produção: O frontend já está em ./dist" -ForegroundColor White
Write-Host ""
