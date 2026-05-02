#!/usr/bin/env python3
"""
Network - Módulo de comunicação de rede para o Peer
Gerencia conexões com o tracker e outros peers
"""

import socket
import json

class NetworkManager:
    def __init__(self, tracker_host, tracker_port):
        self.tracker_host = tracker_host
        self.tracker_port = tracker_port
    
    def send_to_tracker(self, message):
        """Envia uma mensagem JSON para o tracker e retorna a resposta"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(10)
                sock.connect((self.tracker_host, self.tracker_port))
                sock.send(json.dumps(message).encode('utf-8'))
                response = sock.recv(4096).decode('utf-8')
                return json.loads(response)
        except Exception as e:
            print(f"[NETWORK] Erro ao comunicar com tracker: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def register_peer(self, peer_id, ip, port):
        """Registra o peer no tracker"""
        message = {
            'command': 'REGISTER',
            'peer_id': peer_id,
            'ip': ip,
            'port': port
        }
        return self.send_to_tracker(message)
    
    def send_heartbeat(self, peer_id):
        """Envia heartbeat para o tracker"""
        message = {
            'command': 'HEARTBEAT',
            'peer_id': peer_id
        }
        return self.send_to_tracker(message)
    
    def publish_file(self, peer_id, filename, file_hash):
        """Publica um arquivo no tracker"""
        message = {
            'command': 'PUBLISH',
            'peer_id': peer_id,
            'filename': filename,
            'hash': file_hash
        }
        return self.send_to_tracker(message)
    
    def lookup_file(self, search_term):
        """Busca arquivos no tracker"""
        message = {
            'command': 'LOOKUP',
            'term': search_term
        }
        return self.send_to_tracker(message)
    
    def whereis_file(self, filename):
        """Consulta quais peers têm um arquivo"""
        message = {
            'command': 'WHEREIS',
            'filename': filename
        }
        return self.send_to_tracker(message)
    
    def list_peers(self):
        """Lista todos os peers registrados"""
        message = {
            'command': 'LIST_PEERS'
        }
        return self.send_to_tracker(message)
    
    def list_files(self):
        """Lista todos os arquivos registrados"""
        message = {
            'command': 'LIST_FILES'
        }
        return self.send_to_tracker(message)
    
    def unregister_peer(self, peer_id):
        """Remove o peer do tracker"""
        message = {
            'command': 'UNREGISTER',
            'peer_id': peer_id
        }
        return self.send_to_tracker(message)
    
    def download_file_from_peer(self, peer_ip, peer_port, filename, save_path, progress_callback=None):
        """Baixa um arquivo de outro peer"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(30)
                sock.connect((peer_ip, peer_port))
                
                # Solicitar arquivo
                request = {
                    'command': 'DOWNLOAD',
                    'filename': filename
                }
                sock.send(json.dumps(request).encode('utf-8'))
                
                # Receber resposta
                response_data = sock.recv(1024).decode('utf-8')
                response = json.loads(response_data)
                
                if response.get('status') != 'success':
                    return False, response.get('message', 'Erro desconhecido')
                
                file_size = response.get('file_size', 0)
                
                # Receber arquivo em blocos
                received = 0
                with open(save_path, 'wb') as f:
                    while received < file_size:
                        chunk = sock.recv(1024)
                        if not chunk:
                            break
                        f.write(chunk)
                        received += len(chunk)
                        
                        if progress_callback:
                            progress_callback(received, file_size)
                
                return True, "Download concluído"
                
        except Exception as e:
            return False, str(e)
    
    def send_file_to_peer(self, peer_ip, peer_port, filename, file_path):
        """Envia um arquivo para outro peer (para replicação)"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(30)
                sock.connect((peer_ip, peer_port))
                
                # Enviar comando de upload
                import os
                file_size = os.path.getsize(file_path)
                
                request = {
                    'command': 'UPLOAD',
                    'filename': filename,
                    'file_size': file_size
                }
                sock.send(json.dumps(request).encode('utf-8'))
                
                # Aguardar confirmação
                response_data = sock.recv(1024).decode('utf-8')
                response = json.loads(response_data)
                
                if response.get('status') != 'ready':
                    return False, response.get('message', 'Peer não está pronto')
                
                # Enviar arquivo em blocos
                with open(file_path, 'rb') as f:
                    while True:
                        chunk = f.read(1024)
                        if not chunk:
                            break
                        sock.send(chunk)
                
                return True, "Upload concluído"
                
        except Exception as e:
            return False, str(e)
