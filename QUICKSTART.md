# 🚀 Guia de Início Rápido

## ⚡ Começar em 3 Passos

### 1️⃣ Criar Arquivos de Teste (Opcional)

**Windows (PowerShell):**
```powershell
.\create_test_files.ps1
```

**Linux/Mac:**
```bash
chmod +x create_test_files.sh
./create_test_files.sh
```

### 2️⃣ Iniciar o Sistema

```bash
docker-compose up --build
```

Aguarde até ver:
```
p2p_tracker  | [TRACKER] Iniciado em 0.0.0.0:5000
p2p_peer1    | [PEER] Peer iniciado com sucesso!
p2p_peer2    | [PEER] Peer iniciado com sucesso!
p2p_peer3    | [PEER] Peer iniciado com sucesso!
```

### 3️⃣ Acessar um Peer

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

## 🎬 Exemplo Prático

### Cenário: Compartilhar um TCC

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

## 🔄 Fluxo Completo de Trabalho

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

## 🧪 Teste Rápido de Falha

### Simular peer offline:

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

## 📊 Monitoramento em Tempo Real

### Ver logs do tracker:
```bash
docker logs -f p2p_tracker
```

### Ver logs de um peer:
```bash
docker logs -f p2p_peer1
```

## 🛑 Parar o Sistema

### Encerrar peers:
- Dentro de cada peer: Opção **0** → Confirmar: **s**

### Parar containers:
```bash
# No terminal do docker-compose: Ctrl+C
# Ou em outro terminal:
docker-compose down
```

### Limpeza completa:
```bash
docker-compose down -v  # Remove volumes também
```

## 📝 Dicas

✅ **DO's:**
- Use caminhos absolutos ao publicar: `/app/shared_files/arquivo.zip`
- Aguarde alguns segundos entre operações
- Verifique logs em caso de erro
- Use opção 6 para ver peers disponíveis antes de publicar

❌ **DON'Ts:**
- Não feche terminal sem usar opção 0
- Não use caminhos relativos
- Não pare peers durante transferência

## 🆘 Problemas?

Consulte o [TESTE.md](TESTE.md) para guia detalhado de testes ou [README.md](README.md) para documentação completa.

---

**Pronto para começar! 🎉**
