#!/usr/bin/env python3
"""
Peer - Nó da rede P2P
Atua como cliente e servidor simultaneamente
"""

import socket
import threading
import json
import os
import sys
import time
import uuid

from network import NetworkManager
from file_manager import FileManager
from heartbeat import HeartbeatManager
from replication import ReplicationManager
from ui import CLI
from gui import PeerGUI

class Peer:
    def __init__(self, tracker_host, tracker_port, peer_port=None, peer_id=None):
        # Gerar ID único para o peer se não fornecido
        self.peer_id = peer_id or f"peer_{uuid.uuid4().hex[:8]}"
        
        # Determinar IP do peer
        self.peer_ip = self.get_local_ip()
        
        # Porta do peer (gerada automaticamente se não fornecida)
        self.peer_port = peer_port or self.find_free_port()
        
        # Gerenciadores
        self.network = NetworkManager(tracker_host, tracker_port)
        self.file_manager = FileManager(storage_dir=f'./files_{self.peer_id}')
        self.heartbeat = HeartbeatManager(self.network, self.peer_id, interval=30)
        self.replication = ReplicationManager(self.network, self.file_manager, self.peer_id)
        self.ui = CLI()
        
        # Controle
        self.running = False
        self.server_socket = None
        self.server_thread = None
    
    def get_local_ip(self):
        """Obtém o IP local do peer"""
        try:
            # Tentar conectar a um endereço externo para descobrir IP local
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return '127.0.0.1'
    
    def find_free_port(self, start_port=6000, max_attempts=100):
        """Encontra uma porta livre"""
        for port in range(start_port, start_port + max_attempts):
            try:
                test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                test_socket.bind(('', port))
                test_socket.close()
                return port
            except:
                continue
        return start_port
    
    def start(self):
        """Inicia o peer"""
        print(f"\n[PEER] Iniciando peer {self.peer_id}")
        print(f"[PEER] IP: {self.peer_ip}, Porta: {self.peer_port}")
        
        # Registrar no tracker
        response = self.network.register_peer(self.peer_id, self.peer_ip, self.peer_port)
        if response.get('status') != 'success':
            print(f"[PEER] ERRO ao registrar no tracker: {response.get('message')}")
            return False
        
        print(f"[PEER] Registrado no tracker com sucesso")
        
        # Iniciar servidor de arquivos
        self.running = True
        self.server_thread = threading.Thread(target=self.run_server, daemon=True)
        self.server_thread.start()
        
        # Iniciar heartbeat
        self.heartbeat.start()
        
        print(f"[PEER] Peer iniciado com sucesso!")
        return True
    
    def stop(self):
        """Para o peer"""
        print(f"\n[PEER] Encerrando peer {self.peer_id}...")
        
        self.running = False
        
        # Parar heartbeat
        self.heartbeat.stop()
        
        # Desregistrar do tracker
        self.network.unregister_peer(self.peer_id)
        
        # Fechar servidor
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        print(f"[PEER] Peer encerrado")
    
    def run_server(self):
        """Executa o servidor de arquivos do peer"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('0.0.0.0', self.peer_port))
            self.server_socket.listen(5)
            self.server_socket.settimeout(1.0)  # Timeout para permitir verificação de self.running
            
            print(f"[PEER SERVER] Servidor escutando na porta {self.peer_port}")
            
            while self.running:
                try:
                    client_socket, address = self.server_socket.accept()
                    client_thread = threading.Thread(
                        target=self.handle_peer_request,
                        args=(client_socket, address),
                        daemon=True
                    )
                    client_thread.start()
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        print(f"[PEER SERVER] Erro ao aceitar conexão: {e}")
        
        except Exception as e:
            print(f"[PEER SERVER] Erro ao iniciar servidor: {e}")
    
    def handle_peer_request(self, client_socket, address):
        """Processa requisições de outros peers"""
        try:
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                return
            
            request = json.loads(data)
            command = request.get('command')
            
            if command == 'DOWNLOAD':
                self.handle_download_request(client_socket, request)
            elif command == 'UPLOAD':
                self.handle_upload_request(client_socket, request)
            else:
                response = {'status': 'error', 'message': 'Comando desconhecido'}
                client_socket.send(json.dumps(response).encode('utf-8'))
        
        except Exception as e:
            print(f"[PEER SERVER] Erro ao processar requisição: {e}")
        finally:
            client_socket.close()
    
    def handle_download_request(self, client_socket, request):
        """Processa requisição de download de arquivo"""
        filename = request.get('filename')
        
        if not self.file_manager.has_file(filename):
            response = {'status': 'error', 'message': 'Arquivo não encontrado'}
            client_socket.send(json.dumps(response).encode('utf-8'))
            return
        
        file_path = self.file_manager.get_file_path(filename)
        file_size = self.file_manager.get_file_size(filename)
        
        # Enviar resposta inicial
        response = {
            'status': 'success',
            'file_size': file_size
        }
        client_socket.send(json.dumps(response).encode('utf-8'))
        
        # Enviar arquivo em blocos
        print(f"[PEER SERVER] Enviando arquivo '{filename}' ({file_size} bytes)")
        
        try:
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(1024)
                    if not chunk:
                        break
                    client_socket.send(chunk)
            
            print(f"[PEER SERVER] Arquivo '{filename}' enviado com sucesso")
        except Exception as e:
            print(f"[PEER SERVER] Erro ao enviar arquivo: {e}")
    
    def handle_upload_request(self, client_socket, request):
        """Processa requisição de upload de arquivo (replicação)"""
        filename = request.get('filename')
        file_size = request.get('file_size', 0)
        
        # Enviar confirmação
        response = {'status': 'ready'}
        client_socket.send(json.dumps(response).encode('utf-8'))
        
        # Receber arquivo
        file_path = os.path.join(self.file_manager.storage_dir, filename)
        
        print(f"[PEER SERVER] Recebendo arquivo '{filename}' ({file_size} bytes)")
        
        try:
            received = 0
            with open(file_path, 'wb') as f:
                while received < file_size:
                    chunk = client_socket.recv(1024)
                    if not chunk:
                        break
                    f.write(chunk)
                    received += len(chunk)
            
            # Adicionar arquivo ao gerenciador
            success, result = self.file_manager.add_file(file_path, filename)
            
            if success:
                print(f"[PEER SERVER] Arquivo '{filename}' recebido e registrado")
                
                # Publicar no tracker
                self.network.publish_file(self.peer_id, filename, result)
            else:
                print(f"[PEER SERVER] Erro ao registrar arquivo: {result}")
        
        except Exception as e:
            print(f"[PEER SERVER] Erro ao receber arquivo: {e}")
    
    def publish_file(self, file_path):
        """Publica um arquivo na rede"""
        if not os.path.exists(file_path):
            self.ui.print_error("Arquivo não encontrado")
            return False
        
        filename = os.path.basename(file_path)
        
        # Adicionar arquivo ao storage do peer
        success, result = self.file_manager.add_file(file_path, filename)
        
        if not success:
            self.ui.print_error(f"Erro ao adicionar arquivo: {result}")
            return False
        
        file_hash = result
        
        # Publicar no tracker
        response = self.network.publish_file(self.peer_id, filename, file_hash)
        
        if response.get('status') != 'success':
            self.ui.print_error(f"Erro ao publicar no tracker: {response.get('message')}")
            return False
        
        self.ui.print_success(f"Arquivo '{filename}' publicado (hash: {file_hash[:16]}...)")
        
        # Iniciar replicação
        self.ui.print_info("Iniciando replicação...")
        self.replication.replicate_file(filename, file_hash)
        
        return True
    
    def search_files(self, search_term):
        """Busca arquivos na rede"""
        response = self.network.lookup_file(search_term)
        
        if response.get('status') != 'success':
            self.ui.print_error("Erro ao buscar arquivos")
            return []
        
        results = response.get('results', [])
        return results
    
    def download_file(self, filename):
        """Baixa um arquivo da rede"""
        # Verificar se já possui o arquivo
        if self.file_manager.has_file(filename):
            self.ui.print_info("Você já possui este arquivo")
            return False
        
        # Buscar peers que têm o arquivo
        response = self.network.whereis_file(filename)
        
        if response.get('status') != 'success':
            self.ui.print_error(f"Arquivo não encontrado: {response.get('message')}")
            return False
        
        peers = response.get('peers', [])
        
        if not peers:
            self.ui.print_error("Nenhum peer disponível com este arquivo")
            return False
        
        # Selecionar melhor peer
        selected_peer = self.replication.get_best_peer_for_download(peers)
        
        if not selected_peer:
            self.ui.print_error("Erro ao selecionar peer")
            return False
        
        peer_ip = selected_peer['ip']
        peer_port = selected_peer['port']
        peer_id = selected_peer['peer_id']
        
        self.ui.print_info(f"Baixando de {peer_id} ({peer_ip}:{peer_port})")
        
        # Download do arquivo
        save_path = os.path.join(self.file_manager.storage_dir, filename)
        
        def progress_callback(current, total):
            self.ui.print_progress_bar(current, total)
        
        success, message = self.network.download_file_from_peer(
            peer_ip, peer_port, filename, save_path, progress_callback
        )
        
        print()  # Nova linha após barra de progresso
        
        if not success:
            self.ui.print_error(f"Erro ao baixar arquivo: {message}")
            return False
        
        # Registrar arquivo localmente
        self.file_manager.add_file(save_path, filename)
        
        # Publicar no tracker
        file_info = self.file_manager.get_file_info(filename)
        if file_info:
            self.network.publish_file(self.peer_id, filename, file_info['hash'])
        
        self.ui.print_success(f"Arquivo '{filename}' baixado com sucesso!")
        
        return True
    
    def run_cli(self):
        """Executa a interface CLI"""
        self.ui.clear_screen()
        self.ui.print_header()
        
        print(f"Peer ID: {self.peer_id}")
        print(f"Endereço: {self.peer_ip}:{self.peer_port}")
        
        while self.running:
            self.ui.print_menu()
            choice = self.ui.get_input("Escolha uma opção")
            
            if choice == '1':
                # Publicar arquivo
                file_path = self.ui.get_input("Caminho do arquivo")
                self.publish_file(file_path)
                self.ui.wait_for_enter()
            
            elif choice == '2':
                # Buscar arquivos
                search_term = self.ui.get_input("Termo de busca")
                results = self.search_files(search_term)
                self.ui.print_files_table(results)
                self.ui.wait_for_enter()
            
            elif choice == '3':
                # Baixar arquivo
                filename = self.ui.get_input("Nome do arquivo")
                self.download_file(filename)
                self.ui.wait_for_enter()
            
            elif choice == '4':
                # Listar arquivos locais
                files = self.file_manager.list_files()
                self.ui.print_files_table(files)
                self.ui.wait_for_enter()
            
            elif choice == '5':
                # Listar todos os arquivos da rede
                response = self.network.list_files()
                if response.get('status') == 'success':
                    files = response.get('files', [])
                    self.ui.print_files_table(files)
                else:
                    self.ui.print_error("Erro ao obter lista de arquivos")
                self.ui.wait_for_enter()
            
            elif choice == '6':
                # Listar peers ativos
                response = self.network.list_peers()
                if response.get('status') == 'success':
                    peers = response.get('peers', [])
                    self.ui.print_peers_table(peers)
                else:
                    self.ui.print_error("Erro ao obter lista de peers")
                self.ui.wait_for_enter()
            
            elif choice == '7':
                # Status do sistema
                self.ui.print_divider()
                print(f"Peer ID: {self.peer_id}")
                print(f"Endereço: {self.peer_ip}:{self.peer_port}")
                print(f"Arquivos locais: {len(self.file_manager.list_files())}")
                print(f"Heartbeat ativo: {'Sim' if self.heartbeat.running else 'Não'}")
                self.ui.print_divider()
                self.ui.wait_for_enter()
            
            elif choice == '0':
                # Sair
                if self.ui.confirm_action("Deseja realmente sair?"):
                    break
            
            else:
                self.ui.print_error("Opção inválida")
                time.sleep(1)
    
    def run_gui(self):
        """Executa a interface gráfica"""
        gui = PeerGUI(self)
        gui.run()

def main():
    # Configurações do tracker (podem ser passadas via variáveis de ambiente)
    tracker_host = os.environ.get('TRACKER_HOST', 'localhost')
    tracker_port = int(os.environ.get('TRACKER_PORT', '5000'))
    peer_port = int(os.environ.get('PEER_PORT', '0'))  # 0 = porta automática
    peer_id = os.environ.get('PEER_ID', None)
    
    print(f"Conectando ao tracker em {tracker_host}:{tracker_port}...")
    
    # Aguardar tracker estar disponível
    max_retries = 10
    for i in range(max_retries):
        try:
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.settimeout(2)
            test_socket.connect((tracker_host, tracker_port))
            test_socket.close()
            break
        except:
            print(f"Aguardando tracker... ({i+1}/{max_retries})")
            time.sleep(2)
    else:
        print("ERRO: Não foi possível conectar ao tracker")
        sys.exit(1)
    
    # Criar e iniciar peer
    peer = Peer(tracker_host, tracker_port, peer_port, peer_id)
    
    if not peer.start():
        print("ERRO ao iniciar peer")
        sys.exit(1)
    
    try:
        peer.run_cli()
    except KeyboardInterrupt:
        print("\n\nInterrompido pelo usuário")
    finally:
        peer.stop()

if __name__ == '__main__':
    main()
