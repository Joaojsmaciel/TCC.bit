#!/bin/bash
# Script para criar arquivos de teste no sistema P2P

echo "🔧 Criando arquivos de teste no sistema P2P..."

# Criar diretório compartilhado se não existir
mkdir -p shared_files

# Criar arquivos de exemplo
echo "Este é um TCC sobre Sistemas Distribuídos P2P" > shared_files/tcc_sistemas_distribuidos.zip
echo "Artigo sobre Redes de Computadores" > shared_files/artigo_redes.zip
echo "Trabalho de Conclusão de Curso - Segurança" > shared_files/tcc_seguranca.zip
echo "Pesquisa sobre Cloud Computing" > shared_files/artigo_cloud.zip
echo "Projeto Final - Banco de Dados" > shared_files/trabalho_bd.zip

echo "✅ Arquivos criados em shared_files/:"
ls -lh shared_files/

echo ""
echo "📝 Instruções:"
echo "1. Inicie o sistema: docker-compose up --build"
echo "2. Acesse um peer: docker exec -it p2p_peer1 python peer.py"
echo "3. Publique um arquivo (opção 1): /app/shared_files/tcc_sistemas_distribuidos.zip"
echo ""
echo "📁 Arquivos disponíveis:"
echo "  - tcc_sistemas_distribuidos.zip"
echo "  - artigo_redes.zip"
echo "  - tcc_seguranca.zip"
echo "  - artigo_cloud.zip"
echo "  - trabalho_bd.zip"
