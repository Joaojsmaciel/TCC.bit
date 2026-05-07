#!/usr/bin/env python3
"""
UI - Interface de linha de comando (CLI) para o Peer
"""

import os

class CLI:
    def __init__(self):
        self.running = True
    
    def clear_screen(self):
        """Limpa a tela do terminal"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        """Exibe o cabeçalho da aplicação"""
        print("=" * 60)
        print(" 📁 SISTEMA P2P DE COMPARTILHAMENTO DE ARQUIVOS")
        print("=" * 60)
        print()
    
    def print_menu(self):
        """Exibe o menu principal"""
        print("\n┌─────────────────────────────────────────────────────┐")
        print("│                  MENU PRINCIPAL                     │")
        print("├─────────────────────────────────────────────────────┤")
        print("│  1. Publicar arquivo (publish)                      │")
        print("│  2. Buscar arquivos (search)                        │")
        print("│  3. Baixar arquivo (download)                       │")
        print("│  4. Listar arquivos locais (list_local)             │")
        print("│  5. Listar todos os arquivos da rede (list_all)     │")
        print("│  6. Listar peers ativos (list_peers)                │")
        print("│  7. Status do sistema                               │")
        print("│  8. Gerenciar Peers (Admin)                         │")
        print("│  0. Sair (exit)                                     │")
        print("└─────────────────────────────────────────────────────┘")
    
    def get_input(self, prompt):
        """Obtém entrada do usuário"""
        return input(f"\n{prompt}: ").strip()
    
    def print_success(self, message):
        """Exibe mensagem de sucesso"""
        print(f"\n✓ {message}")
    
    def print_error(self, message):
        """Exibe mensagem de erro"""
        print(f"\n✗ ERRO: {message}")
    
    def print_info(self, message):
        """Exibe mensagem informativa"""
        print(f"\nℹ {message}")
    
    def print_files_table(self, files):
        """Exibe tabela de arquivos"""
        if not files:
            print("\nNenhum arquivo encontrado.")
            return
        
        print("\n┌────────────────────────────────────────────────────────────────┐")
        print("│                        ARQUIVOS                                │")
        print("├───┬─────────────────────────────┬──────────┬───────────────────┤")
        print("│ # │ Nome do Arquivo             │ Réplicas │ Hash (primeiros)  │")
        print("├───┼─────────────────────────────┼──────────┼───────────────────┤")
        
        for idx, file_info in enumerate(files, 1):
            filename = file_info.get('filename', 'N/A')
            replicas = file_info.get('replicas', file_info.get('peer_count', 0))
            file_hash = file_info.get('hash', 'N/A')[:16]
            
            # Truncar nome do arquivo se for muito longo
            if len(filename) > 27:
                filename = filename[:24] + "..."
            
            print(f"│{idx:3d}│ {filename:27} │    {replicas:2d}    │ {file_hash:17} │")
        
        print("└───┴─────────────────────────────┴──────────┴───────────────────┘")
    
    def print_peers_table(self, peers):
        """Exibe tabela de peers"""
        if not peers:
            print("\nNenhum peer ativo encontrado.")
            return
        
        print("\n┌────────────────────────────────────────────────────────────┐")
        print("│                       PEERS ATIVOS                         │")
        print("├───┬─────────────────────┬───────────────────┬──────────────┤")
        print("│ # │ Peer ID             │ Endereço          │ Porta        │")
        print("├───┼─────────────────────┼───────────────────┼──────────────┤")
        
        for idx, peer_info in enumerate(peers, 1):
            peer_id = peer_info.get('peer_id', 'N/A')[:19]
            peer_ip = peer_info.get('ip', 'N/A')
            peer_port = peer_info.get('port', 'N/A')
            
            print(f"│{idx:3d}│ {peer_id:19} │ {peer_ip:17} │ {peer_port:12} │")
        
        print("└───┴─────────────────────┴───────────────────┴──────────────┘")
    
    def print_peer_management_menu(self):
        """Exibe menu de gerenciamento de peers"""
        print("\n┌─────────────────────────────────────────────────────┐")
        print("│              GERENCIAMENTO DE PEERS                 │")
        print("├─────────────────────────────────────────────────────┤")
        print("│  1. Listar todos os peers                           │")
        print("│  2. Adicionar peer manualmente                      │")
        print("│  3. Remover peer                                    │")
        print("│  4. Editar informações do peer                      │")
        print("│  5. Ver detalhes de um peer                         │")
        print("│  0. Voltar ao menu principal                        │")
        print("└─────────────────────────────────────────────────────┘")
    
    def print_peer_details(self, peer_info):
        """Exibe detalhes completos de um peer"""
        print("\n┌─────────────────────────────────────────────────────┐")
        print("│              DETALHES DO PEER                       │")
        print("├─────────────────────────────────────────────────────┤")
        print(f"│  Peer ID: {peer_info.get('peer_id', 'N/A'):37} │")
        print(f"│  IP: {peer_info.get('ip', 'N/A'):46} │")
        print(f"│  Porta: {str(peer_info.get('port', 'N/A')):44} │")
        
        if 'last_heartbeat' in peer_info:
            print(f"│  Último Heartbeat: {peer_info['last_heartbeat'][:19]:29} │")
        
        if 'files' in peer_info:
            print(f"│  Arquivos: {len(peer_info['files']):40} │")
        
        print("└─────────────────────────────────────────────────────┘")
    
    def print_progress_bar(self, current, total, bar_length=40):
        """Exibe barra de progresso"""
        if total == 0:
            percent = 100
        else:
            percent = int((current / total) * 100)
        
        filled = int((bar_length * current) // total) if total > 0 else bar_length
        bar = '█' * filled + '░' * (bar_length - filled)
        
        # Converter bytes para formato legível
        def format_bytes(bytes_value):
            for unit in ['B', 'KB', 'MB', 'GB']:
                if bytes_value < 1024.0:
                    return f"{bytes_value:.1f} {unit}"
                bytes_value /= 1024.0
            return f"{bytes_value:.1f} TB"
        
        current_str = format_bytes(current)
        total_str = format_bytes(total)
        
        print(f"\r[{bar}] {percent}% ({current_str}/{total_str})", end='', flush=True)
    
    def confirm_action(self, message):
        """Solicita confirmação do usuário"""
        response = input(f"\n{message} (s/n): ").strip().lower()
        return response in ['s', 'sim', 'y', 'yes']
    
    def wait_for_enter(self):
        """Aguarda usuário pressionar Enter"""
        input("\nPressione Enter para continuar...")
    
    def print_divider(self):
        """Exibe uma linha divisória"""
        print("\n" + "─" * 60)
