# Roteiro de Apresentacao - TP2 Redes P2P Hibrido

Este documento descreve como usar a aplicacao durante a apresentacao do TP2.
O objetivo e demonstrar que a Tematica 5, Backup Academico Seguro, esta
implementada com Tracker, Peers, replicacao voluntaria em pelo menos 2 peers,
heartbeat e re-replicacao.

## 1. Subir a Aplicacao

Na raiz do projeto, execute:

```bash
docker compose up -d --build
```

Verifique se todos os servicos estao ativos:

```bash
docker compose ps
```

Servicos esperados:

- `p2p_tracker`: Tracker central, porta `5000`.
- `p2p_peer1`, `p2p_peer2`, `p2p_peer3`: peers da rede, portas `6001`, `6002`, `6003`.
- `p2p_web_gateway`: peer real usado pela interface web, API na porta `8082`.
- `p2p_hotsite`: painel web de apresentacao, porta `8081`.
- `prometheus`: monitoramento, porta `9090`.
- `grafana`: dashboard, porta `3000`.
- `node_exporter`: metricas do host.

## 2. URLs da Apresentacao

Abra no navegador:

- Hotsite / Painel principal: `http://localhost:8081`
- Gateway API do backend: `http://localhost:8082/api/status`
- Grafana: `http://localhost:3000`
- Prometheus: `http://localhost:9090`

Credenciais padrao do Grafana:

- Usuario: `admin`
- Senha: `admin`

## 3. O que Explicar no Inicio

Use o topo do hotsite para apresentar a arquitetura:

- O Tracker e o servidor central.
- O Tracker nao armazena arquivos, apenas metadados: nome, hash e lista de peers.
- Cada peer atua como cliente e servidor.
- Cliente para consultar/publicar no Tracker.
- Servidor para enviar arquivos para outros peers via TCP.
- A interface web nao substitui o backend. Ela chama o `web-gateway`, que e um peer real integrado ao sistema Python.

Frase sugerida:

> Esta e uma arquitetura P2P hibrida. O Tracker centraliza apenas metadados, enquanto os arquivos zip trafegam diretamente entre peers por socket TCP. A interface web executa as mesmas operacoes da CLI por meio de um peer gateway chamado `web-ui`.

## 4. Painel de Infraestrutura

No topo da pagina:

1. Clique em **Abrir Grafana (Monitoramento)**.
2. Mostre que o ambiente de monitoramento esta em execucao.
3. Volte ao hotsite.
4. Clique em **Abrir Prometheus**.
5. Mostre que as metricas estao disponiveis.

Se o professor perguntar sobre observabilidade:

- Prometheus coleta metricas.
- Grafana exibe dashboards.
- Node Exporter coleta metricas do host.
- O Tracker expoe metricas como quantidade de peers ativos.

## 5. Demonstrar o Fluxo Principal no Hotsite

### 5.1 Verificar Status da Rede

No painel **Acoes da CLI**, clique em:

- `STATUS`

Resultado esperado:

- O log mostra o peer `web-ui`.
- Mostra IP, porta, quantidade de arquivos locais e heartbeat ativo.
- O status global mostra peers ativos.

Essa acao corresponde ao item `7. Status do sistema` da CLI.

### 5.2 Listar Peers Ativos

Clique em:

- `LIST_PEERS`

Resultado esperado:

- A lista **Peers da Rede** deve mostrar `peer1`, `peer2`, `peer3` e `web-ui`.

Essa acao corresponde ao item `6. Listar peers ativos` da CLI.

### 5.3 Publicar um Arquivo .zip

No card **Upload Academico**:

1. Clique em **Selecionar arquivo .zip**.
2. Escolha um arquivo `.zip` de teste, por exemplo `teste_tcc.zip`.
3. Clique em **Publicar no Tracker e Replicar**.

Resultado esperado:

- A interface envia o arquivo para o `web-gateway`.
- O peer `web-ui` calcula o hash SHA-256.
- O `web-ui` publica os metadados no Tracker.
- O backend inicia replicacao TCP para outros peers.
- A tabela **Tracker: Metadados Indexados** mostra:
  - nome do arquivo;
  - hash;
  - quantidade de replicas;
  - peers que possuem o arquivo.

Essa acao corresponde ao item `1. Publicar arquivo` da CLI.

Ponto importante para falar:

> O arquivo nao foi armazenado no Tracker. O Tracker recebeu apenas os metadados. A copia real foi enviada entre peers via TCP.

### 5.4 Buscar Arquivo pelo Nome

No campo `LOOKUP por nome...`:

1. Digite parte do nome do arquivo, por exemplo `tcc`.
2. Clique em `LOOKUP`.

Resultado esperado:

- A tabela e atualizada com os resultados retornados pelo Tracker.
- O terminal interativo mostra o payload JSON do comando `LOOKUP`.

Essa acao corresponde ao item `2. Buscar arquivos` da CLI.

### 5.5 Baixar Arquivo

Na tabela de arquivos:

1. Clique em `DOWNLOAD` no arquivo publicado.

Resultado esperado:

- O `web-ui` consulta o Tracker para descobrir quais peers possuem o arquivo.
- O backend seleciona um peer.
- O arquivo e baixado via TCP.
- O hash e validado apos o download.
- O log mostra `DOWNLOAD concluido e validado pelo backend`.

Essa acao corresponde ao item `3. Baixar arquivo` da CLI.

### 5.6 Listar Arquivos Locais

Clique em:

- `LIST_LOCAL`

Resultado esperado:

- A tabela mostra os arquivos armazenados localmente no peer `web-ui`.

Essa acao corresponde ao item `4. Listar arquivos locais` da CLI.

### 5.7 Listar Todos os Arquivos da Rede

Para voltar a lista global:

1. Clique em `LOOKUP` com o campo vazio, ou recarregue a pagina.

Resultado esperado:

- A tabela volta a mostrar os arquivos indexados no Tracker.

Essa acao corresponde ao item `5. Listar todos os arquivos da rede` da CLI.

## 6. Terminal Interativo de Protocolo

Use a secao **Terminal Interativo de Protocolo** para explicar os comandos:

- `LIST`: lista recursos ou peers.
- `LOOKUP <nome>`: busca metadados pelo nome do arquivo.
- `DOWNLOAD <hash> <peer>`: baixa o arquivo de um peer especifico.

Clique nos botoes:

- `LIST`
- `LOOKUP`
- `DOWNLOAD`

Explique:

- Cliente para Tracker usa JSON via TCP.
- Cliente para Cliente usa TCP para transferir o binario do arquivo.
- O hash e usado para validar integridade.

## 7. Demonstrar Tolerancia a Falhas

A deteccao de falha real depende do heartbeat do Tracker. O timeout padrao esta no backend.

Para uma demonstracao completa em terminal, use:

```bash
python3 test_e2e.py
```

Esse teste automatizado:

1. Sobe Tracker e peers reais.
2. Publica `teste_tcc.zip`.
3. Valida replicas em dois peers.
4. Faz lookup e download.
5. Mata um peer com falha grave.
6. Aguarda o Tracker detectar a queda.
7. Valida re-replicacao para restaurar pelo menos 2 copias.

Se tudo passar, aparece:

```text
✅ SUCESSO: Fluxo Completo do TP2 Validado com Sucesso!
```

Frase sugerida:

> Para a interface visual, mostro a publicacao, busca, download e listagens. Para provar tolerancia a falhas no nivel do sistema operacional, executo o teste E2E automatizado, que mata um processo de peer e valida a re-replicacao real.

## 8. Comandos Uteis Durante a Apresentacao

Ver containers:

```bash
docker compose ps
```

Ver logs do Tracker:

```bash
docker compose logs -f tracker
```

Ver logs do gateway web:

```bash
docker compose logs -f web-gateway
```

Ver logs de um peer:

```bash
docker compose logs -f peer1
```

Consultar status da API:

```bash
curl http://localhost:8082/api/status
```

Listar peers via API:

```bash
curl http://localhost:8082/api/peers
```

Listar arquivos da rede via API:

```bash
curl http://localhost:8082/api/files/network
```

## 9. Ordem Recomendada da Apresentacao

1. Abrir `http://localhost:8081`.
2. Explicar o Tracker, peers e monitoramento.
3. Clicar em `LIST_PEERS`.
4. Clicar em `STATUS`.
5. Fazer upload de um `.zip`.
6. Mostrar o arquivo na tabela do Tracker.
7. Fazer `LOOKUP` pelo nome.
8. Fazer `DOWNLOAD`.
9. Clicar em `LIST_LOCAL`.
10. Mostrar Grafana e Prometheus.
11. Rodar `python3 test_e2e.py` para provar falha e re-replicacao.

## 10. Problemas Comuns

### Hotsite abre, mas nao mostra dados reais

Verifique se o gateway esta ativo:

```bash
docker compose ps web-gateway
```

Teste a API:

```bash
curl http://localhost:8082/api/status
```

### Upload falha

Confirme:

- O arquivo tem extensao `.zip`.
- Existem peers ativos alem do `web-ui`.
- O Tracker esta rodando.

### Grafana nao abre

Verifique:

```bash
docker compose ps grafana
```

URL correta:

```text
http://localhost:3000
```

### Porta em uso

Portas usadas pelo projeto:

- `3000`: Grafana
- `5000`: Tracker
- `6001`, `6002`, `6003`: Peers
- `6200`: peer web-ui
- `8081`: Hotsite
- `8082`: Gateway API
- `9090`: Prometheus

Se alguma porta estiver ocupada, ajuste o `docker-compose.yml`.

