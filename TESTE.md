# Guia de Teste Rápido - Sistema P2P

Este guia demonstra como testar todas as funcionalidades do sistema.

## 🚀 Iniciar o Sistema

```bash
# 1. Build e iniciar containers
docker-compose up --build

# 2. Aguarde até ver as mensagens:
# - [TRACKER] Iniciado em 0.0.0.0:5000
# - [PEER] Peer iniciado com sucesso! (para cada peer)
```

## 📝 Teste 1: Publicação e Replicação

### Terminal 1 - Peer 1
```bash
docker exec -it p2p_peer1 python peer.py
```

Dentro da interface:
1. Escolha opção **1** (Publicar arquivo)
2. Para criar um arquivo de teste:
   - Abra outro terminal
   - Execute:
     ```bash
     docker exec p2p_peer1 sh -c "echo 'Conteúdo do TCC' > /app/shared_files/tcc_exemplo.zip"
     ```
3. Digite o caminho: `/app/shared_files/tcc_exemplo.zip`
4. Observe a replicação automática

### Terminal 2 - Verificar Tracker
```bash
docker logs p2p_tracker | tail -20
```

Você deve ver:
- `[TRACKER] Peer registrado: peer1`
- `[TRACKER] Arquivo publicado: tcc_exemplo.zip por peer1`

## 🔍 Teste 2: Busca e Download

### Terminal 3 - Peer 2
```bash
docker exec -it p2p_peer2 python peer.py
```

1. Escolha opção **2** (Buscar arquivos)
2. Digite termo: `tcc`
3. Observe a tabela com resultados

4. Escolha opção **3** (Baixar arquivo)
5. Digite: `tcc_exemplo.zip`
6. Observe a barra de progresso
7. Arquivo baixado com sucesso!

## 📊 Teste 3: Listar Recursos

### No Peer 2 (ainda aberto):

1. Opção **4** - Ver arquivos locais
   - Deve mostrar `tcc_exemplo.zip`

2. Opção **5** - Ver todos arquivos da rede
   - Mostra arquivos e número de réplicas

3. Opção **6** - Ver peers ativos
   - Deve mostrar peer1, peer2, peer3

4. Opção **7** - Status do sistema
   - Informações do peer atual

## 💥 Teste 4: Tolerância a Falhas

### Simular Falha de Peer

1. Abra novo terminal:
   ```bash
   docker stop p2p_peer3
   ```

2. Aguarde 60 segundos (timeout de heartbeat)

3. Verifique logs do tracker:
   ```bash
   docker logs p2p_tracker | tail -10
   ```
   
   Deve mostrar:
   ```
   [TRACKER] Removendo peer inativo: peer3
   ```

4. No Peer 2, escolha opção **6** (listar peers)
   - peer3 não deve aparecer

5. Escolha opção **5** (listar arquivos)
   - Arquivo ainda disponível (réplicas em peer1 e peer2)

### Recuperar Peer

```bash
docker start p2p_peer3
docker exec -it p2p_peer3 python peer.py
```

## 🔄 Teste 5: Múltiplos Downloads Simultâneos

### Criar múltiplos arquivos:

```bash
# Terminal separado
docker exec p2p_peer1 sh -c "echo 'Artigo 1' > /app/shared_files/artigo1.zip"
docker exec p2p_peer1 sh -c "echo 'Artigo 2' > /app/shared_files/artigo2.zip"
docker exec p2p_peer1 sh -c "echo 'Trabalho' > /app/shared_files/trabalho.zip"
```

### No Peer 1:
1. Publique cada arquivo (opção 1)
   - `/app/shared_files/artigo1.zip`
   - `/app/shared_files/artigo2.zip`
   - `/app/shared_files/trabalho.zip`

### No Peer 3:
1. Baixe todos os arquivos (opção 3)
2. Verifique arquivos locais (opção 4)

## 🎯 Teste 6: Heartbeat

### Monitorar Heartbeat em Tempo Real

```bash
# Terminal separado
docker logs -f p2p_tracker
```

Você verá a cada 30 segundos:
```
[TRACKER] Recebido HEARTBEAT de peer1
[TRACKER] Recebido HEARTBEAT de peer2
[TRACKER] Recebido HEARTBEAT de peer3
```

## 📈 Teste 7: Replicação Completa

### Verificar número de réplicas:

1. Em qualquer peer, opção **5** (listar arquivos da rede)
2. Coluna "Réplicas" deve mostrar **2** ou **3**
3. Se mostrar **1**, arquivo precisa de re-replicação

## 🧹 Finalizar Testes

### Encerrar Peers (em cada terminal):
1. Opção **0** (Sair)
2. Confirmar: `s`

### Parar Sistema:
```bash
# Terminal principal
Ctrl+C

# Remover containers
docker-compose down

# Limpar volumes
docker-compose down -v
```

## ✅ Checklist de Funcionalidades Testadas

- [ ] Registro de peers no tracker
- [ ] Heartbeat automático (30s)
- [ ] Publicação de arquivo
- [ ] Replicação automática (2 cópias)
- [ ] Busca de arquivos
- [ ] Download com progresso
- [ ] Listagem de arquivos locais
- [ ] Listagem de arquivos da rede
- [ ] Listagem de peers ativos
- [ ] Peer desconectar (docker stop)
- [ ] Tracker detectar inatividade (60s)
- [ ] Download de peer alternativo
- [ ] Múltiplos peers simultâneos
- [ ] Persistência de metadados

## 🐛 Problemas Comuns

### Erro ao publicar arquivo
**Problema**: Arquivo não encontrado  
**Solução**: Use caminho absoluto `/app/shared_files/arquivo.zip`

### Peer não aparece na lista
**Problema**: Demora para registrar  
**Solução**: Aguarde 5 segundos após iniciar peer

### Download falha
**Problema**: Peer fonte offline  
**Solução**: Sistema tentará outro peer automaticamente

### Réplicas insuficientes
**Problema**: Menos de 3 peers ativos  
**Solução**: Normal com 3 peers (1 origem + 2 réplicas)

## 📊 Métricas Esperadas

- **Tempo de replicação**: ~1-2 segundos por arquivo pequeno
- **Tempo de download**: ~0.5 segundos para arquivos pequenos
- **Detecção de falha**: máximo 60 segundos
- **Heartbeat**: exatamente 30 segundos

---

**Boa sorte nos testes! 🚀**
