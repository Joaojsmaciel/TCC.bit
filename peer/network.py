#!/usr/bin/env python3
"""
Network - Módulo de comunicação de rede para o Peer
Gerencia conexões com o tracker e outros peers
"""

import socket
import json
import os

class NetworkManager:
    def __init__(self, tracker_host, tracker_port):
        self.tracker_host = tracker_host
        self.tracker_port = tracker_port
    
    @staticmethod
    def send_json(sock, message):
        """Envia uma mensagem JSON delimitada por newline."""
        payload = json.dumps(message).encode('utf-8') + b'\n'
        sock.sendall(payload)

    @staticmethod
    def recv_json(sock):
        """Le uma mensagem JSON delimitada por newline."""
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

    @staticmethod
    def recv_exact_to_file(sock, file_path, file_size, progress_callback=None):
        """Recebe exatamente file_size bytes e grava em disco."""
        received = 0
        with open(file_path, 'wb') as f:
            while received < file_size:
                chunk_size = min(4096, file_size - received)
                chunk = sock.recv(chunk_size)
                if not chunk:
                    break
                f.write(chunk)
                received += len(chunk)

                if progress_callback:
                    progress_callback(received, file_size)

        return received

    def send_to_tracker(self, message):
        """Envia uma mensagem JSON para o tracker e retorna a resposta"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(10)
                sock.connect((self.tracker_host, self.tracker_port))
                self.send_json(sock, message)
                return self.recv_json(sock)
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
            'command': 'LIST',
            'target': 'peers'
        }
        return self.send_to_tracker(message)
    
    def list_files(self):
        """Lista todos os arquivos registrados"""
        message = {
            'command': 'LIST',
            'target': 'files'
        }
        return self.send_to_tracker(message)
    
    def unregister_peer(self, peer_id):
        """Remove o peer do tracker"""
        message = {
            'command': 'UNREGISTER',
            'peer_id': peer_id
        }
        return self.send_to_tracker(message)
    
    def download_file_from_peer(self, peer_ip, peer_port, file_hash, save_path, filename=None, progress_callback=None):
        """Baixa um arquivo de outro peer"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(30)
                sock.connect((peer_ip, peer_port))
                
                # Solicitar arquivo
                request = {
                    'command': 'DOWNLOAD',
                    'hash': file_hash,
                    'filename': filename
                }
                self.send_json(sock, request)
                
                # Receber resposta
                response = self.recv_json(sock)
                
                if response.get('status') != 'success':
                    return False, response.get('message', 'Erro desconhecido')
                
                file_size = response.get('file_size', 0)
                expected_hash = response.get('hash')

                self.send_json(sock, {'status': 'ack'})
                
                # Receber arquivo em blocos
                received = self.recv_exact_to_file(sock, save_path, file_size, progress_callback)

                if received != file_size:
                    return False, f"Download incompleto: {received}/{file_size} bytes"

                if expected_hash and expected_hash != file_hash:
                    return False, "Hash informado pelo peer nao confere com o tracker"
                
                return True, "Download concluído"
                
        except Exception as e:
            return False, str(e)
    
    def send_file_to_peer(self, peer_ip, peer_port, filename, file_path, file_hash=None):
        """Envia um arquivo para outro peer (para replicação)"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(30)
                sock.connect((peer_ip, peer_port))
                
                # Enviar comando de upload
                file_size = os.path.getsize(file_path)
                
                request = {
                    'command': 'UPLOAD',
                    'filename': filename,
                    'file_size': file_size,
                    'hash': file_hash
                }
                self.send_json(sock, request)
                
                # Aguardar confirmação
                response = self.recv_json(sock)
                
                if response.get('status') != 'ready':
                    return False, response.get('message', 'Peer não está pronto')
                
                # Enviar arquivo em blocos
                with open(file_path, 'rb') as f:
                    while True:
                        chunk = f.read(4096)
                        if not chunk:
                            break
                        sock.sendall(chunk)

                final_response = self.recv_json(sock)
                if final_response.get('status') != 'success':
                    return False, final_response.get('message', 'Upload nao confirmado')
                
                return True, "Upload concluído"
                
        except Exception as e:
            return False, str(e)
