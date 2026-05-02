# Script PowerShell para criar arquivos de teste no sistema P2P

Write-Host "🔧 Criando arquivos de teste no sistema P2P..." -ForegroundColor Cyan

# Criar diretório compartilhado se não existir
if (!(Test-Path -Path "shared_files")) {
    New-Item -ItemType Directory -Path "shared_files" | Out-Null
}

# Criar arquivos de exemplo
"Este é um TCC sobre Sistemas Distribuídos P2P" | Out-File -FilePath "shared_files\tcc_sistemas_distribuidos.zip" -Encoding UTF8
"Artigo sobre Redes de Computadores" | Out-File -FilePath "shared_files\artigo_redes.zip" -Encoding UTF8
"Trabalho de Conclusão de Curso - Segurança" | Out-File -FilePath "shared_files\tcc_seguranca.zip" -Encoding UTF8
"Pesquisa sobre Cloud Computing" | Out-File -FilePath "shared_files\artigo_cloud.zip" -Encoding UTF8
"Projeto Final - Banco de Dados" | Out-File -FilePath "shared_files\trabalho_bd.zip" -Encoding UTF8

Write-Host "✅ Arquivos criados em shared_files/:" -ForegroundColor Green
Get-ChildItem -Path "shared_files" | Format-Table Name, Length, LastWriteTime

Write-Host ""
Write-Host "📝 Instruções:" -ForegroundColor Yellow
Write-Host "1. Inicie o sistema: docker-compose up --build"
Write-Host "2. Acesse um peer: docker exec -it p2p_peer1 python peer.py"
Write-Host "3. Publique um arquivo (opção 1): /app/shared_files/tcc_sistemas_distribuidos.zip"
Write-Host ""
Write-Host "📁 Arquivos disponíveis:" -ForegroundColor Yellow
Write-Host "  - tcc_sistemas_distribuidos.zip"
Write-Host "  - artigo_redes.zip"
Write-Host "  - tcc_seguranca.zip"
Write-Host "  - artigo_cloud.zip"
Write-Host "  - trabalho_bd.zip"
