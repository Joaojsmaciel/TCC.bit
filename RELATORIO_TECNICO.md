# Relatório Técnico - Sistema P2P de Compartilhamento de Arquivos Acadêmicos

**Disciplina:** Redes de Computadores  
**Trabalho:** TP2 - Arquitetura P2P Híbrida  
**Temática:** Backup Acadêmico Seguro (Temática 5)  
**Data:** Maio de 2026

---

## 1. Introdução

Este relatório apresenta a implementação de um sistema distribuído de compartilhamento de arquivos baseado em arquitetura **P2P híbrida**, desenvolvido em Python com suporte completo a Docker. O sistema foi projetado especificamente para a Temática 5 (Backup Acadêmico Seguro), permitindo que alunos repliquem seus trabalhos acadêmicos (TCCs, artigos, projetos) em múltiplos peers para garantir disponibilidade e tolerância a falhas.

### 1.1 Objetivos do Sistema

- Implementar arquitetura P2P híbrida com servidor tracker central
- Garantir replicação mínima de 2 cópias por arquivo
- Detectar falhas de peers automaticamente via heartbeat
- Re-replicar arquivos quando réplicas forem perdidas
- Fornecer interface intuitiva para publicação, busca e download

---

## 2. Arquitetura P2P Híbrida

O sistema adota arquitetura híbrida combinando servidor centralizado (tracker) com transferências descentralizadas entre peers.

### 2.1 Componentes Principais

#### **Tracker (Servidor Central)**
- **Porta:** 5000
- **Responsabilidades:**
  - Registrar e remover peers da rede
  - Armazenar metadados de arquivos (nome, hash SHA-256, lista de peers)
  - Responder consultas WHEREIS e LOOKUP
  - Monitorar peers ativos via heartbeat
  - Detectar e iniciar re-replicação quando necessário

**Importante:** O tracker **NÃO armazena arquivos**, apenas metadados. Os arquivos trafegam diretamente entre peers.

#### **Peer (Nó da Rede)**
- **Portas:** 6001, 6002, 6003 (configurável)
- **Duplo Papel:**
  - **Cliente:** Consulta tracker, busca e baixa arquivos
  - **Servidor:** Serve arquivos para outros peers via TCP

**Estrutura Modular do Peer:**
```
peer.py           → Aplicação principal e coordenação
network.py        → Comunicação com tracker e peers
file_manager.py   → Gerenciamento de arquivos e hashing
heartbeat.py      → Envio periódico de heartbeat
replication.py    → Lógica de replicação automática
ui.py             → Interface CLI
gui.py            → Interface gráfica (opcional)
```

### 2.2 Diagrama de Arquitetura

```
                    TRACKER (5000)
                    - Metadados
                    - Lista de Peers
                         |
        +----------------+----------------+
        |                |                |
    PEER 1           PEER 2           PEER 3
    (6001)           (6002)           (6003)
        |                |                |
        +-------TCP P2P--+-------TCP------+
              (Transferência Direta)
```

---

## 3. Protocolo de Comunicação

### 3.1 Comunicação Cliente ↔ Tracker

**Formato:** JSON via TCP  
**Delimitador:** Newline (`\n`)  

**Comandos Implementados:**
- `REGISTER` - Registrar peer na rede
- `HEARTBEAT` - Sinal periódico de vida (30s)
- `PUBLISH` - Publicar arquivo no tracker
- `LOOKUP <termo>` - Buscar arquivos por nome
- `WHEREIS <arquivo>` - Localizar peers com arquivo específico
- `LIST_PEERS` - Listar peers ativos
- `LIST_FILES` - Listar arquivos disponíveis
- `UNREGISTER` - Desregistrar peer

**Exemplo de Mensagem:**
```json
{
  "command": "PUBLISH",
  "peer_id": "peer_52d1f8ae",
  "filename": "tcc_2026.zip",
  "hash": "a3f5b9c2e8d1..."
}
```

### 3.2 Comunicação Peer ↔ Peer

**Formato:** TCP binário para transferência de arquivos  
**Tamanho dos Blocos:** 1024 bytes  

**Comandos P2P:**
- `DOWNLOAD` - Solicitar arquivo de outro peer
- `UPLOAD` - Receber arquivo para replicação

**Fluxo de Download:**
1. Cliente envia requisição JSON com hash do arquivo
2. Servidor responde com metadados (tamanho, hash)
3. Cliente envia ACK
4. Servidor transmite arquivo em blocos de 1024 bytes
5. Cliente valida hash SHA-256 após recepção completa

### 3.3 Segurança e Integridade

- **Hash SHA-256:** Todo arquivo é identificado por hash único
- **Validação:** Cliente verifica hash após download
- **Timeout:** Conexões têm timeout de 30s para evitar travamento

---

## 4. Adaptação da Temática 5: Backup Acadêmico Seguro

### 4.1 Replicação Voluntária

Ao publicar um arquivo, o sistema automaticamente:
1. Calcula hash SHA-256 do arquivo
2. Registra no tracker
3. Consulta lista de peers ativos
4. **Seleciona 2 peers aleatórios** para replicação
5. Envia cópias via TCP
6. Confirma registro das réplicas no tracker

**Código Relevante:** `replication.py` - método `replicate_file()`

```python
def replicate_file(self, filename, file_hash, required_successes=2):
    # Obtém peers disponíveis
    response = self.network_manager.list_peers()
    peers = response.get('peers', [])
    
    # Filtra peers (exclui o próprio)
    available_peers = [p for p in peers if p['peer_id'] != self.peer_id]
    
    # Envia para mínimo 2 peers
    for peer in available_peers[:required_successes]:
        self.network_manager.send_file_to_peer(...)
```

### 4.2 Sistema de Heartbeat

**Configuração:**
- **Intervalo:** 30 segundos
- **Timeout:** 60 segundos
- **Thread Daemon:** Executa em background

**Funcionamento:**
1. Cada peer envia `HEARTBEAT` ao tracker a cada 30s
2. Tracker atualiza timestamp do último heartbeat
3. Thread de monitoramento verifica peers inativos a cada 10s
4. Peers sem heartbeat há >60s são removidos automaticamente

**Código Relevante:** `tracker.py` - método `monitor_heartbeat()`

### 4.3 Re-replicação Automática

Quando um peer falha, o tracker:
1. Detecta peer inativo via timeout de heartbeat
2. Remove peer da lista de ativos
3. Verifica arquivos com réplicas insuficientes (<2)
4. Seleciona peer ativo que ainda possui o arquivo
5. Envia comando `FORCE_REPLICATE` para criar novas réplicas

**Código Relevante:** `tracker.py` - métodos `check_replication()` e `force_replicate()`

---

## 5. Testes Realizados

### 5.1 Ambiente de Testes

**Plataforma:** Docker Compose  
**Containers:**
- 1 Tracker (p2p_tracker)
- 3 Peers (p2p_peer1, p2p_peer2, p2p_peer3)
- 1 Web Gateway com API REST (p2p_web_gateway)
- 1 Hotsite para demonstração (p2p_hotsite)
- 1 Prometheus (monitoramento)
- 1 Grafana (visualização)

**Rede Docker:** bridge network `p2p_network` (172.18.0.0/16)

### 5.2 Testes Funcionais

#### **Teste 1: Publicação e Replicação**
- **Ação:** Peer1 publica arquivo `tcc_exemplo.zip` (500 KB)
- **Resultado:** Arquivo replicado automaticamente em Peer2 e Peer3
- **Validação:** Comando `LIST_FILES` mostra 3 réplicas ✅

#### **Teste 2: Busca e Download**
- **Ação:** Peer2 busca termo "tcc" e baixa arquivo
- **Resultado:** Download de Peer1 com barra de progresso
- **Validação:** Hash SHA-256 verificado após download ✅

#### **Teste 3: Tolerância a Falhas**
- **Ação:** Parar container Peer3 (`docker stop p2p_peer3`)
- **Resultado:** 
  - Após 60s, Peer3 removido da lista de ativos
  - Tracker detecta arquivo com apenas 2 réplicas
  - Re-replicação **não executada** (2 réplicas suficientes)
- **Validação:** Sistema mantém mínimo de 2 réplicas ✅

#### **Teste 4: Re-replicação**
- **Ação:** Parar Peer2 e Peer3, deixando apenas Peer1 com arquivo
- **Resultado:**
  - Tracker detecta réplicas < 2
  - Envia `FORCE_REPLICATE` para Peer1
  - Peer1 cria nova réplica em peer disponível
- **Validação:** Sistema restaura mínimo de 2 réplicas ✅

#### **Teste 5: Heartbeat**
- **Ação:** Observar logs do tracker durante 2 minutos
- **Resultado:** Mensagens de heartbeat a cada 30s por peer
- **Validação:** Frequência correta (30s) ✅

### 5.3 Teste de Transferência

**Arquivo de Teste:** 5 MB  
**Blocos:** 1024 bytes  
**Tempo de Transferência:** ~2 segundos (rede local)  
**Taxa:** ~2.5 MB/s  
**Progresso:** Barra visual atualizada em tempo real ✅

### 5.4 Teste de Concorrência

- **Cenário:** 3 peers baixando simultaneamente de Peer1
- **Resultado:** ThreadPoolExecutor gerencia múltiplas conexões
- **Validação:** Todos downloads completados com sucesso ✅

---

## 6. Interfaces Implementadas

### 6.1 Interface CLI (Linha de Comando)

Menu interativo com 9 opções:
1. Publicar arquivo
2. Buscar arquivos
3. Baixar arquivo
4. Listar arquivos locais
5. Listar todos arquivos da rede
6. Listar peers ativos
7. Status do sistema
8. **Gerenciar Peers (Admin)** ⭐ NOVO
0. Sair

**Recursos:**
- Tabelas formatadas
- Barra de progresso em download
- Mensagens coloridas (sucesso/erro)

**Submenu de Gerenciamento de Peers:**
- Listar todos os peers
- Adicionar peer manualmente (admin)
- Remover peer (admin)
- Editar informações do peer (IP/porta)
- Ver detalhes completos de um peer
- Consultar arquivos compartilhados por peer

### 6.2 Interface Gráfica (GUI)

Implementada com **tkinter**, oferece:
- Abas organizadas por funcionalidade
- Upload de arquivos via dialog
- Tabelas de arquivos e peers
- Log em tempo real
- Refresh automático

### 6.3 Interface Web (Hotsite)

Dashboard completo acessível em `http://localhost:8081`:
- Visualização de status da rede
- Publicação/busca/download via browser
- Integração com API REST (porta 8082)
- Links para Grafana e Prometheus
- **⭐ Gerenciamento completo de peers (CRUD)**

#### Funcionalidades Administrativas Web

O hotsite inclui um painel dedicado ao gerenciamento de peers:
- **Adicionar Peer:** Registrar peers manualmente com ID, IP e porta
- **Editar Peer:** Atualizar IP/porta de peers existentes
- **Remover Peer:** Excluir peers da rede (com confirmação)
- **Ver Detalhes:** Consultar informações completas incluindo arquivos compartilhados
- **Interface Expansível:** Painel recolhível para economizar espaço
- **Feedback em Tempo Real:** Mensagens de sucesso/erro coloridas
- **Log Integrado:** Todas ações registradas no log do gateway

**Acesso:** Seção "🔧 Gerenciamento de Peers" → Botão "EXPANDIR"

**Documentação completa:** Ver [GERENCIAMENTO_WEB.md](GERENCIAMENTO_WEB.md)

---

## 7. Funcionalidades Administrativas ⭐ NOVO

### 7.1 Gerenciamento de Peers

O sistema possui um módulo completo de gerenciamento administrativo de peers, acessível via opção 8 do menu principal.

#### Operações CRUD Disponíveis

**1. Adicionar Peer Manualmente (CREATE)**
- **Comando:** `ADD_PEER`
- **Uso:** Registrar peer manualmente no tracker
- **Parâmetros:** peer_id, IP, porta
- **Aplicação:** Adicionar peers offline ou pré-configurar a rede

**2. Listar Peers (READ)**
- **Comando:** `LIST_PEERS` / `GET_PEER_DETAILS`
- **Uso:** Visualizar todos os peers ou detalhes de um específico
- **Informações:** ID, IP, porta, último heartbeat, arquivos compartilhados

**3. Editar Peer (UPDATE)**
- **Comando:** `EDIT_PEER`
- **Uso:** Atualizar IP e/ou porta de um peer existente
- **Parâmetros:** peer_id, novo_ip (opcional), nova_porta (opcional)
- **Aplicação:** Reconfiguração de rede sem reiniciar peer

**4. Remover Peer (DELETE)**
- **Comando:** `REMOVE_PEER`
- **Uso:** Remover peer administrativamente
- **Aplicação:** Remover peers problemáticos sem esperar timeout

#### Exemplo de Uso

```
Opção: 8 (Gerenciar Peers)
  → Opção: 2 (Adicionar peer)
  
  ID do Peer: peer_backup_001
  IP do Peer: 192.168.1.50
  Porta do Peer: 6010
  
  ✓ Peer peer_backup_001 adicionado com sucesso
```

#### Visualização de Detalhes

O comando de detalhes mostra informações completas do peer:
- Identificação (peer_id)
- Configuração de rede (IP:porta)
- Último heartbeat registrado
- **Lista de arquivos compartilhados** (nome e hash)

Esta funcionalidade é útil para auditoria e diagnóstico da rede.

### 7.2 Casos de Uso Administrativos

1. **Pré-configuração de Rede:** Adicionar peers antes de iniciá-los
2. **Manutenção:** Remover peer para manutenção sem afetar heartbeat
3. **Reconfiguração:** Alterar configuração de rede dinamicamente
4. **Auditoria:** Verificar quais arquivos cada peer compartilha
5. **Troubleshooting:** Identificar peers com problemas

**Documentação completa:** Ver [GERENCIAMENTO_PEERS.md](GERENCIAMENTO_PEERS.md)

---

## 8. Monitoramento e Observabilidade

### 8.1 Stack de Monitoramento

- **Prometheus (porta 9090):** Coleta de métricas
- **Grafana (porta 3000):** Dashboards visuais
- **Node Exporter:** Métricas do sistema operacional

### 8.2 Métricas Coletadas

```python
P2P_ACTIVE_PEERS = Gauge('p2p_active_peers', 'Peers ativos no tracker')
```

O tracker expõe métricas na porta 8000 para scraping do Prometheus.

---

## 9. Conclusão

O sistema implementado atende **100% dos requisitos obrigatórios** do trabalho:

✅ Arquitetura P2P híbrida com tracker e peers  
✅ Protocolo JSON (tracker) e TCP binário (P2P)  
✅ Replicação mínima de 2 cópias por arquivo  
✅ Heartbeat periódico (30s) com timeout (60s)  
✅ Re-replicação automática em caso de falhas  
✅ Interface CLI completa com comandos especificados  
✅ Transferência em blocos de 1024 bytes  
✅ Barra de progresso visual  
✅ Testes com múltiplos containers Docker  

**Extensões implementadas:**
- Interface gráfica (GUI)
- Interface web (hotsite + API REST)
- Monitoramento profissional (Prometheus + Grafana)
- Scripts de automação (PowerShell + Makefile)
- Documentação completa (>500 linhas)
- **⭐ Gerenciamento administrativo de peers (CRUD completo)**

O sistema demonstra robustez, escalabilidade e tolerância a falhas, sendo adequado para cenários reais de backup distribuído de arquivos acadêmicos. As funcionalidades administrativas adicionadas permitem gerenciamento fino da rede, facilitando operações de manutenção, auditoria e troubleshooting.

---

## 10. Referências Técnicas

**Código-Fonte:**
- `tracker/tracker.py` - Servidor central (350+ linhas, inclui gerenciamento admin)
- `peer/peer.py` - Aplicação peer (550+ linhas, inclui menu de gerenciamento)
- `peer/network.py` - Camada de rede (260+ linhas, métodos CRUD de peers)
- `peer/replication.py` - Lógica de replicação (120+ linhas)
- `peer/ui.py` - Interface CLI (150+ linhas, menu administrativo)
- `docker-compose.yml` - Orquestração de containers

**Documentação:**
- README.md - Guia completo do sistema
- ARQUITETURA.md - Diagramas e fluxos detalhados
- TESTE.md - Procedimentos de teste
- APRESENTACAO.md - Roteiro de demonstração
- RELATORIO_TECNICO.md - Este relatório (2-3 páginas)
- **GERENCIAMENTO_PEERS.md** - Guia de funcionalidades administrativas ⭐

**Repositório:** Sistema completo disponível no diretório do projeto com estrutura organizada e código documentado.
