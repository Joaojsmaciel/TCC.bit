# Arquitetura do Sistema P2P - Diagrama Detalhado

## Visão Geral da Arquitetura

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SISTEMA P2P HÍBRIDO                               │
└─────────────────────────────────────────────────────────────────────────────┘

                                TRACKER (Servidor Central)
                    ┌───────────────────────────────────────────┐
                    │  Porta: 5000                              │
                    │  ┌─────────────────────────────────────┐  │
                    │  │  Gerenciador de Metadados           │  │
                    │  │  • Registro de Peers                │  │
                    │  │  • Hash dos Arquivos                │  │
                    │  │  • Localização (IP:Porta)           │  │
                    │  └─────────────────────────────────────┘  │
                    │  ┌─────────────────────────────────────┐  │
                    │  │  Monitor de Heartbeat               │  │
                    │  │  • Intervalo: 30s                   │  │
                    │  │  • Timeout: 60s                     │  │
                    │  │  • Auto-remoção de inativos         │  │
                    │  └─────────────────────────────────────┘  │
                    │  ┌─────────────────────────────────────┐  │
                    │  │  API de Consultas                   │  │
                    │  │  • REGISTER / UNREGISTER            │  │
                    │  │  • PUBLISH / LOOKUP / WHEREIS       │  │
                    │  │  • HEARTBEAT / LIST_PEERS/FILES     │  │
                    │  └─────────────────────────────────────┘  │
                    └─────────┬───────────┬───────────┬─────────┘
                              │           │           │
                         JSON │      JSON │      JSON │
                         TCP  │       TCP │       TCP │
                              ↓           ↓           ↓
        ┌─────────────────────────┬─────────────────────────┬─────────────────────────┐
        │                         │                         │                         │
┌───────▼─────────┐      ┌────────▼────────┐      ┌────────▼────────┐      ┌────────────────┐
│   PEER 1        │      │   PEER 2        │      │   PEER 3        │      │  PEER N...     │
│  172.18.0.3     │◄────►│  172.18.0.4     │◄────►│  172.18.0.5     │◄────►│  ...           │
│  Porta: 6001    │      │  Porta: 6002    │      │  Porta: 6003    │      │  Porta: 600N   │
└─────────────────┘      └─────────────────┘      └─────────────────┘      └────────────────┘
        │                         │                         │
        └─────────────────────────┴─────────────────────────┘
                      Transferência P2P Direta
                      (TCP Binário - Blocos 1024B)
```

## Arquitetura Interna do PEER

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            PEER (Nó P2P)                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  CLI - Interface do Usuário (ui.py)                             │  │
│  │  • Menu interativo                                               │  │
│  │  • Tabelas formatadas                                            │  │
│  │  • Barra de progresso                                            │  │
│  └────────────────────────────┬─────────────────────────────────────┘  │
│                               │                                         │
│  ┌────────────────────────────▼─────────────────────────────────────┐  │
│  │  PEER CORE (peer.py)                                            │  │
│  │  • Coordenação geral                                             │  │
│  │  • Processamento de comandos                                     │  │
│  │  • Gerenciamento de estado                                       │  │
│  └──┬────────────┬─────────────┬────────────────┬──────────────────┘  │
│     │            │             │                │                      │
│  ┌──▼──────┐  ┌─▼──────────┐ ┌▼──────────────┐ ┌▼───────────────────┐│
│  │Network  │  │File Manager│ │Heartbeat      │ │Replication         ││
│  │Manager  │  │            │ │Manager        │ │Manager             ││
│  │(network)│  │(file_mgr)  │ │(heartbeat)    │ │(replication)       ││
│  └──┬──────┘  └─┬──────────┘ └┬──────────────┘ └┬───────────────────┘│
│     │           │             │                  │                    │
│     │           │             │                  │                    │
│  ┌──▼───────────▼─────────────▼──────────────────▼──────────────────┐│
│  │  SERVIDOR DE ARQUIVOS (Thread Daemon)                            ││
│  │  • Escuta conexões de peers                                      ││
│  │  • Processa DOWNLOAD (envia arquivos)                            ││
│  │  • Processa UPLOAD (recebe réplicas)                             ││
│  │  • Multi-threaded (múltiplas conexões simultâneas)               ││
│  └──────────────────────────────────────────────────────────────────┘│
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  ARMAZENAMENTO LOCAL                                             │  │
│  │  files_<peer_id>/                                                │  │
│  │  ├── arquivo1.zip                                                │  │
│  │  ├── arquivo2.zip                                                │  │
│  │  └── .metadata.json (hash, tamanho, caminho)                     │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

## Fluxo de Publicação de Arquivo

```
PEER 1                    TRACKER                    PEER 2              PEER 3
  │                          │                          │                  │
  │ 1. PUBLISH              │                          │                  │
  ├─────────────────────────►│                          │                  │
  │    (filename, hash,      │                          │                  │
  │     peer_id)             │                          │                  │
  │                          │                          │                  │
  │ 2. Success               │                          │                  │
  │◄─────────────────────────┤                          │                  │
  │                          │                          │                  │
  │ 3. LIST_PEERS            │                          │                  │
  ├─────────────────────────►│                          │                  │
  │                          │                          │                  │
  │ 4. Lista de peers        │                          │                  │
  │◄─────────────────────────┤                          │                  │
  │                          │                          │                  │
  │ 5. UPLOAD (arquivo)                                 │                  │
  ├─────────────────────────────────────────────────────►                  │
  │                          │                          │                  │
  │ 6. Success                                          │                  │
  │◄─────────────────────────────────────────────────────                  │
  │                          │                          │                  │
  │                          │ 7. PUBLISH               │                  │
  │                          │◄─────────────────────────┤                  │
  │                          │                          │                  │
  │ 8. UPLOAD (arquivo)                                                    │
  ├────────────────────────────────────────────────────────────────────────►
  │                          │                          │                  │
  │ 9. Success                                          │                  │
  │◄────────────────────────────────────────────────────────────────────────
  │                          │                          │                  │
  │                          │                          │ 10. PUBLISH      │
  │                          │◄─────────────────────────────────────────────
  │                          │                          │                  │
  ✓ Replicação concluída     ✓ 3 réplicas registradas   ✓ Arquivo recebido✓ Arquivo recebido
    (2 réplicas enviadas)      (peer1, peer2, peer3)
```

## Fluxo de Download de Arquivo

```
PEER 2                    TRACKER                    PEER 1
  │                          │                          │
  │ 1. WHEREIS(filename)     │                          │
  ├─────────────────────────►│                          │
  │                          │                          │
  │ 2. Lista de peers        │                          │
  │    [peer1, peer3]        │                          │
  │◄─────────────────────────┤                          │
  │                          │                          │
  │ 3. Seleciona peer1       │                          │
  │                          │                          │
  │ 4. DOWNLOAD(filename)                               │
  ├─────────────────────────────────────────────────────►
  │                          │                          │
  │ 5. Arquivo (blocos)                                 │
  │◄─────────────────────────────────────────────────────
  │ [████████████░░░] 85%    │                          │
  │◄─────────────────────────────────────────────────────
  │ [████████████████] 100%  │                          │
  │                          │                          │
  │ 6. PUBLISH(filename)     │                          │
  ├─────────────────────────►│                          │
  │                          │                          │
  │ 7. Success               │                          │
  │◄─────────────────────────┤                          │
  │                          │                          │
  ✓ Download completo        ✓ peer2 registrado         ✓ Upload completo
    Arquivo salvo              Nova réplica
```

## Fluxo de Heartbeat

```
PEER 1              PEER 2              TRACKER              MONITOR
  │                    │                    │                    │
  ├─ HEARTBEAT ────────────────────────────►│                    │
  │  (a cada 30s)      │                    │                    │
  │                    ├─ HEARTBEAT ───────►│                    │
  │                    │  (a cada 30s)      │                    │
  ├─ HEARTBEAT ────────────────────────────►│                    │
  │                    │                    │                    │
  │                    ├─ HEARTBEAT ───────►│                    │
  │                    │                    │                    │
  │  X CRASH           │                    │                    │
  │  (peer1 para)      │                    │                    │
  │                    │                    │   ┌────────────────┤
  │                    │                    │   │ Verifica a     │
  │                    │                    │   │ cada 10s       │
  │                    │                    │◄──┘                │
  │                    │                    │                    │
  │                    ├─ HEARTBEAT ───────►│                    │
  │                    │                    │                    │
  │                    │                    │   ┌────────────────┤
  │                    │                    │   │ peer1:         │
  │                    │                    │   │ last_hb > 60s  │
  │                    │                    │   │ REMOVE!        │
  │                    │                    │◄──┘                │
  │                    │                    │                    │
  │                    │                    │ [ALERTA]           │
  │                    │                    │ Arquivo.zip tem    │
  │                    │                    │ apenas 2 réplicas  │
  │                    │                    │                    │
```

## Protocolo de Comunicação

### Cliente → Tracker (JSON via TCP)

```json
// REGISTER
{
  "command": "REGISTER",
  "peer_id": "peer1",
  "ip": "172.18.0.3",
  "port": 6001
}

// PUBLISH
{
  "command": "PUBLISH",
  "peer_id": "peer1",
  "filename": "arquivo.zip",
  "hash": "a3f2b8c9d1e4f5a6..."
}

// WHEREIS
{
  "command": "WHEREIS",
  "filename": "arquivo.zip"
}
```

### Peer → Peer (TCP Direto)

```
1. Handshake (JSON)
   {"command": "DOWNLOAD", "filename": "arquivo.zip"}
   
2. Resposta (JSON)
   {"status": "success", "file_size": 2621440}
   
3. Transferência (Binário)
   [1024 bytes][1024 bytes][1024 bytes]...[últimos bytes]
```

## Threads e Concorrência

```
PEER Process
│
├── Main Thread (CLI Loop)
│   └── Processa comandos do usuário
│
├── Server Thread (Daemon)
│   ├── Accept Loop
│   └── Para cada conexão:
│       └── Client Handler Thread
│           ├── DOWNLOAD → Envia arquivo
│           └── UPLOAD → Recebe arquivo
│
└── Heartbeat Thread (Daemon)
    └── Loop infinito (30s)
        └── Envia HEARTBEAT para tracker
```

---

**Documentação da Arquitetura v1.0**
