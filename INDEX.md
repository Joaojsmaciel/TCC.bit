# 📑 Índice do Projeto - Sistema P2P

Guia de navegação de todos os arquivos e documentação do projeto.

## 📂 Estrutura Completa

```
Sistematcc/
│
├── 📚 DOCUMENTAÇÃO
│   ├── README.md              → Documentação principal completa
│   ├── QUICKSTART.md          → Guia de início rápido (3 passos)
│   ├── GUI_GUIDE.md           → Guia completo da Interface Gráfica
│   ├── TESTE.md               → Guia detalhado de testes
│   ├── ARQUITETURA.md         → Diagramas e arquitetura do sistema
│   ├── CONFIGURACAO.md        → Configurações e personalização
│   ├── CHANGELOG.md           → Histórico de mudanças
│   └── INDEX.md               → Este arquivo (índice)
│
├── 🐳 DOCKER
│   ├── docker-compose.yml     → Orquestração de containers
│   ├── tracker/
│   │   └── Dockerfile         → Imagem do tracker
│   └── peer/
│       └── Dockerfile         → Imagem do peer
│
├── 🖥️ CÓDIGO FONTE
│   ├── tracker/
│   │   └── tracker.py         → Servidor tracker central
│   └── peer/
│       ├── peer.py            → Aplicação principal do peer
│       ├── peer_gui.py        → Ponto de entrada para GUI
│       ├── network.py         → Gerenciamento de rede
│       ├── file_manager.py    → Gerenciamento de arquivos
│       ├── heartbeat.py       → Sistema de heartbeat
│       ├── replication.py     → Lógica de replicação
│       ├── ui.py              → Interface CLI
│       └── gui.py             → Interface Gráfica (GUI)
│
├── 🛠️ run_gui.ps1            → Script para iniciar GUI (Windows)
│   ├── SCRIPTS E UTILITÁRIOS
│   ├── manage.ps1             → Script de gerenciamento (Windows)
│   ├── Makefile               → Comandos make (Linux/Mac)
│   ├── create_test_files.ps1  → Criar arquivos teste (Windows)
│   └── create_test_files.sh   → Criar arquivos teste (Linux/Mac)
│
└── ⚙️ CONFIGURAÇÃO
    └── .gitignore             → Arquivos ignorados pelo Git
```

## 📖 Documentação

### README.md
**O que é**: Documentação principal e completa do projeto  
**Quando usar**: Primeira leitura, referência completa  
**Conteúdo**:
- Características do sistema
- Arquitetura resumida
- Estrutura do projeto
- Como executar
- Exemplos de uso
- Comunicação (protocolos)
- Troubleshooting

### QUICKSTART.md
**O que é**: Guia de início rápido  
**Quando usar**: Primeira vez usando o sistema  
**Conteúdo**:
- 3 passos para começar
- Comandos essenciais
- Exemplo prático
- Fluxo de trabalho
- Teste rápido de falha

### GUI_GUIDE.md
**O que é**: Guia completo da Interface Gráfica  
**Quando usar**: Para usar o sistema com interface visual  
**Conteúdo**:
- Como executar com GUI
- Funcionalidades de cada aba
- Dicas de uso
- Solução de problemas
- Comparação CLI vs GUI
- Configurações avançadas

### TESTE.md
**O que é**: Guia completo de testes  
**Quando usar**: Para testar todas as funcionalidades  
**Conteúdo**:
- Teste de publicação e replicação
- Teste de busca e download
- Teste de listagem
- Teste de tolerância a falhas
- Teste de heartbeat
- Checklist de funcionalidades

### ARQUITETURA.md
**O que é**: Diagramas e detalhes da arquitetura  
**Quando usar**: Entender como o sistema funciona internamente  
**Conteúdo**:
- Diagrama da arquitetura geral
- Arquitetura interna do peer
- Fluxo de publicação
- Fluxo de download
- Fluxo de heartbeat
- Protocolo de comunicação
- Threads e concorrência

### CONFIGURACAO.md
**O que é**: Guia de configuração e personalização  
**Quando usar**: Para personalizar o sistema  
**Conteúdo**:
- Variáveis de ambiente
- Configurações do sistema
- Personalização via Docker Compose
- Adicionar mais peers
- Ajustes de performance
- Modo de desenvolvimento

## 🖥️ Código Fonte

### tracker/tracker.py
**Responsabilidade**: Servidor central de metadados  
**Classes**: `Tracker`  
**Principais métodos**:
- `start()` - Inicia servidor
- `register_peer()` - Registra peer
- `publish_file()` - Registra arquivo
- `lookup_file()` - Busca arquivos
- `whereis()` - Localiza peers com arquivo
- `monitor_heartbeat()` - Monitora peers inativos

### peer/peer.py
**Responsabilidade**: Aplicação principal do peer  
**Classes**: `Peer`  
**Principais métodos**:
- `start()` - Inicia peer
- `run_server()` - Servidor de arquivos
- `publish_file()` - Publica arquivo
- `search_files()` - Busca arquivos
- `download_file()` - Baixa arquivo
- `run_cli()` - Interface CLI

### peer/network.py
**Responsabilidade**: Comunicação de rede  
**Classes**: `NetworkManager`  
**Principais métodos**:
- `send_to_tracker()` - Envia mensagem ao tracker
- `register_peer()` - Registra no tracker
- `download_file_from_peer()` - Baixa arquivo
- `send_file_to_peer()` - Envia arquivo

### peer/file_manager.py
**Responsabilidade**: Gerenciamento de arquivos  
**Classes**: `FileManager`  
**Principais métodos**:
- `add_file()` - Adiciona arquivo
- `calculate_hash()` - Calcula SHA-256
- `list_files()` - Lista arquivos
- `verify_file_integrity()` - Verifica integridade

### peer/heartbeat.py
**Responsabilidade**: Sistema de heartbeat  
**Classes**: `HeartbeatManager`  
**Principais métodos**:
- `start()` - Inicia heartbeat
- `_heartbeat_loop()` - Loop de envio

### peer/replication.py
**Responsabilidade**: Replicação de arquivos  
**Classes**: `ReplicationManager`  
**Principais métodos**:
- `replicate_file()` - Replica arquivo
- `check_file_replication()` - Verifica réplicas
- `get_best_peer_for_download()` - Seleciona peer

### peer/ui.py
**Responsabilidade**: Interface de linha de comando  
**Classes**: `CLI`  
**Principais métodos**:
- `print_menu()` - Exibe menu
- `print_files_table()` - Tabela de arquivos
- `print_peers_table()` - Tabela de peers
- `print_progress_bar()` - Barra de progresso

## 🐳 Docker

### docker-compose.yml
**Responsabilidade**: Orquestração de containers  
**Serviços**:
- `tracker` - Servidor tracker (porta 5000)
- `peer1` - Peer 1 (porta 6001)
- `peer2` - Peer 2 (porta 6002)
- `peer3` - Peer 3 (porta 6003)

### tracker/Dockerfile
**Responsabilidade**: Imagem Docker do tracker  
**Base**: Python 3.9-slim  
**Expõe**: Porta 5000

### peer/Dockerfile
**Responsabilidade**: Imagem Docker do peer  
**Base**: Python 3.9-slim  
**Expõe**: Portas 6000-6100

## 🛠️ Scripts

### manage.ps1 (Windows)
**Responsabilidade**: Gerenciamento do sistema no Windows  
**Comandos principais**:
- `.\manage.ps1 up` - Iniciar sistema
- `.\manage.ps1 peer1` - Acessar peer1
- `.\manage.ps1 files` - Criar arquivos teste
- `.\manage.ps1 clean` - Limpar sistema

### Makefile (Linux/Mac)
**Responsabilidade**: Gerenciamento do sistema no Linux/Mac  
**Comandos principais**:
- `make up` - Iniciar sistema
- `make peer1` - Acessar peer1
- `make files` - Criar arquivos teste
- `make clean` - Limpar sistema

### create_test_files.ps1 / .sh
**Responsabilidade**: Criar arquivos de teste  
**Cria**:
- tcc_sistemas_distribuidos.zip
- artigo_redes.zip
- tcc_seguranca.zip
- artigo_cloud.zip
- trabalho_bd.zip

## 🚀 Fluxo de Leitura Recomendado

### Para Usuários Novos:
1. **README.md** - Entender o que é o projeto
2. **QUICKSTART.md** - Começar rapidamente
3. **TESTE.md** - Testar funcionalidades

### Para Desenvolvedores:
1. **README.md** - Visão geral
2. **ARQUITETURA.md** - Entender estrutura
3. **Código fonte** - Explorar implementação
4. **CONFIGURACAO.md** - Personalizar

### Para Deploy/Produção:
1. **README.md** - Configuração básica
2. **CONFIGURACAO.md** - Personalização
3. **docker-compose.yml** - Ajustes de deploy

## 🔗 Links Rápidos

| Preciso... | Arquivo |
|------------|---------|
| Começar rapidamente | [QUICKSTART.md](QUICKSTART.md) |
| Entender arquitetura | [ARQUITETURA.md](ARQUITETURA.md) |
| Testar o sistema | [TESTE.md](TESTE.md) |
| Configurar | [CONFIGURACAO.md](CONFIGURACAO.md) |
| Referência completa | [README.md](README.md) |
| Executar comandos | [manage.ps1](manage.ps1) ou [Makefile](Makefile) |

## 📊 Estatísticas do Projeto

- **Arquivos Python**: 7
- **Linhas de código**: ~2000+
- **Arquivos de documentação**: 6
- **Scripts auxiliares**: 4
- **Containers Docker**: 4 (1 tracker + 3 peers)

---

**Sistema P2P de Compartilhamento de Arquivos - v1.0**
