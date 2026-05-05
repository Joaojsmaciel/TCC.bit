# 🚀 Guia de Início Rápido

## ⚡ Começar em 2 Passos

### 1️⃣ Iniciar o Sistema

```bash
docker-compose up -d --build
```

Aguarde até ver todos os serviços ativos:
```bash
docker-compose ps
```

Serviços iniciados:
- ✅ **p2p_tracker** - Servidor central (porta 5000)
- ✅ **p2p_peer1, p2p_peer2, p2p_peer3** - Nós da rede (6001-6003)
- ✅ **p2p_web_gateway** - API REST (porta 8082)
- ✅ **p2p_hotsite** - Dashboard web (porta 8081)
- ✅ **prometheus** - Métricas (porta 9090)
- ✅ **grafana** - Monitoramento (porta 3000)
- ✅ **node_exporter** - Métricas do sistema

### 2️⃣ Escolher Interface

#### 🌐 Opção A: Interface Web (Mais Fácil - Recomendado)

Abra no navegador: **http://localhost:8081**

**Vantagens:**
- ✅ Interface intuitiva e visual
- ✅ Não precisa de comandos Docker
- ✅ Acesso direto ao Grafana e Prometheus
- ✅ Logs em tempo real
- ✅ Upload de arquivos via formulário

**Como usar:**
1. Clique em **STATUS** para ver estado da rede
2. Use **PUBLISH** para publicar arquivos
3. Use **SEARCH** para buscar arquivos
4. Use **DOWNLOAD** para baixar arquivos
5. Veja **LIST_PEERS** para peers ativos
6. Acesse **Grafana** para monitoramento visual

📖 **Guia completo:** [APRESENTACAO.md](APRESENTACAO.md)

#### 💻 Opção B: Interface CLI (Docker)

**Em um novo terminal:**

```bash
docker exec -it p2p_peer1 python peer.py
```

## 📋 Comandos Essenciais

| Opção | Comando | Descrição |
|-------|---------|-----------|
| 1 | Publicar | Adiciona arquivo à rede com replicação |
| 2 | Buscar | Procura arquivos pelo nome |
| 3 | Download | Baixa arquivo de outro peer |
| 4 | Listar Local | Mostra seus arquivos |
| 5 | Listar Rede | Mostra todos os arquivos disponíveis |
| 6 | Listar Peers | Mostra peers ativos |
| 0 | Sair | Encerra o peer |

## 🎬 Exemplo Prático Completo

### Cenário: Compartilhar um TCC

#### Via Interface Web (http://localhost:8081)

**1. Publicar arquivo:**
- Clique em **PUBLISH**
- Selecione arquivo (ou use caminho `/app/shared_files/arquivo.zip`)
- Veja confirmação de réplicas criadas

**2. Buscar arquivo:**
- Clique em **SEARCH**
- Digite termo (ex: "tcc")
- Veja resultados com quantidade de réplicas

**3. Baixar arquivo:**
- Clique em **DOWNLOAD**
- Digite nome do arquivo
- Veja progresso do download

**4. Monitorar:**
- Clique em **Abrir Grafana**
- Veja métricas em tempo real
- Observe uso de rede e peers ativos

#### Via CLI (Docker)

**Peer 1 (Publicar):**
```
Escolha uma opção: 1
Caminho do arquivo: /app/shared_files/tcc_sistemas_distribuidos.zip
✓ Arquivo 'tcc_sistemas_distribuidos.zip' publicado
[REPLICATION] Réplica criada em peer2
[REPLICATION] Réplica criada em peer3
```

**Peer 2 (Buscar e Baixar):**
```
Escolha uma opção: 2
Termo de busca: tcc

┌───┬─────────────────────────────┬──────────┬───────────────────┐
│ # │ Nome do Arquivo             │ Réplicas │ Hash (primeiros)  │
├───┼─────────────────────────────┼──────────┼───────────────────┤
│  1│ tcc_sistemas_distribuidos...│     3    │ a3f2b8c9d1e4f... │
└───┴─────────────────────────────┴──────────┴───────────────────┘

Escolha uma opção: 3
Nome do arquivo: tcc_sistemas_distribuidos.zip
[████████████████████████████████████████] 100%
✓ Arquivo baixado com sucesso!
```

## � Monitoramento em Tempo Real

### Grafana (Dashboard Visual)

**Acesso:** http://localhost:3000  
**Login:** admin / admin

**O que ver:**
- Número de peers ativos
- Arquivos publicados
- Transferências em andamento
- Uso de CPU/memória
- Métricas de rede

### Prometheus (Métricas Brutas)

**Acesso:** http://localhost:9090

**Consultas úteis:**
```
# Número de peers ativos
p2p_peers_active

# Arquivos na rede
p2p_files_total

# Uso de CPU
rate(node_cpu_seconds_total[5m])
```

### API REST (Programação)

**Base URL:** http://localhost:8082/api

**Endpoints:**
- `GET /status` - Status do sistema
- `GET /peers` - Lista de peers
- `GET /files` - Arquivos disponíveis
- `POST /publish` - Publicar arquivo
- `GET /search?term=arquivo` - Buscar arquivos

## 📁 Criar Arquivos de Teste

**Windows (PowerShell):**
```powershell
.\create_test_files.ps1
```

**Linux/Mac:**
```bash
chmod +x create_test_files.sh
./create_test_files.sh
```

Cria arquivos de exemplo em `shared_files/` para testar o sistema.

## 🔄 Fluxo Completo de Trabalho

```
┌─────────────────────────────────────────────────────────────┐
│ 1. PREPARAÇÃO                                               │
│    • docker-compose up -d --build                           │
│    • Acessar http://localhost:8081                          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. ESCOLHER INTERFACE                                      │
│    🌐 Web: http://localhost:8081 (recomendado)          │
│    💻 CLI: docker exec -it p2p_peer1 python peer.py    │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. PUBLICAR ARQUIVO                                        │
│    • Via web: botão PUBLISH                               │
│    • Via CLI: opção 1                                     │
│    • Sistema replica automaticamente em 2 peers          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. BUSCAR E BAIXAR                                         │
│    • Buscar: botão SEARCH ou opção 2                     │
│    • Baixar: botão DOWNLOAD ou opção 3                   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. MONITORAR                                               │
│    • Grafana: http://localhost:3000                        │
│    • Prometheus: http://localhost:9090                     │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 Fluxo Completo de Trabalho (Antigo)

```
┌─────────────────────────────────────────────────────────────┐
│ 1. PREPARAÇÃO                                               │
│    • Criar arquivos de teste                                │
│    • Iniciar docker-compose                                 │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. PUBLICAÇÃO (Peer 1)                                      │
│    • Acessar peer: docker exec -it p2p_peer1 python peer.py│
│    • Opção 1: Publicar arquivo                              │
│    • Sistema replica automaticamente                        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. DESCOBERTA (Peer 2)                                      │
│    • Acessar peer: docker exec -it p2p_peer2 python peer.py│
│    • Opção 2: Buscar arquivos                               │
│    • Ver lista de resultados                                │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. DOWNLOAD (Peer 2)                                        │
│    • Opção 3: Baixar arquivo                                │
│    • Sistema seleciona melhor peer                          │
│    • Download com barra de progresso                        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. VERIFICAÇÃO                                              │
│    • Opção 4: Ver arquivos locais                           │
│    • Opção 5: Ver status da rede                            │
│    • Opção 6: Ver peers ativos                              │
└─────────────────────────────────────────────────────────────┘
```

## 🔗 URLs Importantes

Após iniciar o sistema, acesse:

| Serviço | URL | Descrição |
|---------|-----|-----------|
| 🌐 **Hotsite** | http://localhost:8081 | Dashboard web principal |
| 🔌 **API Gateway** | http://localhost:8082/api/status | API REST do sistema |
| 📊 **Grafana** | http://localhost:3000 | Monitoramento visual (admin/admin) |
| 📈 **Prometheus** | http://localhost:9090 | Métricas do sistema |
| 📡 **Tracker** | tcp://localhost:5000 | Servidor central (TCP) |

## 🧪 Teste Rápido de Falha

### Opção A: Via Interface Web

1. Acesse http://localhost:8081
2. Clique em **LIST_PEERS** - veja 4 peers ativos (peer1, peer2, peer3, web-ui)
3. Em outro terminal: `docker stop p2p_peer3`
4. Aguarde ~60 segundos
5. Clique em **LIST_PEERS** novamente - peer3 não aparecerá mais
6. Veja logs no hotsite indicando a remoção

### Opção B: Via CLI

**Terminal 1:**
```bash
docker stop p2p_peer3
```

**Terminal 2 (no Peer 2):**
```
Escolha uma opção: 6  # Listar peers

# peer3 não aparecerá (após ~60s)
```

**Verificar logs:**
```bash
docker logs p2p_tracker | grep "inativo"
# [TRACKER] Removendo peer inativo: peer3
```

**Reativar:**
```bash
docker start p2p_peer3
docker exec -it p2p_peer3 python peer.py
```

## 📊 Ver Logs do Sistema

### Via Interface Web

No hotsite (http://localhost:8081), a seção de logs mostra operações em tempo real.

### Via Docker

**Ver logs do tracker:**
```bash
docker logs -f p2p_tracker
```

**Ver logs de um peer:**
```bParar todos os containers:
```bash
docker-compose down
```

### Limpeza completa (remove volumes):
```bash
docker-compose down -v
```

### Usando scripts de gerenciamento:

**Windows:**
```powershell
.\manage.ps1 stop    # Parar
.\manage.ps1 clean   # Limpar tudo
```

**Linux/Mac:**
```bash
make stop    # Parar
make clean   # Limpar tudo

## 🛑 Parar o Sistema

### Encerrar peers:
- Dentro de cada peer: Opção **0** → Confirmar: **s**

### Parar containers:
```bash
# No terminal do docker-compose: Ctrl+C
# Ou em outro terminal:
docker-compose down
### Interface Web
✅ **Recomendações:**
- Use o hotsite (porta 8081) para demonstrações visuais
- Monitore com Grafana para ver métricas em tempo real
- Use a API REST para integrações programáticas
- Acompanhe logs diretamente na interface

### Interface CLI
✅ **DO's:**
- Use caminhos absolutos ao publicar: `/app/shared_files/arquivo.zip`
- Aguarde alguns segundos entre operações
- Verifique logs em caso de erro
- Use opção 6 para ver peers disponíveis antes de publicar

❌ **DON'Ts:**
- Não feche terminal sem usar opção 0
- Não use caminhos relativos
- Não pare peers durante transferência

## 🎓 Próximos Passos

1. **Para demonstrações:** Veja [APRESENTACAO.md](APRESENTACAO.md) - Roteiro completo de apresentação
2. **Para testes detalhados:** Veja [TESTE.md](TESTE.md) - Guia de testes completos
3. **Para usar GUI local:** Veja [GUI_GUIDE.md](GUI_GUIDE.md) - Interface gráfica desktop
4. **Para documentação completa:** Veja [README.md](README.md) - Referência completa do sistema

## 🆘 Problemas?

### Sistema não inicia
```bash
# Verificar status dos containers
docker-compose ps

# Ver logs de todos os serviços
docker-compose logs

# Reconstruir do zero
docker-compose down -v
docker-compose up -d --build
```

### Hotsite não carrega
- Verifique se a porta 8081 está livre
- Aguarde alguns segundos após `docker-compose up`
- Acesse: `docker logs p2p_hotsite`

### Grafana não conecta
- Aguarde ~30 segundos após iniciar
- Login: admin / admin
- Verifique Prometheus: http://localhost:9090

---

**Pronto para começar! 🎉**

**⭐ Início Recomendado:** Acesse http://localhost:8081 e explore o dashboard web!s
- Não pare peers durante transferência

## 🆘 Problemas?

Consulte o [TESTE.md](TESTE.md) para guia detalhado de testes ou [README.md](README.md) para documentação completa.

---

**Pronto para começar! 🎉**
