# Script para executar o sistema P2P com Interface Gráfica
# Uso: .\run_gui.ps1

Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host " Sistema P2P - Interface Gráfica" -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se Python está instalado
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ ERRO: Python não encontrado!" -ForegroundColor Red
    Write-Host "Por favor, instale Python 3.8 ou superior." -ForegroundColor Yellow
    exit 1
}

# Perguntar se deseja iniciar o tracker
Write-Host ""
$startTracker = Read-Host "Deseja iniciar o tracker? (S/N)"

if ($startTracker -eq "S" -or $startTracker -eq "s") {
    Write-Host ""
    Write-Host "🚀 Iniciando Tracker..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\tracker'; python tracker.py"
    Start-Sleep -Seconds 2
}

# Solicitar configurações do peer
Write-Host ""
Write-Host "Configuração do Peer:" -ForegroundColor Cyan
Write-Host "-----------------------------------------------------"

$trackerHost = Read-Host "Host do Tracker (padrão: localhost)"
if ([string]::IsNullOrWhiteSpace($trackerHost)) {
    $trackerHost = "localhost"
}

$trackerPort = Read-Host "Porta do Tracker (padrão: 5000)"
if ([string]::IsNullOrWhiteSpace($trackerPort)) {
    $trackerPort = "5000"
}

$peerPort = Read-Host "Porta do Peer (padrão: automático, deixe vazio)"
if ([string]::IsNullOrWhiteSpace($peerPort)) {
    $peerPort = "0"
}

# Configurar variáveis de ambiente
$env:TRACKER_HOST = $trackerHost
$env:TRACKER_PORT = $trackerPort
$env:PEER_PORT = $peerPort

Write-Host ""
Write-Host "🎨 Iniciando Interface Gráfica..." -ForegroundColor Green
Write-Host ""

# Navegar para a pasta peer e executar
Set-Location -Path "$PSScriptRoot\peer"
python peer_gui.py

# Finalização
Write-Host ""
Write-Host "Aplicação encerrada." -ForegroundColor Yellow
