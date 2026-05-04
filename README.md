# 📁 Sistema P2P de Compartilhamento de Arquivos

Sistema distribuído de compartilhamento de arquivos baseado em arquitetura P2P híbrida (com servidor tracker central), desenvolvido em Python com suporte completo a Docker.

## 🎯 Características

- **Arquitetura P2P Híbrida**: Servidor tracker central + peers distribuídos
- **Replicação Automática**: Mínimo de 2 réplicas por arquivo para tolerância a falhas
- **Heartbeat**: Monitoramento automático de peers ativos (30 segundos)
- **Interface CLI Interativa**: Menu intuitivo com tabelas formatadas e barra de progresso
- **🎨 Interface Gráfica (GUI)**: Interface moderna com tkinter para facilitar o uso
- **Comunicação TCP**: JSON entre cliente-tracker, transferência binária entre peers
- **Concorrência**: Threading para múltiplas operações simultâneas
- **Docker**: Ambiente completo containerizado com docker-compose

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│                    TRACKER (Servidor)                   │
│  - Registro de peers                                    │
│  - Metadados de arquivos (nome, hash, peers)            │
│  - Heartbeat monitoring                                 │
│  - LOOKUP / WHEREIS                                     │
└────────────┬────────────────────────────┬───────────────┘
             │                            │
    ┌────────┴────────┐          ┌────────┴────────┐
    │   PEER 1        │◄────────►│   PEER 2        │
    │  (Client+Server)│          │  (Client+Server)│
    └─────────────────┘          └─────────────────┘
             │                            │
             └────────────┬───────────────┘
                          │
                    ┌─────┴──────┐
                    │   PEER 3   │
                    │(Client+Srv)│
                    └────────────┘
```

### Componentes

#### Tracker
- **Não armazena arquivos**, apenas metadados
- Mantém registro de peers ativos
- Responde a consultas (WHEREIS, LOOKUP)
- Remove peers inativos automaticamente
- Porta padrão: **5000**

#### Peer
Cada peer funciona como **cliente E servidor**:
- Publica arquivos no tracker
- Busca e baixa arquivos de outros peers
- Serve arquivos para outros peers
- Envia heartbeat periódico
- Gerencia replicação automática
- Portas: **6001, 6002, 6003** (configurável)

## 📂 Estrutura do Projeto

```
Sistematcc/
├── tracker/
│   ├── tracker.py           # Servidor tracker
│   └── Dockerfile
├── peer/
│   ├── peer.py              # Aplicação principal do peer
│   ├── network.py           # Gerenciamento de rede
│   ├── file_manager.py      # Gerenciamento de arquivos
│   ├── heartbeat.py         # Sistema de heartbeat
│   ├── replication.py       # Lógica de replicação
│   ├── ui.py                # Interface CLI
│   └── Dockerfile
├── docker-compose.yml       # Orquestração de containers
├── shared_files/            # Diretório compartilhado (criado automaticamente)
└── README.md
```

## 🚀 Como Executar

📌 **Roteiro de apresentação:** veja [APRESENTACAO.md](APRESENTACAO.md) para o passo a passo de uso do hotsite, gateway web, Grafana, Prometheus e teste E2E.

### Pré-requisitos
- Docker
- Docker Compose

### Passo 1: Build e Iniciar Containers

```bash
# Na raiz do projeto
docker-compose up --build
```

Isso iniciará:
- 1 Tracker (porta 5000)
- 3 Peers (portas 6001, 6002, 6003)

### Passo 2: Acessar um Peer

Abra um novo terminal e acesse um peer:

```bash
# Acessar Peer 1
docker exec -it p2p_peer1 python peer.py

# Ou Peer 2
docker exec -it p2p_peer2 python peer.py

# Ou Peer 3
docker exec -it p2p_peer3 python peer.py
```

### Passo 3: Usar a Interface

A interface CLI será exibida com o menu:

```
┌─────────────────────────────────────────────────────┐
│                  MENU PRINCIPAL                     │
├─────────────────────────────────────────────────────┤
│  1. Publicar arquivo (publish)                      │
│  2. Buscar arquivos (search)                        │
│  3. Baixar arquivo (download)                       │
│  4. Listar arquivos locais (list_local)             │
│  5. Listar todos os arquivos da rede (list_all)     │
│  6. Listar peers ativos (list_peers)                │
│  7. Status do sistema                               │
│  0. Sair (exit)                                     │
└─────────────────────────────────────────────────────┘
```

## 🎨 Interface Gráfica (GUI)

O sistema agora possui uma **interface gráfica moderna** desenvolvida com tkinter!

### Executando com GUI (Recomendado para uso local)

**Windows (PowerShell):**
```powershell
.\run_gui.ps1
```

**Manual:**
```bash
# Terminal 1: Iniciar tracker
cd tracker
python tracker.py

# Terminal 2: Iniciar peer com GUI
cd peer
python peer_gui.py
```

### Recursos da Interface Gráfica

- ✅ **Publicar arquivos** com seletor de arquivo gráfico
- ✅ **Buscar e baixar** arquivos com tabelas interativas
- ✅ **Visualizar arquivos locais** com tamanhos formatados
- ✅ **Monitorar peers ativos** em tempo real
- ✅ **Logs em tempo real** com timestamps
- ✅ **Barra de status** com estatísticas
- ✅ **Interface moderna** com tema escuro

### Screenshots da GUI

A interface possui 5 abas principais:
1. **📤 Publicar Arquivo**: Selecione e publique arquivos facilmente
2. **🔍 Buscar Arquivos**: Busque e baixe arquivos da rede
3. **💾 Arquivos Locais**: Veja seus arquivos compartilhados
4. **🌐 Peers Ativos**: Monitore peers conectados
5. **📋 Logs**: Acompanhe todas as operações

📖 **Guia completo:** Veja [GUI_GUIDE.md](GUI_GUIDE.md) para instruções detalhadas

> **Nota:** A GUI não funciona em containers Docker. Para usar com Docker, utilize a interface CLI (`python peer.py`).

## 📖 Exemplos de Uso

### 1. Publicar um Arquivo

No **Peer 1**:
```
Escolha uma opção: 1
Caminho do arquivo: /app/shared_files/meu_arquivo.zip
```

O sistema irá:
1. Calcular hash SHA-256
2. Registrar no tracker
3. Selecionar 2 peers aleatórios
4. Replicar arquivo automaticamente
5. Atualizar tracker

### 2. Buscar Arquivos

No **Peer 2**:
```
Escolha uma opção: 2
Termo de busca: arquivo
```

Exibe tabela com resultados:
```
┌────────────────────────────────────────────────────────────────┐
│                        ARQUIVOS                                │
├───┬─────────────────────────────┬──────────┬───────────────────┤
│ # │ Nome do Arquivo             │ Réplicas │ Hash (primeiros)  │
├───┼─────────────────────────────┼──────────┼───────────────────┤
│  1│ meu_arquivo.zip             │     3    │ a3f2b8c9d1e4f... │
└───┴─────────────────────────────┴──────────┴───────────────────┘
```

### 3. Baixar Arquivo

No **Peer 3**:
```
Escolha uma opção: 3
Nome do arquivo: meu_arquivo.zip
```

O sistema irá:
1. Consultar WHEREIS no tracker
2. Selecionar melhor peer
3. Baixar arquivo com barra de progresso
4. Registrar localmente
5. Publicar no tracker

Exemplo de progresso:
```
[████████████████████████████████████████] 100% (2.5 MB/2.5 MB)
✓ Arquivo 'meu_arquivo.zip' baixado com sucesso!
```

### 4. Listar Peers Ativos

```
Escolha uma opção: 6
```

Exibe:
```
┌────────────────────────────────────────────────────────────┐
│                       PEERS ATIVOS                         │
├───┬─────────────────────┬───────────────────┬──────────────┤
│ # │ Peer ID             │ Endereço          │ Porta        │
├───┼─────────────────────┼───────────────────┼──────────────┤
│  1│ peer1               │ 172.18.0.3        │ 6001         │
│  2│ peer2               │ 172.18.0.4        │ 6002         │
│  3│ peer3               │ 172.18.0.5        │ 6003         │
└───┴─────────────────────┴───────────────────┴──────────────┘
```

## 🧪 Testes de Tolerância a Falhas

### Teste 1: Peer Desconectando

1. Inicie os 3 peers
2. Publique um arquivo no Peer 1 (será replicado para 2 outros peers)
3. Pare um peer:
   ```bash
   docker stop p2p_peer2
   ```
4. Verifique que o arquivo ainda está disponível nos outros peers
5. O tracker detectará a falha em ~60 segundos (timeout de heartbeat)

### Teste 2: Re-replicação

1. Com apenas 2 peers ativos e 1 arquivo
2. Pare mais um peer:
   ```bash
   docker stop p2p_peer3
   ```
3. O tracker emitirá alerta:
   ```
   [TRACKER] ALERTA: Arquivo 'arquivo.zip' tem apenas 1 réplica(s)
   ```
4. Reinicie um peer:
   ```bash
   docker start p2p_peer2
   docker exec -it p2p_peer2 python peer.py
   ```
5. Baixe o arquivo no novo peer para criar nova réplica

### Teste 3: Download com Fallback

1. Tente baixar um arquivo
2. Se o peer selecionado falhar, o sistema tentará outro automaticamente
3. Mensagem: "Baixando de peer2 (172.18.0.4:6002)"

## 🔧 Comunicação

### Cliente ↔ Tracker (JSON via TCP)

#### Mensagens disponíveis:

**REGISTER**
```json
{
  "command": "REGISTER",
  "peer_id": "peer1",
  "ip": "172.18.0.3",
  "port": 6001
}
```

**HEARTBEAT**
```json
{
  "command": "HEARTBEAT",
  "peer_id": "peer1"
}
```

**PUBLISH**
```json
{
  "command": "PUBLISH",
  "peer_id": "peer1",
  "filename": "arquivo.zip",
  "hash": "a3f2b8c9d1e4f5a6b7c8d9e0f1a2b3c4..."
}
```

**LOOKUP**
```json
{
  "command": "LOOKUP",
  "term": "tcc"
}
```

**WHEREIS**
```json
{
  "command": "WHEREIS",
  "filename": "arquivo.zip"
}
```

### Peer ↔ Peer (TCP Direto)

**DOWNLOAD** (requisição)
```json
{
  "command": "DOWNLOAD",
  "filename": "arquivo.zip"
}
```

**UPLOAD** (replicação)
```json
{
  "command": "UPLOAD",
  "filename": "arquivo.zip",
  "file_size": 2621440
}
```

Após negociação, arquivos são transferidos em blocos de **1024 bytes**.

## 🔁 Sistema de Replicação

### Fluxo de Publicação

```
1. Peer adiciona arquivo localmente
2. Calcula hash SHA-256
3. Registra no tracker
4. Consulta peers disponíveis
5. Seleciona 2 peers aleatoriamente
6. Envia arquivo para cada peer
7. Peers receptores:
   a. Salvam arquivo
   b. Registram localmente
   c. Publicam no tracker
```

### Garantias

- **Mínimo de 2 réplicas** além do original
- Seleção aleatória de peers
- Verificação de integridade (hash)
- Re-replicação manual após falhas

## 📊 Monitoramento

### Heartbeat

- Intervalo: **30 segundos**
- Timeout: **60 segundos**
- Peers inativos removidos automaticamente
- Log no tracker:
  ```
  [TRACKER] Removendo peer inativo: peer2
  [TRACKER] ALERTA: Arquivo 'doc.zip' tem apenas 1 réplica(s)
  ```

### Logs

**Tracker:**
```
[TRACKER] Iniciado em 0.0.0.0:5000
[TRACKER] Recebido REGISTER de ('172.18.0.3', 51234)
[TRACKER] Peer registrado: peer1 (172.18.0.3:6001)
[TRACKER] Arquivo publicado: arquivo.zip por peer1
```

**Peer:**
```
[PEER] Iniciando peer peer1
[PEER] Registrado no tracker com sucesso
[PEER SERVER] Servidor escutando na porta 6001
[HEARTBEAT] Enviado com sucesso
[REPLICATION] Iniciando replicação de 'arquivo.zip'
[REPLICATION] ✓ Réplica criada em peer2
```

## 🛠️ Comandos Docker Úteis

```bash
# Ver logs do tracker
docker logs p2p_tracker

# Ver logs de um peer
docker logs p2p_peer1

# Parar todos os containers
docker-compose down

# Reiniciar um peer específico
docker restart p2p_peer2

# Remover tudo e reconstruir
docker-compose down -v
docker-compose up --build
```

## 🧹 Limpeza

```bash
# Parar e remover containers
docker-compose down

# Remover volumes (arquivos compartilhados)
docker-compose down -v

# Remover imagens construídas
docker rmi sistematcc_tracker sistematcc_peer1 sistematcc_peer2 sistematcc_peer3
```

## 📝 Notas Técnicas

### Concorrência
- **Threading** para operações simultâneas
- Heartbeat em thread daemon
- Servidor de arquivos em thread separada
- Múltiplos downloads/uploads paralelos

### Segurança
- Hash SHA-256 para verificação de integridade
- Validação de peers antes de transferência
- Timeout em conexões de rede

### Limitações
- Replicação inicial para 2 peers (mínimo)
- Re-replicação manual após falhas
- Sem criptografia de dados em trânsito
- Sem autenticação de peers

### Extensões Possíveis
- ✨ Criptografia TLS
- ✨ Autenticação de peers
- ✨ DHT (Distributed Hash Table)
- ✨ Re-replicação automática
- ✨ Balanceamento de carga
- ✨ Compressão de arquivos
- ✨ Interface Web (Flask)

## 🐛 Troubleshooting

### Erro: "Não foi possível conectar ao tracker"
- Verifique se o tracker está rodando: `docker ps`
- Aguarde alguns segundos após `docker-compose up`
- Verifique logs: `docker logs p2p_tracker`

### Erro ao baixar arquivo
- Verifique se há peers com o arquivo: opção 6 (listar peers)
- Tente outro peer
- Verifique conectividade de rede

### Peers não se comunicam
- Verifique se estão na mesma rede Docker: `docker network inspect sistematcc_p2p_network`
- Reinicie os containers

## 📄 Licença

Projeto educacional - Sistema P2P de Compartilhamento de Arquivos

---

**Desenvolvido com Python 3.9 e Docker** 🐍 🐳
