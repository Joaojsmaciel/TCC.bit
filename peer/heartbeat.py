#!/usr/bin/env python3
"""
Heartbeat - Gerenciamento de heartbeat do Peer
Envia sinais periódicos para o tracker
"""

import threading
import time

class HeartbeatManager:
    def __init__(self, network_manager, peer_id, interval=30):
        self.network_manager = network_manager
        self.peer_id = peer_id
        self.interval = interval
        self.running = False
        self.thread = None
    
    def start(self):
        """Inicia o envio de heartbeats"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self.thread.start()
        print(f"[HEARTBEAT] Iniciado (intervalo: {self.interval}s)")
    
    def stop(self):
        """Para o envio de heartbeats"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        print("[HEARTBEAT] Parado")
    
    def _heartbeat_loop(self):
        """Loop principal de envio de heartbeats"""
        while self.running:
            try:
                response = self.network_manager.send_heartbeat(self.peer_id)
                if response.get('status') == 'success':
                    print(f"[HEARTBEAT] Enviado com sucesso")
                else:
                    print(f"[HEARTBEAT] Erro: {response.get('message', 'Desconhecido')}")
            except Exception as e:
                print(f"[HEARTBEAT] Erro ao enviar: {e}")
            
            time.sleep(self.interval)
