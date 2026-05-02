# ⚙️ Configurações do Sistema P2P

Este arquivo descreve as configurações disponíveis do sistema.

## Variáveis de Ambiente

### Tracker

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `TRACKER_HOST` | `0.0.0.0` | IP do servidor tracker |
| `TRACKER_PORT` | `5000` | Porta do servidor tracker |

### Peer

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `TRACKER_HOST` | `localhost` | Endereço do tracker para conectar |
| `TRACKER_PORT` | `5000` | Porta do tracker |
| `PEER_PORT` | `0` (automático) | Porta do servidor do peer |
| `PEER_ID` | `peer_<random>` | ID único do peer |

## Configurações do Sistema

### Heartbeat

```python
# heartbeat.py
interval = 30  # segundos entre heartbeats
```

### Timeout do Tracker

```python
# tracker.py
heartbeat_timeout = 60  # segundos até peer ser considerado inativo
```

### Replicação

```python
# replication.py
min_replicas = 2  # número mínimo de réplicas por arquivo
```

### Transferência de Arquivos

```python
# network.py
chunk_size = 1024  # tamanho do bloco de transferência em bytes
timeout = 30       # timeout de conexão em segundos
```

## Personalização via Docker Compose

Edite [docker-compose.yml](docker-compose.yml):

```yaml
services:
  tracker:
    ports:
      - "5000:5000"  # Altere a porta externa

  peer1:
    environment:
      - TRACKER_HOST=tracker
      - TRACKER_PORT=5000
      - PEER_PORT=6001      # Altere a porta
      - PEER_ID=peer1       # Altere o ID
    ports:
      - "6001:6001"         # Altere a porta externa
```

## Adicionar Mais Peers

Copie a configuração de um peer existente:

```yaml
  peer4:
    build:
      context: ./peer
      dockerfile: Dockerfile
    container_name: p2p_peer4
    environment:
      - TRACKER_HOST=tracker
      - TRACKER_PORT=5000
      - PEER_PORT=6004
      - PEER_ID=peer4
    ports:
      - "6004:6004"
    volumes:
      - ./shared_files:/app/shared_files
    networks:
      - p2p_network
    depends_on:
      - tracker
    restart: unless-stopped
    stdin_open: true
    tty: true
```

## Configurações de Rede

### Portas Usadas

- **5000**: Tracker (TCP)
- **6001-6100**: Peers (TCP)

### Rede Docker

```yaml
networks:
  p2p_network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.18.0.0/16  # Opcional: definir subnet
```

## Volumes

### Compartilhamento de Arquivos

```yaml
volumes:
  - ./shared_files:/app/shared_files  # Arquivos de entrada
  - peer1_data:/app/files_peer1       # Armazenamento do peer (opcional)
```

## Logs

### Nível de Log

Para ativar logs detalhados, modifique os arquivos Python:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Persistência de Logs

```yaml
  peer1:
    volumes:
      - ./logs:/app/logs
```

## Ajustes de Performance

### Aumentar Timeout

```python
# network.py
sock.settimeout(60)  # Aumentar de 30 para 60 segundos
```

### Aumentar Tamanho de Bloco

```python
# network.py
chunk = f.read(4096)  # Aumentar de 1024 para 4096 bytes
```

### Reduzir Intervalo de Heartbeat

```python
# heartbeat.py
interval = 15  # Reduzir de 30 para 15 segundos
```

## Modo de Desenvolvimento

Para desenvolvimento local sem Docker:

```bash
# Terminal 1 - Tracker
cd tracker
python tracker.py

# Terminal 2 - Peer 1
cd peer
export TRACKER_HOST=localhost
export TRACKER_PORT=5000
export PEER_PORT=6001
export PEER_ID=peer1
python peer.py

# Terminal 3 - Peer 2
cd peer
export TRACKER_HOST=localhost
export TRACKER_PORT=5000
export PEER_PORT=6002
export PEER_ID=peer2
python peer.py
```

## Segurança

### Adicionar Autenticação (Futuro)

```python
# tracker.py
AUTH_TOKEN = "seu_token_secreto"

def authenticate(request):
    return request.get('token') == AUTH_TOKEN
```

### Limitar Conexões

```python
# tracker.py
MAX_PEERS = 100

if len(self.peers) >= MAX_PEERS:
    return {'status': 'error', 'message': 'Limite de peers atingido'}
```

---

**Configuração do Sistema P2P v1.0**
