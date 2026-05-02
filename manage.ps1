# Script PowerShell para gerenciar o Sistema P2P
# Equivalente ao Makefile para usuários Windows

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

function Show-Help {
    Write-Host ""
    Write-Host "Sistema P2P - Comandos Disponíveis" -ForegroundColor Cyan
    Write-Host "===================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Uso: .\manage.ps1 <comando>" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Comandos:" -ForegroundColor Green
    Write-Host "  build         " -NoNewline; Write-Host "Constrói as imagens Docker"
    Write-Host "  up/start      " -NoNewline; Write-Host "Inicia o sistema (tracker + 3 peers)"
    Write-Host "  down/stop     " -NoNewline; Write-Host "Para o sistema"
    Write-Host "  restart       " -NoNewline; Write-Host "Reinicia o sistema"
    Write-Host "  logs          " -NoNewline; Write-Host "Mostra logs de todos os containers"
    Write-Host "  logs-tracker  " -NoNewline; Write-Host "Mostra logs do tracker"
    Write-Host "  logs-peer1    " -NoNewline; Write-Host "Mostra logs do peer1"
    Write-Host "  logs-peer2    " -NoNewline; Write-Host "Mostra logs do peer2"
    Write-Host "  logs-peer3    " -NoNewline; Write-Host "Mostra logs do peer3"
    Write-Host "  peer1         " -NoNewline; Write-Host "Acessa interface do Peer 1"
    Write-Host "  peer2         " -NoNewline; Write-Host "Acessa interface do Peer 2"
    Write-Host "  peer3         " -NoNewline; Write-Host "Acessa interface do Peer 3"
    Write-Host "  status/ps     " -NoNewline; Write-Host "Mostra status de todos os containers"
    Write-Host "  files         " -NoNewline; Write-Host "Cria arquivos de teste"
    Write-Host "  test          " -NoNewline; Write-Host "Inicia sistema com arquivos de teste"
    Write-Host "  clean         " -NoNewline; Write-Host "Remove containers, volumes e arquivos"
    Write-Host "  clean-all     " -NoNewline; Write-Host "Remove tudo, incluindo imagens"
    Write-Host "  rebuild       " -NoNewline; Write-Host "Reconstrói e reinicia tudo"
    Write-Host "  shell-peer1   " -NoNewline; Write-Host "Abre shell no container do peer1"
    Write-Host "  shell-peer2   " -NoNewline; Write-Host "Abre shell no container do peer2"
    Write-Host "  shell-peer3   " -NoNewline; Write-Host "Abre shell no container do peer3"
    Write-Host "  shell-tracker " -NoNewline; Write-Host "Abre shell no container do tracker"
    Write-Host ""
}

function Build {
    Write-Host "Construindo imagens..." -ForegroundColor Green
    docker-compose build
}

function Up {
    Write-Host "Iniciando sistema P2P..." -ForegroundColor Green
    docker-compose up -d
    Write-Host "Sistema iniciado!" -ForegroundColor Green
    Write-Host "Acesse os peers com:" -ForegroundColor Yellow
    Write-Host "  .\manage.ps1 peer1"
    Write-Host "  .\manage.ps1 peer2"
    Write-Host "  .\manage.ps1 peer3"
}

function Down {
    Write-Host "Parando sistema..." -ForegroundColor Green
    docker-compose down
}

function Restart {
    Down
    Up
}

function Logs {
    docker-compose logs -f
}

function Logs-Tracker {
    docker-compose logs -f tracker
}

function Logs-Peer1 {
    docker-compose logs -f peer1
}

function Logs-Peer2 {
    docker-compose logs -f peer2
}

function Logs-Peer3 {
    docker-compose logs -f peer3
}

function Peer1 {
    Write-Host "Acessando Peer 1..." -ForegroundColor Green
    docker exec -it p2p_peer1 python peer.py
}

function Peer2 {
    Write-Host "Acessando Peer 2..." -ForegroundColor Green
    docker exec -it p2p_peer2 python peer.py
}

function Peer3 {
    Write-Host "Acessando Peer 3..." -ForegroundColor Green
    docker exec -it p2p_peer3 python peer.py
}

function Status {
    Write-Host "Status dos Containers:" -ForegroundColor Green
    docker-compose ps
}

function Create-Files {
    Write-Host "Criando arquivos de teste..." -ForegroundColor Green
    
    if (!(Test-Path -Path "shared_files")) {
        New-Item -ItemType Directory -Path "shared_files" | Out-Null
    }
    
    "Este é um TCC sobre Sistemas Distribuídos P2P" | Out-File -FilePath "shared_files\tcc_sistemas_distribuidos.zip" -Encoding UTF8
    "Artigo sobre Redes de Computadores" | Out-File -FilePath "shared_files\artigo_redes.zip" -Encoding UTF8
    "Trabalho de Conclusão de Curso - Segurança" | Out-File -FilePath "shared_files\tcc_seguranca.zip" -Encoding UTF8
    "Pesquisa sobre Cloud Computing" | Out-File -FilePath "shared_files\artigo_cloud.zip" -Encoding UTF8
    "Projeto Final - Banco de Dados" | Out-File -FilePath "shared_files\trabalho_bd.zip" -Encoding UTF8
    
    Write-Host "Arquivos criados em shared_files/" -ForegroundColor Green
    Get-ChildItem -Path "shared_files" | Format-Table Name, Length, LastWriteTime
}

function Clean {
    Write-Host "Limpando sistema..." -ForegroundColor Green
    docker-compose down -v
    
    if (Test-Path -Path "shared_files") {
        Remove-Item -Path "shared_files" -Recurse -Force
    }
    
    Get-ChildItem -Path "." -Filter "files_*" -Directory | Remove-Item -Recurse -Force
    
    Write-Host "Sistema limpo!" -ForegroundColor Green
}

function Clean-All {
    Clean
    Write-Host "Removendo imagens Docker..." -ForegroundColor Green
    docker rmi sistematcc_tracker sistematcc_peer1 sistematcc_peer2 sistematcc_peer3 2>$null
    Write-Host "Limpeza completa!" -ForegroundColor Green
}

function Test {
    Create-Files
    Up
    Write-Host "Sistema iniciado com arquivos de teste!" -ForegroundColor Green
    Start-Sleep -Seconds 3
    Write-Host "Aguardando inicialização..." -ForegroundColor Yellow
    Start-Sleep -Seconds 2
    Write-Host "Pronto! Use '.\manage.ps1 peer1' para acessar um peer." -ForegroundColor Green
}

function Shell-Peer1 {
    docker exec -it p2p_peer1 sh
}

function Shell-Peer2 {
    docker exec -it p2p_peer2 sh
}

function Shell-Peer3 {
    docker exec -it p2p_peer3 sh
}

function Shell-Tracker {
    docker exec -it p2p_tracker sh
}

function Rebuild {
    Clean
    Build
    Up
}

# Executar comando
switch ($Command.ToLower()) {
    "help" { Show-Help }
    "build" { Build }
    "up" { Up }
    "start" { Up }
    "down" { Down }
    "stop" { Down }
    "restart" { Restart }
    "logs" { Logs }
    "logs-tracker" { Logs-Tracker }
    "logs-peer1" { Logs-Peer1 }
    "logs-peer2" { Logs-Peer2 }
    "logs-peer3" { Logs-Peer3 }
    "peer1" { Peer1 }
    "peer2" { Peer2 }
    "peer3" { Peer3 }
    "status" { Status }
    "ps" { Status }
    "files" { Create-Files }
    "clean" { Clean }
    "clean-all" { Clean-All }
    "test" { Test }
    "shell-peer1" { Shell-Peer1 }
    "shell-peer2" { Shell-Peer2 }
    "shell-peer3" { Shell-Peer3 }
    "shell-tracker" { Shell-Tracker }
    "rebuild" { Rebuild }
    default {
        Write-Host "Comando desconhecido: $Command" -ForegroundColor Red
        Write-Host ""
        Show-Help
    }
}
