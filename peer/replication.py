#!/usr/bin/env python3
"""
Replication - Gerenciamento de replicação de arquivos
Garante que arquivos tenham pelo menos 2 réplicas
"""

import random

class ReplicationManager:
    def __init__(self, network_manager, file_manager, peer_id):
        self.network_manager = network_manager
        self.file_manager = file_manager
        self.peer_id = peer_id
        self.min_replicas = 2
    
    def replicate_file(self, filename, file_hash):
        """
        Replica um arquivo para outros peers
        Garante que haja pelo menos 2 réplicas (além do original)
        """
        print(f"[REPLICATION] Iniciando replicação de '{filename}'")
        
        # Obter lista de peers disponíveis
        response = self.network_manager.list_peers()
        if response.get('status') != 'success':
            print(f"[REPLICATION] Erro ao obter lista de peers")
            return False
        
        peers = response.get('peers', [])
        
        # Filtrar peers (excluir a si mesmo)
        available_peers = [p for p in peers if p['peer_id'] != self.peer_id]
        
        if len(available_peers) < self.min_replicas:
            print(f"[REPLICATION] AVISO: Apenas {len(available_peers)} peer(s) disponível(is). Ideal: {self.min_replicas}")
        
        # Selecionar peers aleatoriamente para replicação
        num_replicas = min(self.min_replicas, len(available_peers))
        selected_peers = random.sample(available_peers, num_replicas) if available_peers else []
        
        file_path = self.file_manager.get_file_path(filename)
        if not file_path:
            print(f"[REPLICATION] Erro: arquivo '{filename}' não encontrado localmente")
            return False
        
        success_count = 0
        
        for peer in selected_peers:
            peer_ip = peer['ip']
            peer_port = peer['port']
            peer_id = peer['peer_id']
            
            print(f"[REPLICATION] Enviando para {peer_id} ({peer_ip}:{peer_port})")
            
            success, message = self.network_manager.send_file_to_peer(
                peer_ip, peer_port, filename, file_path
            )
            
            if success:
                print(f"[REPLICATION] ✓ Réplica criada em {peer_id}")
                
                # Notificar o tracker que o peer agora tem o arquivo
                # (isso seria feito pelo peer receptor ao receber o arquivo)
                success_count += 1
            else:
                print(f"[REPLICATION] ✗ Falha ao enviar para {peer_id}: {message}")
        
        print(f"[REPLICATION] Concluído: {success_count}/{num_replicas} réplicas criadas")
        
        return success_count > 0
    
    def check_file_replication(self, filename):
        """
        Verifica se um arquivo tem réplicas suficientes
        Retorna (tem_replicas_suficientes, numero_de_replicas)
        """
        response = self.network_manager.whereis_file(filename)
        
        if response.get('status') != 'success':
            return False, 0
        
        peers = response.get('peers', [])
        num_replicas = len(peers)
        
        return num_replicas >= self.min_replicas, num_replicas
    
    def get_best_peer_for_download(self, peers):
        """
        Seleciona o melhor peer para download
        Por simplicidade, seleciona aleatoriamente
        """
        if not peers:
            return None
        
        # Poderia implementar lógica mais sofisticada aqui
        # (ex: ping, latência, carga do peer, etc.)
        return random.choice(peers)
    
    def replicate_if_needed(self, filename):
        """
        Verifica e replica um arquivo se necessário
        """
        has_enough, count = self.check_file_replication(filename)
        
        if not has_enough:
            print(f"[REPLICATION] Arquivo '{filename}' tem apenas {count} réplica(s)")
            file_info = self.file_manager.get_file_info(filename)
            if file_info:
                return self.replicate_file(filename, file_info['hash'])
        
        return True
