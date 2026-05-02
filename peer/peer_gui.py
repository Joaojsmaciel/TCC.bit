#!/usr/bin/env python3
"""
Peer GUI - Ponto de entrada para a versão com interface gráfica
"""

import socket
import os
import sys
import time

from peer import Peer


def main():
    # Configurações do tracker (podem ser passadas via variáveis de ambiente)
    tracker_host = os.environ.get('TRACKER_HOST', 'localhost')
    tracker_port = int(os.environ.get('TRACKER_PORT', '5000'))
    peer_port = int(os.environ.get('PEER_PORT', '0'))  # 0 = porta automática
    peer_id = os.environ.get('PEER_ID', None)
    
    print(f"🚀 Iniciando Sistema P2P com Interface Gráfica")
    print(f"Conectando ao tracker em {tracker_host}:{tracker_port}...")
    
    # Aguardar tracker estar disponível
    max_retries = 10
    for i in range(max_retries):
        try:
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.settimeout(2)
            test_socket.connect((tracker_host, tracker_port))
            test_socket.close()
            print(f"✓ Tracker encontrado!")
            break
        except:
            print(f"⏳ Aguardando tracker... ({i+1}/{max_retries})")
            time.sleep(2)
    else:
        print("❌ ERRO: Não foi possível conectar ao tracker")
        print("Certifique-se de que o tracker está executando.")
        sys.exit(1)
    
    # Criar e iniciar peer
    peer = Peer(tracker_host, tracker_port, peer_port, peer_id)
    
    if not peer.start():
        print("❌ ERRO ao iniciar peer")
        sys.exit(1)
    
    try:
        # Iniciar interface gráfica
        peer.run_gui()
    except KeyboardInterrupt:
        print("\n⚠ Interrompido pelo usuário")
    finally:
        peer.stop()
        print("👋 Aplicação encerrada")


if __name__ == '__main__':
    main()
