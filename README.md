# 📁 Sistema P2P de Compartilhamento de Arquivos

Sistema distribuído de compartilhamento de arquivos baseado em arquitetura P2P híbrida (com servidor tracker central), desenvolvido em Python com suporte completo a Docker.

---

## 📑 Índice

- [🚀 Início Rápido](#-início-rápido)
- [🔗 URLs do Sistema](#-urls-do-sistema)
- [🎯 Características](#-características)
- [🏗️ Arquitetura](#-arquitetura)
- [📂 Estrutura do Projeto](#-estrutura-do-projeto)
- [🚀 Como Executar](#-como-executar)
- [🛠️ Scripts de Gerenciamento](#-scripts-de-gerenciamento)
- [🌐 Interface Web (Hotsite)](#-interface-web-hotsite)
- [🎨 Interface Gráfica Local (GUI)](#-interface-gráfica-local-gui)
- [📖 Exemplos de Uso](#-exemplos-de-uso)
- [🧪 Testes de Tolerância a Falhas](#-testes-de-tolerância-a-falhas)
- [🔧 Comunicação](#-comunicação)
- [🔁 Sistema de Replicação](#-sistema-de-replicação)
- [📊 Monitoramento](#-monitoramento)
- [🛠️ Comandos Docker Úteis](#-comandos-docker-úteis)
- [🐛 Troubleshooting](#-troubleshooting)

---

## 🚀 Início Rápido

```bash
# 1. Iniciar o sistema completo
docker-compose up -d --build

# 2. Acessar interface web
# Abra no navegador: http://localhost:8081
```

📖 **Guia completo:** Veja [QUICKSTART.md](QUICKSTART.md) para instruções detalhadas  
🎬 **Demonstração:** Veja [APRESENTACAO.md](APRESENTACAO.md) para roteiro de apresentação

## 🔗 URLs do Sistema

Após iniciar com `docker-compose up -d --build`, acesse:

| Serviço | URL | Descrição |
|---------|-----|-----------|
| 🌐 **Hotsite** | http://localhost:8081 | Dashboard web principal |
| 🔌 **API Gateway** | http://localhost:8082/api/status | API REST do sistema |
| 📊 **Grafana** | http://localhost:3000 | Monitoramento visual (admin/admin) |
| 📈 **Prometheus** | http://localhost:9090 | Métricas do sistema |
| 📡 **Tracker** | tcp://localhost:5000 | Servidor central (TCP) |
| 👥 **Peers** | tcp://localhost:6001-6003 | Nós da rede P2P |

## 🎯 Características

- **Arquitetura P2P Híbrida**: Servidor tracker central + peers distribuídos
- **Replicação Automática**: Mínimo de 2 réplicas por arquivo para tolerância a falhas
- **Heartbeat**: Monitoramento automático de peers ativos (30 segundos)
- **Interface CLI Interativa**: Menu intuitivo com tabelas formatadas e barra de progresso
- **🎨 Interface Gráfica (GUI)**: Interface moderna com tkinter para facilitar o uso
- **🌐 Interface Web (Hotsite)**: Dashboard web completo na porta 8081 para demonstrações
- **🔌 Web Gateway API**: API REST na porta 8082 integrada ao sistema P2P
- **📊 Monitoramento**: Stack completa com Prometheus (9090) e Grafana (3000)
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
│   ├── requirements.txt
│   └── Dockerfile
├── peer/
│   ├── peer.py              # Aplicação principal do peer (CLI)
│   ├── peer_gui.py          # Ponto de entrada para GUI
│   ├── web_gateway.py       # Gateway web com API REST
│   ├── network.py           # Gerenciamento de rede
│   ├── file_manager.py      # Gerenciamento de arquivos
│   ├── heartbeat.py         # Sistema de heartbeat
│   ├── replication.py       # Lógica de replicação
│   ├── ui.py                # Interface CLI
│   ├── gui.py               # Interface Gráfica
│   └── Dockerfile
├── hotsite/
│   └── index.html           # Dashboard web de apresentação
├── config/
│   └── prometheus.yml       # Configuração do Prometheus
├── docker-compose.yml       # Orquestração de containers
├── manage.ps1               # Script de gerenciamento (Windows)
├── run_gui.ps1              # Script para executar GUI (Windows)
├── Makefile                 # Comandos make (Linux/Mac)
├── shared_files/            # Diretório compartilhado
├── APRESENTACAO.md          # Roteiro de apresentação completo
├── QUICKSTART.md            # Guia de início rápido
├── GUI_GUIDE.md             # Guia da interface gráfica
└── README.md                # Este arquivo
```

## 🚀 Como Executar

### 📌 Roteiro Completo de Apresentação

**Para demonstração do sistema completo**, veja [APRESENTACAO.md](APRESENTACAO.md) com:
- Uso do hotsite web (porta 8081)
- Gateway web API (porta 8082)
- Monitoramento com Grafana (porta 3000)
- Métricas do Prometheus (porta 9090)
- Teste E2E automatizado

### Pré-requisitos
- Docker
- Docker Compose

### Opção 1: Execução Completa com Interface Web (Recomendado)

```bash
# Na raiz do projeto
docker-compose up -d --build
```

Isso iniciará:
- **1 Tracker** (porta 5000) - Servidor central
- **3 Peers** (portas 6001, 6002, 6003) - Nós da rede
- **Web Gateway** (porta 8082) - API REST + Peer integrado (porta 6200)
- **Hotsite** (porta 8081) - Dashboard web de apresentação
- **Prometheus** (porta 9090) - Coleta de métricas
- **Grafana** (porta 3000) - Dashboards de monitoramento
- **Node Exporter** - Métricas do sistema

**Acesse:**
- 🌐 **Hotsite:** http://localhost:8081 (interface web principal)
- 📊 **Grafana:** http://localhost:3000 (usuário: admin, senha: admin)
- 📈 **Prometheus:** http://localhost:9090
- 🔌 **API Status:** http://localhost:8082/api/status

### Opção 2: Usando Scripts de Gerenciamento

**Windows (PowerShell):**
```powershell
.\manage.ps1 up
```

**Linux/Mac:**
```bash
make up
```

### Passo 2: Escolher Interface

#### A) Interface Web (Mais Fácil)

Acesse http://localhost:8081 no navegador e use o dashboard web:
- Visualize status da rede
- Publique arquivos via interface gráfica
- Busque e baixe arquivos
- Monitore peers ativos
- Acesse Grafana e Prometheus

#### B) Interface CLI (Docker)

Abra um novo terminal e acesse um peer:

```bash
# Acessar Peer 1
docker exec -it p2p_peer1 python peer.py

# Ou Peer 2
docker exec -it p2p_peer2 python peer.py

# Ou Peer 3
docker exec -it p2p_peer3 python peer.py
```

#### C) Interface Gráfica Local (GUI)

**Windows:**
```powershell
.\run_gui.ps1
```

Veja [GUI_GUIDE.md](GUI_GUIDE.md) para mais detalhes.

## 🛠️ Scripts de Gerenciamento

O sistema inclui scripts para facilitar o gerenciamento:

### Windows (PowerShell)

Use `manage.ps1` para operações comuns:

```powershell
.\manage.ps1 up          # Iniciar sistema
.\manage.ps1 down        # Parar sistema
.\manage.ps1 restart     # Reiniciar sistema
.\manage.ps1 logs        # Ver logs
.\manage.ps1 peer1       # Acessar peer1
.\manage.ps1 peer2       # Acessar peer2
.\manage.ps1 peer3       # Acessar peer3
.\manage.ps1 status      # Ver status
.\manage.ps1 clean       # Limpar containers e volumes
.\manage.ps1 rebuild     # Reconstruir tudo
.\manage.ps1 files       # Criar arquivos de teste
```

Execute GUI:
```powershell
.\run_gui.ps1           # Iniciar interface gráfica
```

### Linux/Mac (Makefile)

Use comandos `make`:

```bash
make up                 # Iniciar sistema
make down               # Parar sistema
make restart            # Reiniciar sistema
make logs               # Ver logs
make peer1              # Acessar peer1
make peer2              # Acessar peer2
make peer3              # Acessar peer3
make status             # Ver status
make clean              # Limpar containers e volumes
make rebuild            # Reconstruir tudo
make test               # Criar arquivos de teste e iniciar
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

## � Interface Web (Hotsite)

O sistema possui um **dashboard web completo** para demonstrações e uso intuitivo!

### Acessando o Hotsite

1. Inicie o sistema com Docker:
   ```bash
   docker-compose up -d --build
   ```

2. Abra no navegador: **http://localhost:8081**

### Funcionalidades do Hotsite

- ✅ **Painel de Status**: Visualize estado da rede em tempo real
- ✅ **Operações P2P**: Publique, busque e baixe arquivos
- ✅ **Monitor de Peers**: Acompanhe peers ativos
- ✅ **Integração com Grafana**: Acesso direto ao monitoramento
- ✅ **Logs em Tempo Real**: Veja operações conforme acontecem
- ✅ **API REST**: Gateway web na porta 8082

📖 **Roteiro completo:** [APRESENTACAO.md](APRESENTACAO.md)

## 🎨 Interface Gráfica Local (GUI)

Além da interface web, o sistema possui uma **interface gráfica desktop** com tkinter!

### Executando com GUI (Uso Local)

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

### Hotsite não carrega (porta 8081)
- Verifique se a porta está livre: `netstat -an | findstr 8081`
- Aguarde alguns segundos após iniciar
- Veja logs: `docker logs p2p_hotsite`

### Grafana não conecta ao Prometheus
- Aguarde ~30 segundos após iniciar o sistema
- Verifique se Prometheus está ativo: http://localhost:9090
- Veja logs: `docker logs grafana`

### API retorna erro 500
- Verifique se o tracker está ativo
- Veja logs do gateway: `docker logs p2p_web_gateway`
- Teste conexão: http://localhost:8082/api/status

## 📚 Documentação Adicional

Este projeto possui documentação completa e organizada:

| Documento | Descrição |
|-----------|-----------|
| [QUICKSTART.md](QUICKSTART.md) | **Guia de início rápido** - Comece em 2 passos |
| [APRESENTACAO.md](APRESENTACAO.md) | **Roteiro de apresentação** - Demonstração completa do sistema |
| [GUI_GUIDE.md](GUI_GUIDE.md) | **Guia da GUI** - Interface gráfica desktop com tkinter |
| [TESTE.md](TESTE.md) | **Guia de testes** - Testes detalhados de todas as funcionalidades |
| [ARQUITETURA.md](ARQUITETURA.md) | **Arquitetura** - Diagramas e detalhes técnicos |
| [CONFIGURACAO.md](CONFIGURACAO.md) | **Configuração** - Personalização e variáveis de ambiente |
| [CHANGELOG.md](CHANGELOG.md) | **Histórico** - Log de mudanças do projeto |
| [INDEX.md](INDEX.md) | **Índice** - Navegação completa da documentação |

### 🎯 Por onde começar?

1. **Primeiro uso?** → [QUICKSTART.md](QUICKSTART.md)
2. **Apresentação/Demo?** → [APRESENTACAO.md](APRESENTACAO.md)
3. **Interface gráfica?** → [GUI_GUIDE.md](GUI_GUIDE.md)
4. **Testar tudo?** → [TESTE.md](TESTE.md)
5. **Entender arquitetura?** → [ARQUITETURA.md](ARQUITETURA.md)

## 📄 Licença

Projeto educacional - Sistema P2P de Compartilhamento de Arquivos

---

**Desenvolvido com Python 3.9 e Docker** 🐍 🐳
