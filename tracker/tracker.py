#!/usr/bin/env python3
"""
Tracker - Servidor Central do Sistema P2P
Gerencia metadados de arquivos e registro de peers
"""

import socket
import threading
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Set

class Tracker:
    def __init__(self, host='0.0.0.0', port=5000):
        self.host = host
        self.port = port
        self.peers = {}  # {peer_id: {'ip': ip, 'port': port, 'last_heartbeat': timestamp}}
        self.files = {}  # {filename: {'hash': hash, 'peers': [peer_id1, peer_id2]}}
        self.lock = threading.Lock()
        self.running = True
        self.heartbeat_timeout = 60  # segundos
        
    def start(self):
        """Inicia o servidor tracker"""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        
        print(f"[TRACKER] Iniciado em {self.host}:{self.port}")
        
        # Thread para monitorar heartbeat
        heartbeat_thread = threading.Thread(target=self.monitor_heartbeat, daemon=True)
        heartbeat_thread.start()
        
        while self.running:
            try:
                client_socket, address = server_socket.accept()
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, address),
                    daemon=True
                )
                client_thread.start()
            except Exception as e:
                print(f"[TRACKER] Erro ao aceitar conexão: {e}")
        
        server_socket.close()
    
    def handle_client(self, client_socket, address):
        """Processa requisições de clientes"""
        try:
            data = client_socket.recv(4096).decode('utf-8')
            if not data:
                return
                
            request = json.loads(data)
            command = request.get('command')
            
            print(f"[TRACKER] Recebido {command} de {address}")
            
            response = {}
            
            if command == 'REGISTER':
                response = self.register_peer(request)
            elif command == 'HEARTBEAT':
                response = self.update_heartbeat(request)
            elif command == 'PUBLISH':
                response = self.publish_file(request)
            elif command == 'LOOKUP':
                response = self.lookup_file(request)
            elif command == 'WHEREIS':
                response = self.whereis(request)
            elif command == 'LIST_PEERS':
                response = self.list_peers()
            elif command == 'LIST_FILES':
                response = self.list_files()
            elif command == 'UNREGISTER':
                response = self.unregister_peer(request)
            else:
                response = {'status': 'error', 'message': 'Comando desconhecido'}
            
            client_socket.send(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            error_response = {'status': 'error', 'message': str(e)}
            try:
                client_socket.send(json.dumps(error_response).encode('utf-8'))
            except:
                pass
            print(f"[TRACKER] Erro ao processar requisição: {e}")
        finally:
            client_socket.close()
    
    def register_peer(self, request):
        """Registra um novo peer"""
        peer_id = request.get('peer_id')
        ip = request.get('ip')
        port = request.get('port')
        
        with self.lock:
            self.peers[peer_id] = {
                'ip': ip,
                'port': port,
                'last_heartbeat': datetime.now()
            }
        
        print(f"[TRACKER] Peer registrado: {peer_id} ({ip}:{port})")
        return {'status': 'success', 'message': 'Peer registrado com sucesso'}
    
    def update_heartbeat(self, request):
        """Atualiza o heartbeat de um peer"""
        peer_id = request.get('peer_id')
        
        with self.lock:
            if peer_id in self.peers:
                self.peers[peer_id]['last_heartbeat'] = datetime.now()
                return {'status': 'success'}
            else:
                return {'status': 'error', 'message': 'Peer não registrado'}
    
    def publish_file(self, request):
        """Registra um arquivo no tracker"""
        filename = request.get('filename')
        file_hash = request.get('hash')
        peer_id = request.get('peer_id')
        
        with self.lock:
            if filename not in self.files:
                self.files[filename] = {
                    'hash': file_hash,
                    'peers': []
                }
            
            if peer_id not in self.files[filename]['peers']:
                self.files[filename]['peers'].append(peer_id)
        
        print(f"[TRACKER] Arquivo publicado: {filename} por {peer_id}")
        return {'status': 'success', 'message': 'Arquivo publicado com sucesso'}
    
    def lookup_file(self, request):
        """Busca arquivos por termo"""
        search_term = request.get('term', '').lower()
        
        with self.lock:
            results = []
            for filename, info in self.files.items():
                if search_term in filename.lower():
                    # Filtrar apenas peers ativos
                    active_peers = [p for p in info['peers'] if p in self.peers]
                    if active_peers:
                        results.append({
                            'filename': filename,
                            'hash': info['hash'],
                            'peer_count': len(active_peers)
                        })
        
        return {'status': 'success', 'results': results}
    
    def whereis(self, request):
        """Retorna a lista de peers que possuem um arquivo"""
        filename = request.get('filename')
        
        with self.lock:
            if filename in self.files:
                # Retornar apenas peers ativos
                active_peers = []
                for peer_id in self.files[filename]['peers']:
                    if peer_id in self.peers:
                        peer_info = self.peers[peer_id]
                        active_peers.append({
                            'peer_id': peer_id,
                            'ip': peer_info['ip'],
                            'port': peer_info['port']
                        })
                
                return {
                    'status': 'success',
                    'filename': filename,
                    'hash': self.files[filename]['hash'],
                    'peers': active_peers
                }
            else:
                return {'status': 'error', 'message': 'Arquivo não encontrado'}
    
    def list_peers(self):
        """Lista todos os peers ativos"""
        with self.lock:
            peers_list = []
            for peer_id, info in self.peers.items():
                peers_list.append({
                    'peer_id': peer_id,
                    'ip': info['ip'],
                    'port': info['port'],
                    'last_heartbeat': info['last_heartbeat'].isoformat()
                })
        
        return {'status': 'success', 'peers': peers_list}
    
    def list_files(self):
        """Lista todos os arquivos registrados"""
        with self.lock:
            files_list = []
            for filename, info in self.files.items():
                active_peers = [p for p in info['peers'] if p in self.peers]
                files_list.append({
                    'filename': filename,
                    'hash': info['hash'],
                    'replicas': len(active_peers),
                    'peers': active_peers
                })
        
        return {'status': 'success', 'files': files_list}
    
    def unregister_peer(self, request):
        """Remove um peer do tracker"""
        peer_id = request.get('peer_id')
        
        with self.lock:
            if peer_id in self.peers:
                del self.peers[peer_id]
                print(f"[TRACKER] Peer removido: {peer_id}")
        
        return {'status': 'success'}
    
    def monitor_heartbeat(self):
        """Monitora peers inativos e remove automaticamente"""
        while self.running:
            time.sleep(10)  # Verifica a cada 10 segundos
            
            with self.lock:
                now = datetime.now()
                inactive_peers = []
                
                for peer_id, info in self.peers.items():
                    time_diff = (now - info['last_heartbeat']).total_seconds()
                    if time_diff > self.heartbeat_timeout:
                        inactive_peers.append(peer_id)
                
                for peer_id in inactive_peers:
                    print(f"[TRACKER] Removendo peer inativo: {peer_id}")
                    del self.peers[peer_id]
                    
                    # Verificar se algum arquivo precisa de re-replicação
                    self.check_replication()
    
    def check_replication(self):
        """Verifica arquivos que precisam de re-replicação"""
        for filename, info in self.files.items():
            active_peers = [p for p in info['peers'] if p in self.peers]
            
            if len(active_peers) < 2 and len(active_peers) > 0:
                print(f"[TRACKER] ALERTA: Arquivo '{filename}' tem apenas {len(active_peers)} réplica(s)")
            elif len(active_peers) == 0:
                print(f"[TRACKER] ALERTA: Arquivo '{filename}' não tem réplicas disponíveis")

def main():
    tracker = Tracker(host='0.0.0.0', port=5000)
    try:
        tracker.start()
    except KeyboardInterrupt:
        print("\n[TRACKER] Encerrando...")
        tracker.running = False

if __name__ == '__main__':
    main()
