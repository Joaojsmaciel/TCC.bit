#!/usr/bin/env python3
"""
File Manager - Gerenciamento de arquivos do Peer
Lida com armazenamento, hashing e listagem de arquivos
"""

import os
import hashlib
import json

class FileManager:
    def __init__(self, storage_dir='./files'):
        self.storage_dir = storage_dir
        self.metadata_file = os.path.join(storage_dir, '.metadata.json')
        self.metadata = {}
        
        # Criar diretório de armazenamento se não existir
        os.makedirs(storage_dir, exist_ok=True)
        
        # Carregar metadados
        self.load_metadata()
    
    def load_metadata(self):
        """Carrega metadados dos arquivos"""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r') as f:
                    self.metadata = json.load(f)
            except:
                self.metadata = {}
        else:
            self.metadata = {}
    
    def save_metadata(self):
        """Salva metadados no arquivo"""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            print(f"[FILE_MANAGER] Erro ao salvar metadados: {e}")
    
    def calculate_hash(self, file_path):
        """Calcula o hash SHA-256 de um arquivo"""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            print(f"[FILE_MANAGER] Erro ao calcular hash: {e}")
            return None
    
    def add_file(self, source_path, filename=None):
        """Adiciona um arquivo ao armazenamento do peer"""
        if not os.path.exists(source_path):
            return False, "Arquivo não encontrado"
        
        if filename is None:
            filename = os.path.basename(source_path)
        
        dest_path = os.path.join(self.storage_dir, filename)
        
        # Copiar arquivo se não for o mesmo
        if os.path.abspath(source_path) != os.path.abspath(dest_path):
            try:
                import shutil
                shutil.copy2(source_path, dest_path)
            except Exception as e:
                return False, f"Erro ao copiar arquivo: {e}"
        
        # Calcular hash
        file_hash = self.calculate_hash(dest_path)
        if not file_hash:
            return False, "Erro ao calcular hash"
        
        # Salvar metadados
        self.metadata[filename] = {
            'hash': file_hash,
            'size': os.path.getsize(dest_path),
            'path': dest_path
        }
        self.save_metadata()
        
        return True, file_hash
    
    def get_file_path(self, filename):
        """Retorna o caminho completo de um arquivo"""
        file_path = os.path.join(self.storage_dir, filename)
        if os.path.exists(file_path):
            return file_path
        return None
    
    def has_file(self, filename):
        """Verifica se o peer tem um arquivo"""
        return filename in self.metadata and os.path.exists(self.get_file_path(filename))
    
    def get_file_info(self, filename):
        """Retorna informações sobre um arquivo"""
        if filename in self.metadata:
            return self.metadata[filename]
        return None

    def get_file_by_hash(self, file_hash):
        """Retorna (filename, info) para o hash informado."""
        for filename, info in self.metadata.items():
            if info.get('hash') == file_hash and os.path.exists(info.get('path', '')):
                return filename, info
        return None, None
    
    def list_files(self):
        """Lista todos os arquivos do peer"""
        files = []
        for filename, info in self.metadata.items():
            if os.path.exists(info['path']):
                files.append({
                    'filename': filename,
                    'hash': info['hash'],
                    'size': info['size']
                })
        return files
    
    def remove_file(self, filename):
        """Remove um arquivo do armazenamento"""
        if filename in self.metadata:
            file_path = self.metadata[filename]['path']
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                del self.metadata[filename]
                self.save_metadata()
                return True, "Arquivo removido"
            except Exception as e:
                return False, f"Erro ao remover arquivo: {e}"
        return False, "Arquivo não encontrado"
    
    def get_file_size(self, filename):
        """Retorna o tamanho de um arquivo"""
        file_path = self.get_file_path(filename)
        if file_path and os.path.exists(file_path):
            return os.path.getsize(file_path)
        return 0
    
    def verify_file_integrity(self, filename):
        """Verifica a integridade de um arquivo comparando hashes"""
        if filename not in self.metadata:
            return False
        
        file_path = self.get_file_path(filename)
        if not file_path:
            return False
        
        current_hash = self.calculate_hash(file_path)
        stored_hash = self.metadata[filename]['hash']
        
        return current_hash == stored_hash

    def verify_file_hash(self, file_path, expected_hash):
        """Verifica se o arquivo em file_path possui o hash esperado."""
        current_hash = self.calculate_hash(file_path)
        return current_hash == expected_hash, current_hash
