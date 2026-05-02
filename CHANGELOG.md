# 📝 Changelog

Histórico de versões e mudanças do Sistema P2P.

## [2.0.0] - 2026-05-02

### 🎨 Nova Interface Gráfica (GUI)

Adicionada interface gráfica moderna desenvolvida com tkinter para facilitar o uso do sistema.

### ✨ Novidades

#### Interface Gráfica (GUI)
- ✅ Interface moderna com tema escuro
- ✅ 5 abas principais: Publicar, Buscar, Arquivos Locais, Peers Ativos, Logs
- ✅ Seletor de arquivo gráfico para publicação
- ✅ Tabelas interativas com Treeview para:
  - Resultados de busca
  - Arquivos locais
  - Lista de peers ativos
- ✅ Logs em tempo real com timestamps
- ✅ Barra de status com estatísticas (arquivos/peers)
- ✅ Download com um clique
- ✅ Atualização automática de estatísticas
- ✅ Execução em threads separadas (não trava a interface)
- ✅ Mensagens de confirmação e erro com diálogos
- ✅ Formatação automática de tamanhos de arquivo

#### Scripts e Ferramentas
- ✅ `peer_gui.py` - Ponto de entrada para GUI
- ✅ `run_gui.ps1` - Script PowerShell para Windows
- ✅ `GUI_GUIDE.md` - Documentação completa da GUI

#### Melhorias no Código
- ✅ Método `run_gui()` adicionado à classe Peer
- ✅ Importação da GUI integrada ao peer.py
- ✅ Suporte a múltiplas interfaces (CLI e GUI)

### 📖 Documentação
- ✅ Guia completo de uso da GUI ([GUI_GUIDE.md](GUI_GUIDE.md))
- ✅ README.md atualizado com seção de GUI
- ✅ INDEX.md atualizado com novos arquivos
- ✅ Instruções de execução para Windows e Linux/Mac

### ⚠️ Notas Importantes
- A GUI **não funciona** em containers Docker (sem suporte X11/display)
- Para Docker, continue usando a interface CLI (`python peer.py`)
- Para uso local, prefira a GUI para melhor experiência

---

## [1.0.0] - 2026-05-02

### 🎉 Lançamento Inicial

Primeira versão funcional completa do Sistema P2P de Compartilhamento de Arquivos.

### ✨ Funcionalidades Implementadas

#### Tracker (Servidor Central)
- ✅ Registro e gerenciamento de peers
- ✅ Armazenamento de metadados de arquivos (nome, hash, localização)
- ✅ Sistema de heartbeat com timeout configurável (60s)
- ✅ Remoção automática de peers inativos
- ✅ Comandos: REGISTER, PUBLISH, LOOKUP, WHEREIS, HEARTBEAT
- ✅ Listagem de peers e arquivos disponíveis
- ✅ Detecção de arquivos com réplicas insuficientes

#### Peer (Cliente + Servidor)
- ✅ Registro automático no tracker
- ✅ Publicação de arquivos com hash SHA-256
- ✅ Busca de arquivos por termo
- ✅ Download de arquivos com barra de progresso
- ✅ Upload de arquivos (servidor)
- ✅ Heartbeat automático a cada 30 segundos
- ✅ Replicação automática (mínimo 2 cópias)
- ✅ Seleção aleatória de peers para replicação
- ✅ Interface CLI interativa com menu
- ✅ Verificação de integridade de arquivos (hash)

#### Interface CLI
- ✅ Menu interativo com 8 opções
- ✅ Tabelas formatadas para arquivos e peers
- ✅ Barra de progresso em downloads
- ✅ Feedback visual (✓, ✗, ℹ)
- ✅ Confirmação de ações críticas

#### Docker
- ✅ Dockerfile para tracker
- ✅ Dockerfile para peer
- ✅ docker-compose.yml com 1 tracker + 3 peers
- ✅ Rede bridge isolada
- ✅ Volumes compartilhados para arquivos
- ✅ Variáveis de ambiente configuráveis
- ✅ Restart automático de containers

#### Comunicação
- ✅ JSON via TCP (cliente ↔ tracker)
- ✅ TCP direto binário (peer ↔ peer)
- ✅ Transferência em blocos de 1024 bytes
- ✅ Timeouts configuráveis
- ✅ Tratamento de erros de rede

#### Replicação e Tolerância a Falhas
- ✅ Mínimo 2 réplicas por arquivo
- ✅ Seleção aleatória de peers
- ✅ Re-replicação manual disponível
- ✅ Detecção de peers inativos
- ✅ Fallback automático em caso de falha de download
- ✅ Alertas de réplicas insuficientes

### 📚 Documentação Criada

- ✅ README.md - Documentação completa
- ✅ QUICKSTART.md - Guia de início rápido
- ✅ TESTE.md - Guia de testes detalhado
- ✅ ARQUITETURA.md - Diagramas e arquitetura
- ✅ CONFIGURACAO.md - Configurações
- ✅ INDEX.md - Índice do projeto
- ✅ CHANGELOG.md - Este arquivo

### 🛠️ Scripts e Utilitários

- ✅ manage.ps1 - Script PowerShell para Windows
- ✅ Makefile - Comandos make para Linux/Mac
- ✅ create_test_files.ps1 - Criar arquivos teste (Windows)
- ✅ create_test_files.sh - Criar arquivos teste (Linux/Mac)
- ✅ .gitignore - Arquivos ignorados

### 🧪 Testes

- ✅ Teste de publicação e replicação
- ✅ Teste de busca e download
- ✅ Teste de listagem (peers, arquivos)
- ✅ Teste de tolerância a falhas
- ✅ Teste de heartbeat
- ✅ Teste de múltiplos downloads
- ✅ Teste de peer desconectando

### 📊 Métricas

- **Linhas de código**: ~2000+
- **Arquivos Python**: 7
- **Containers**: 4 (1 tracker + 3 peers)
- **Protocolos**: 2 (JSON/TCP, TCP binário)
- **Comandos CLI**: 8
- **Comandos de gerenciamento**: 15+

### 🔧 Tecnologias

- Python 3.9
- Docker
- Docker Compose
- Socket Programming (TCP)
- Threading
- JSON
- SHA-256 Hashing

---

## 🚀 Próximas Versões (Planejado)

### [1.1.0] - Planejado

#### Melhorias
- [ ] Re-replicação automática ao detectar falhas
- [ ] Logs estruturados com níveis (DEBUG, INFO, WARNING, ERROR)
- [ ] Persistência de metadados do tracker em JSON
- [ ] Estatísticas de uso (uploads, downloads, peers)

### [1.2.0] - Planejado

#### Novas Funcionalidades
- [ ] Interface web com Flask
- [ ] Compressão de arquivos durante transferência
- [ ] Cache de arquivos frequentes
- [ ] Priorização de downloads

### [2.0.0] - Planejado

#### Grandes Mudanças
- [ ] Criptografia TLS em comunicações
- [ ] Autenticação de peers com tokens
- [ ] DHT (Distributed Hash Table)
- [ ] Remoção do tracker (P2P puro)
- [ ] Descoberta automática de peers (multicast)

---

## 📝 Formato do Changelog

Este changelog segue o formato [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

### Tipos de Mudanças

- **✨ Added** - Novas funcionalidades
- **🔧 Changed** - Mudanças em funcionalidades existentes
- **⚠️ Deprecated** - Funcionalidades que serão removidas
- **🗑️ Removed** - Funcionalidades removidas
- **🐛 Fixed** - Correções de bugs
- **🔒 Security** - Correções de segurança

---

**Versão atual: 1.0.0**  
**Data: 02 de Maio de 2026**
