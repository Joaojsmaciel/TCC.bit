# Funcionalidades de Gerenciamento de Peers

## 📋 Resumo das Novas Funcionalidades

Foram adicionadas funcionalidades completas de gerenciamento de peers ao sistema P2P, permitindo operações CRUD (Create, Read, Update, Delete) administrativas.

---

## 🆕 Nova Opção no Menu Principal

**Opção 8: Gerenciar Peers (Admin)**

Ao selecionar a opção 8 no menu principal da CLI, o usuário acessa um submenu dedicado ao gerenciamento de peers.

---

## 📑 Menu de Gerenciamento de Peers

```
┌─────────────────────────────────────────────────────┐
│              GERENCIAMENTO DE PEERS                 │
├─────────────────────────────────────────────────────┤
│  1. Listar todos os peers                           │
│  2. Adicionar peer manualmente                      │
│  3. Remover peer                                    │
│  4. Editar informações do peer                      │
│  5. Ver detalhes de um peer                         │
│  0. Voltar ao menu principal                        │
└─────────────────────────────────────────────────────┘
```

---

## 🔧 Funcionalidades Detalhadas

### 1. Listar Todos os Peers ✅

**Comando:** Opção 1 no submenu

**Descrição:** Exibe tabela formatada com todos os peers ativos na rede.

**Informações mostradas:**
- Peer ID
- Endereço IP
- Porta
- Índice numérico

**Exemplo de saída:**
```
┌────────────────────────────────────────────────────────────┐
│                       PEERS ATIVOS                         │
├───┬─────────────────────┬───────────────────┬──────────────┤
│ # │ Peer ID             │ Endereço          │ Porta        │
├───┼─────────────────────┼───────────────────┼──────────────┤
│  1│ peer_52d1f8ae       │ 172.18.0.3        │ 6001         │
│  2│ peer_a3b4c5d6       │ 172.18.0.4        │ 6002         │
│  3│ peer_web-ui         │ 172.18.0.8        │ 6200         │
└───┴─────────────────────┴───────────────────┴──────────────┘
```

---

### 2. Adicionar Peer Manualmente ✅

**Comando:** Opção 2 no submenu

**Descrição:** Permite adicionar um peer manualmente ao tracker (funcionalidade administrativa).

**Passos:**
1. Informar Peer ID
2. Informar IP do peer
3. Informar porta do peer
4. Sistema confirma adição

**Protocolo:** `ADD_PEER`

**Exemplo:**
```
ID do Peer: peer_novo_1234
IP do Peer: 192.168.1.100
Porta do Peer: 6005

✓ Peer peer_novo_1234 adicionado com sucesso
```

**Implementação no Tracker:**
```python
def add_peer_manual(self, request):
    peer_id = request.get('peer_id')
    ip = request.get('ip')
    port = request.get('port')
    
    self.peers[peer_id] = {
        'ip': ip,
        'port': port,
        'last_heartbeat': datetime.now()
    }
```

---

### 3. Remover Peer ✅

**Comando:** Opção 3 no submenu

**Descrição:** Remove um peer do tracker (funcionalidade administrativa).

**Passos:**
1. Informar Peer ID a remover
2. Confirmar ação
3. Sistema remove e confirma

**Protocolo:** `REMOVE_PEER`

**Exemplo:**
```
ID do Peer a remover: peer_antigo_5678

Confirma remoção do peer 'peer_antigo_5678'? (s/n): s

✓ Peer peer_antigo_5678 removido com sucesso
```

**Implementação no Tracker:**
```python
def remove_peer_admin(self, request):
    peer_id = request.get('peer_id')
    
    if peer_id in self.peers:
        del self.peers[peer_id]
        P2P_ACTIVE_PEERS.set(len(self.peers))
        return {'status': 'success'}
```

---

### 4. Editar Informações do Peer ✅

**Comando:** Opção 4 no submenu

**Descrição:** Permite alterar IP e/ou porta de um peer existente.

**Passos:**
1. Informar Peer ID a editar
2. Informar novo IP (opcional - Enter para manter)
3. Informar nova porta (opcional - Enter para manter)
4. Sistema atualiza e confirma

**Protocolo:** `EDIT_PEER`

**Exemplo:**
```
ID do Peer a editar: peer_52d1f8ae
Deixe em branco para não alterar

Novo IP (ou Enter para manter): 172.18.0.10
Nova Porta (ou Enter para manter): 

✓ Peer peer_52d1f8ae atualizado com sucesso
```

**Implementação no Tracker:**
```python
def edit_peer(self, request):
    peer_id = request.get('peer_id')
    new_ip = request.get('new_ip')
    new_port = request.get('new_port')
    
    if peer_id not in self.peers:
        return {'status': 'error', 'message': 'Peer não encontrado'}
    
    if new_ip:
        self.peers[peer_id]['ip'] = new_ip
    if new_port:
        self.peers[peer_id]['port'] = new_port
    
    self.peers[peer_id]['last_heartbeat'] = datetime.now()
```

---

### 5. Ver Detalhes de um Peer ✅

**Comando:** Opção 5 no submenu

**Descrição:** Exibe informações completas de um peer específico, incluindo lista de arquivos compartilhados.

**Passos:**
1. Informar Peer ID
2. Sistema exibe detalhes completos

**Protocolo:** `GET_PEER_DETAILS`

**Exemplo:**
```
ID do Peer: peer_52d1f8ae

┌─────────────────────────────────────────────────────┐
│              DETALHES DO PEER                       │
├─────────────────────────────────────────────────────┤
│  Peer ID: peer_52d1f8ae                             │
│  IP: 172.18.0.3                                     │
│  Porta: 6001                                        │
│  Último Heartbeat: 2026-05-06 14:32:10             │
│  Arquivos: 3                                        │
└─────────────────────────────────────────────────────┘

Arquivos (3):
  - tcc_exemplo.zip (a3f5b9c2e8d1...)
  - artigo_redes.zip (b7e2c8d9f1a3...)
  - projeto_final.zip (c9f3d1e2a4b5...)
```

**Implementação no Tracker:**
```python
def get_peer_details(self, request):
    peer_id = request.get('peer_id')
    
    peer_info = self.peers[peer_id].copy()
    peer_info['peer_id'] = peer_id
    
    # Adicionar lista de arquivos do peer
    peer_files = []
    for file_hash, file_info in self.files.items():
        if peer_id in file_info['peers']:
            peer_files.append({
                'filename': file_info['filename'],
                'hash': file_hash
            })
    
    peer_info['files'] = peer_files
    return {'status': 'success', 'peer': peer_info}
```

---

## 🔌 Novos Comandos Implementados

### Comandos Adicionados ao Tracker

| Comando | Descrição | Parâmetros |
|---------|-----------|------------|
| `ADD_PEER` | Adicionar peer manualmente | peer_id, ip, port |
| `REMOVE_PEER` | Remover peer (admin) | peer_id |
| `EDIT_PEER` | Editar informações do peer | peer_id, new_ip (opcional), new_port (opcional) |
| `GET_PEER_DETAILS` | Obter detalhes completos | peer_id |

### Métodos Adicionados ao NetworkManager

```python
def add_peer_manual(self, peer_id, ip, port)
def remove_peer_admin(self, peer_id)
def edit_peer(self, peer_id, new_ip=None, new_port=None)
def get_peer_details(self, peer_id)
```

---

## 📊 Arquivos Modificados

### 1. `peer/ui.py`
- ✅ Adicionada opção 8 no menu principal
- ✅ Novo método `print_peer_management_menu()`
- ✅ Novo método `print_peer_details(peer_info)`

### 2. `peer/network.py`
- ✅ Método `add_peer_manual()`
- ✅ Método `remove_peer_admin()`
- ✅ Método `edit_peer()`
- ✅ Método `get_peer_details()`

### 3. `tracker/tracker.py`
- ✅ Handler para comando `ADD_PEER`
- ✅ Handler para comando `REMOVE_PEER`
- ✅ Handler para comando `EDIT_PEER`
- ✅ Handler para comando `GET_PEER_DETAILS`
- ✅ Método `add_peer_manual()`
- ✅ Método `remove_peer_admin()`
- ✅ Método `edit_peer()`
- ✅ Método `get_peer_details()`

### 4. `peer/peer.py`
- ✅ Novo método `manage_peers_menu()`
- ✅ Integração no loop principal da CLI (opção 8)

---

## 🎯 Casos de Uso

### Caso de Uso 1: Adicionar Peer Offline
Um administrador pode adicionar manualmente um peer que está offline mas será iniciado posteriormente.

### Caso de Uso 2: Remover Peer Problemático
Remover peer que está causando problemas na rede sem esperar timeout de heartbeat.

### Caso de Uso 3: Atualizar Configuração de Peer
Alterar IP/porta de um peer quando a configuração de rede mudar.

### Caso de Uso 4: Auditoria
Verificar quais arquivos um peer específico está compartilhando.

### Caso de Uso 5: Monitoramento
Listar todos os peers e verificar quais estão ativos no momento.

---

## ✅ Testes Sugeridos

### Teste 1: Adicionar Peer
```bash
# 1. Acessar peer
docker exec -it p2p_peer1 python peer.py

# 2. Escolher opção 8 (Gerenciar Peers)
# 3. Escolher opção 2 (Adicionar peer)
# 4. Informar: peer_test_123, 192.168.1.50, 7000
# 5. Verificar sucesso
```

### Teste 2: Editar Peer
```bash
# 1. No menu de gerenciamento, opção 4
# 2. Informar peer_id existente
# 3. Mudar IP ou porta
# 4. Verificar atualização na listagem (opção 1)
```

### Teste 3: Ver Detalhes
```bash
# 1. Opção 5 no menu de gerenciamento
# 2. Informar peer_id de peer com arquivos
# 3. Verificar que lista de arquivos aparece
```

### Teste 4: Remover Peer
```bash
# 1. Opção 3 no menu de gerenciamento
# 2. Informar peer_id a remover
# 3. Confirmar
# 4. Verificar que não aparece mais na listagem
```

---

## 🔒 Considerações de Segurança

**Importante:** Estas funcionalidades são administrativas e devem ser usadas com cuidado:

- ⚠️ Remover peer pode causar perda de réplicas de arquivos
- ⚠️ Editar IP/porta incorretamente pode tornar peer inacessível
- ⚠️ Adicionar peer com informações incorretas pode causar erros

**Recomendação:** Em produção, estas funcionalidades deveriam ter:
- Autenticação de administrador
- Log de todas as operações
- Confirmação dupla para operações críticas

---

## 📝 Documentação Técnica

### Fluxo de Comunicação

```
PEER CLI                    NETWORK MANAGER              TRACKER
   │                              │                         │
   │  1. Escolhe opção 8          │                         │
   │──────────────────────►       │                         │
   │                              │                         │
   │  2. Escolhe opção 2          │                         │
   │  (Adicionar peer)            │                         │
   │                              │                         │
   │  3. Informa dados            │  ADD_PEER               │
   │  (id, ip, port)              ├────────────────────────►│
   │                              │                         │
   │                              │  Response (success)     │
   │                              │◄────────────────────────┤
   │                              │                         │
   │  4. Exibe confirmação        │                         │
   │◄──────────────────────       │                         │
   │  "Peer adicionado"           │                         │
```

---

## 🎉 Conclusão

O sistema agora possui gerenciamento completo de peers com:
- ✅ Listagem de peers
- ✅ Adição manual de peers
- ✅ Remoção de peers
- ✅ Edição de informações
- ✅ Visualização detalhada

Todas as funcionalidades estão integradas à CLI existente e seguem o mesmo padrão de interface do sistema.
