#!/usr/bin/env python3
"""
Tracker - Servidor Central do Sistema P2P
Gerencia metadados de arquivos e registro de peers
"""

import socket
import threading
import json
import time
from datetime import datetime

from prometheus_client import Gauge, start_http_server

P2P_ACTIVE_PEERS = Gauge(
    'p2p_active_peers',
    'Quantidade de peers ativos registrados no tracker'
)


class Tracker:
    def __init__(self, host='0.0.0.0', port=5000):
        self.host = host
        self.port = port
        self.peers = {}  # {peer_id: {'ip': ip, 'port': port, 'last_heartbeat': timestamp}}
        self.files = {}  # {hash: {'filename': filename, 'peers': [peer_id1, peer_id2]}}
        self.lock = threading.Lock()
        self.running = True
        self.heartbeat_timeout = 60  # segundos
        self.min_replicas = 2
        start_http_server(8000)
        P2P_ACTIVE_PEERS.set(0)

    @staticmethod
    def send_json(sock, message):
        payload = json.dumps(message).encode('utf-8') + b'\n'
        sock.sendall(payload)

    @staticmethod
    def recv_json(sock):
        data = bytearray()
        while True:
            chunk = sock.recv(1)
            if not chunk:
                break
            if chunk == b'\n':
                break
            data.extend(chunk)

        if not data:
            raise ConnectionError("Conexao encerrada antes do JSON")

        return json.loads(data.decode('utf-8'))
        
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
            request = self.recv_json(client_socket)
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
            elif command == 'LIST':
                target = request.get('target', 'files')
                response = self.list_peers() if target == 'peers' else self.list_files()
            elif command == 'LIST_PEERS':
                response = self.list_peers()
            elif command == 'LIST_FILES':
                response = self.list_files()
            elif command == 'UNREGISTER':
                response = self.unregister_peer(request)
            else:
                response = {'status': 'error', 'message': 'Comando desconhecido'}
            
            self.send_json(client_socket, response)
            
        except Exception as e:
            error_response = {'status': 'error', 'message': str(e)}
            try:
                self.send_json(client_socket, error_response)
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
            P2P_ACTIVE_PEERS.set(len(self.peers))
        
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

        if not filename or not file_hash or not peer_id:
            return {'status': 'error', 'message': 'Metadados incompletos'}
        
        with self.lock:
            if file_hash not in self.files:
                self.files[file_hash] = {
                    'filename': filename,
                    'peers': []
                }
            
            if peer_id not in self.files[file_hash]['peers']:
                self.files[file_hash]['peers'].append(peer_id)
        
        print(f"[TRACKER] Arquivo publicado: {filename} por {peer_id}")
        return {'status': 'success', 'message': 'Arquivo publicado com sucesso'}
    
    def lookup_file(self, request):
        """Busca arquivos por termo"""
        search_term = request.get('term', '').lower()
        
        with self.lock:
            results = []
            for file_hash, info in self.files.items():
                filename = info['filename']
                if search_term in filename.lower():
                    # Filtrar apenas peers ativos
                    active_peers = [p for p in info['peers'] if p in self.peers]
                    if active_peers:
                        results.append({
                            'filename': filename,
                            'hash': file_hash,
                            'peer_count': len(active_peers)
                        })
        
        return {'status': 'success', 'results': results}
    
    def whereis(self, request):
        """Retorna a lista de peers que possuem um arquivo"""
        filename = request.get('filename')
        file_hash = request.get('hash')
        
        with self.lock:
            if not file_hash and filename:
                for candidate_hash, info in self.files.items():
                    if info['filename'] == filename:
                        file_hash = candidate_hash
                        break

            if file_hash in self.files:
                info = self.files[file_hash]
                # Retornar apenas peers ativos
                active_peers = []
                for peer_id in info['peers']:
                    if peer_id in self.peers:
                        peer_info = self.peers[peer_id]
                        active_peers.append({
                            'peer_id': peer_id,
                            'ip': peer_info['ip'],
                            'port': peer_info['port']
                        })
                
                return {
                    'status': 'success',
                    'filename': info['filename'],
                    'hash': file_hash,
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
            for file_hash, info in self.files.items():
                active_peers = [p for p in info['peers'] if p in self.peers]
                files_list.append({
                    'filename': info['filename'],
                    'hash': file_hash,
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
                P2P_ACTIVE_PEERS.set(len(self.peers))
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

                if inactive_peers:
                    P2P_ACTIVE_PEERS.set(len(self.peers))

            if inactive_peers:
                # Verificar fora do lock para nao bloquear novas requisicoes.
                self.check_replication()
    
    def check_replication(self):
        """Verifica arquivos que precisam de re-replicação"""
        replication_jobs = []

        with self.lock:
            for file_hash, info in self.files.items():
                active_holders = [p for p in info['peers'] if p in self.peers]

                if len(active_holders) == 0:
                    print(f"[TRACKER] ALERTA: Arquivo '{info['filename']}' não tem réplicas disponíveis")
                    continue

                if len(active_holders) >= self.min_replicas:
                    continue

                source_peer_id = active_holders[0]
                source_peer = self.peers[source_peer_id]
                required_successes = self.min_replicas - len(active_holders)
                candidates = [p for p in self.peers if p not in active_holders]

                if not candidates:
                    print(f"[TRACKER] ALERTA: Arquivo '{info['filename']}' precisa de re-replicação, mas nao ha destino ativo")
                    continue

                replication_jobs.append({
                    'source_peer_id': source_peer_id,
                    'source_ip': source_peer['ip'],
                    'source_port': source_peer['port'],
                    'filename': info['filename'],
                    'hash': file_hash,
                    'required_successes': required_successes,
                    'exclude_peers': active_holders
                })

        for job in replication_jobs:
            self.force_replicate(job)

    def force_replicate(self, job):
        """Instrui um peer ativo a criar novas réplicas do arquivo."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(10)
                sock.connect((job['source_ip'], job['source_port']))
                self.send_json(sock, {
                    'command': 'FORCE_REPLICATE',
                    'filename': job['filename'],
                    'hash': job['hash'],
                    'required_successes': job['required_successes'],
                    'exclude_peers': job['exclude_peers']
                })
                response = self.recv_json(sock)

            if response.get('status') == 'accepted':
                print(f"[TRACKER] FORCE_REPLICATE enviado para {job['source_peer_id']} ({job['filename']})")
            else:
                print(f"[TRACKER] FORCE_REPLICATE recusado por {job['source_peer_id']}: {response.get('message')}")
        except Exception as e:
            print(f"[TRACKER] Falha ao enviar FORCE_REPLICATE para {job['source_peer_id']}: {e}")

def main():
    tracker = Tracker(host='0.0.0.0', port=5000)
    try:
        tracker.start()
    except KeyboardInterrupt:
        print("\n[TRACKER] Encerrando...")
        tracker.running = False

if __name__ == '__main__':
    main()
