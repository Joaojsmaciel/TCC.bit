# Guia de Uso da Aplicacao P2P

Este documento explica como executar e usar o sistema P2P de compartilhamento de arquivos, tanto pela interface grafica quanto pela interface CLI em Docker. O sistema usa um tracker central para registrar peers e metadados, enquanto os arquivos sao transferidos diretamente entre peers.

## 1. Visao Geral

A aplicacao possui estes componentes principais:

- **Tracker**: servidor central que registra peers ativos, arquivos publicados e localizacao das replicas.
- **Peer**: no da rede que publica, busca, baixa e serve arquivos para outros peers.
- **GUI do Peer**: interface grafica em Tkinter para operar um peer localmente.
- **CLI do Peer**: interface de terminal usada principalmente nos containers Docker.
- **Prometheus/Grafana/Node Exporter**: stack de observabilidade para acompanhar consumo da VM e metricas da rede P2P.

## 2. Pre-requisitos

Para executar com Docker:

- Docker
- Docker Compose

Para executar a GUI localmente:

- Python 3.8 ou superior
- Tkinter
- Acesso ao tracker na porta configurada, por padrao `5000`

No Linux, se o Tkinter nao estiver instalado:

```bash
sudo apt-get install python3-tk
```

Para testar se o Tkinter esta disponivel:

```bash
python3 -c "import tkinter; print('OK')"
```

## 3. Execucao com Docker

Na raiz do projeto, execute:

```bash
docker compose up -d --build
```

Esse comando sobe:

- tracker em `localhost:5000`
- peer1 em `localhost:6001`
- peer2 em `localhost:6002`
- peer3 em `localhost:6003`
- Prometheus em `localhost:9090`
- Grafana em `localhost:3000`
- Node Exporter em `localhost:9100`

Para acompanhar os logs:

```bash
docker compose logs -f
```

Para parar tudo:

```bash
docker compose down
```

## 4. Usando a CLI em Docker

Depois de subir os containers, abra um terminal interativo em um peer:

```bash
docker exec -it p2p_peer1 python peer.py
```

Tambem e possivel usar:

```bash
docker exec -it p2p_peer2 python peer.py
docker exec -it p2p_peer3 python peer.py
```

O menu principal apresenta as opcoes:

```text
1. Publicar arquivo
2. Buscar arquivos
3. Baixar arquivo
4. Listar arquivos locais
5. Listar todos os arquivos da rede
6. Listar peers ativos
7. Status do sistema
0. Sair
```

### Publicar Arquivo Pela CLI

1. Acesse um peer:

```bash
docker exec -it p2p_peer1 python peer.py
```

2. Escolha a opcao `1`.
3. Informe o caminho do arquivo dentro do container.

Exemplo:

```text
/app/shared_files/exemplo.txt
```

Ao publicar, o peer calcula o hash SHA-256, registra o arquivo no tracker e tenta replicar o arquivo para outros peers ativos.

### Buscar Arquivos Pela CLI

1. Escolha a opcao `2`.
2. Digite o nome ou parte do nome do arquivo.
3. A CLI mostra os arquivos encontrados, hash e quantidade de replicas.

### Baixar Arquivo Pela CLI

1. Escolha a opcao `3`.
2. Digite o nome exato do arquivo.
3. O peer consulta o tracker, escolhe um peer fonte e baixa o arquivo diretamente dele.
4. Depois do download, o arquivo e registrado localmente e publicado no tracker.

## 5. Execucao Local com GUI

A GUI nao deve ser executada dentro dos containers Docker. Ela usa Tkinter e deve rodar localmente no sistema operacional.

### Windows com PowerShell

Na raiz do projeto:

```powershell
.\run_gui.ps1
```

O script:

- verifica se o Python esta instalado;
- pergunta se deseja iniciar o tracker;
- solicita host e porta do tracker;
- solicita porta do peer, ou usa porta automatica;
- inicia `peer/peer_gui.py`.

### Linux ou Execucao Manual

Terminal 1, iniciar o tracker:

```bash
cd tracker
python3 tracker.py
```

Terminal 2, iniciar um peer com GUI:

```bash
cd peer
python3 peer_gui.py
```

Por padrao, a GUI tenta conectar no tracker em `localhost:5000` e escolhe uma porta livre para o peer.

## 6. Configuracao por Variaveis de Ambiente

Voce pode configurar tracker, porta e ID do peer antes de iniciar a GUI.

Linux:

```bash
export TRACKER_HOST="localhost"
export TRACKER_PORT="5000"
export PEER_PORT="6001"
export PEER_ID="peer_gui_1"
cd peer
python3 peer_gui.py
```

Windows PowerShell:

```powershell
$env:TRACKER_HOST = "localhost"
$env:TRACKER_PORT = "5000"
$env:PEER_PORT = "6001"
$env:PEER_ID = "peer_gui_1"
cd peer
python peer_gui.py
```

Se `PEER_PORT=0` ou nao for definido, a aplicacao escolhe uma porta livre automaticamente.

## 7. Usando a Interface Grafica

Ao abrir a GUI, o topo da janela mostra:

- ID do peer;
- IP e porta do peer;
- status de conexao com o tracker.

A interface possui cinco abas.

### Aba Publicar Arquivo

Use essa aba para colocar um arquivo na rede.

1. Clique em **Selecionar Arquivo**.
2. Escolha um arquivo do computador.
3. Clique em **Publicar na Rede**.
4. Aguarde a mensagem de sucesso.

O arquivo e copiado para o diretorio local do peer, registrado no tracker e usado como fonte para replicacao.

### Aba Buscar Arquivos

Use essa aba para encontrar e baixar arquivos publicados.

Para buscar por nome:

1. Digite um termo no campo de busca.
2. Clique em **Buscar** ou pressione Enter.
3. Veja os resultados na tabela.

Para listar tudo:

1. Clique em **Listar Todos**.
2. A tabela mostra todos os arquivos conhecidos pelo tracker.

Para baixar:

1. Selecione um item da tabela.
2. Clique em **Baixar Arquivo Selecionado**.
3. Aguarde a confirmacao.

O download e feito diretamente de outro peer. O tracker apenas informa quais peers possuem o arquivo.

### Aba Arquivos Locais

Mostra os arquivos armazenados pelo peer atual.

Campos exibidos:

- nome do arquivo;
- tamanho;
- hash.

Use **Atualizar Lista** para recarregar a tabela.

Os arquivos ficam em um diretorio com o formato:

```text
peer/files_<peer_id>/
```

### Aba Peers Ativos

Mostra os peers registrados no tracker.

Campos exibidos:

- ID do peer;
- IP;
- porta;
- quantidade de arquivos, quando informada.

Use **Atualizar Lista** para consultar novamente o tracker.

### Aba Logs

Mostra eventos da GUI, como:

- arquivo selecionado;
- publicacao iniciada;
- busca realizada;
- download iniciado;
- atualizacoes de peers;
- erros retornados pela aplicacao.

Use **Limpar Logs** para limpar a tela de logs.

## 8. Fluxo Recomendado para Demonstracao

1. Suba a stack:

```bash
docker compose up -d --build
```

2. Configure o Grafana:

```bash
./setup_grafana.sh
```

3. Abra o Grafana em:

```text
http://localhost:3000
```

Credenciais padrao:

```text
usuario: admin
senha: admin
```

4. Abra um peer pela CLI:

```bash
docker exec -it p2p_peer1 python peer.py
```

5. Publique um arquivo pelo `p2p_peer1`.
6. Acesse outro peer:

```bash
docker exec -it p2p_peer2 python peer.py
```

7. Busque e baixe o arquivo pelo `p2p_peer2`.
8. No Grafana, abra o dashboard **Controle da Rede P2P** e acompanhe a metrica `p2p_active_peers`.
9. Para simular queda de peer:

```bash
docker stop p2p_peer3
```

10. Aguarde o timeout de heartbeat do tracker e observe a queda no painel.

## 9. Observabilidade

Prometheus coleta metricas em:

- `node_exporter`: consumo da VM, CPU, memoria, disco e rede;
- `tracker_app`: metricas expostas pelo tracker na porta `8000`.

Endpoints principais:

```text
Prometheus: http://localhost:9090
Grafana:    http://localhost:3000
Tracker:    http://localhost:5000
Metricas:   http://localhost:8000/metrics
```

A metrica customizada do tracker e:

```text
p2p_active_peers
```

Ela representa a quantidade atual de peers ativos registrados no tracker.

Para consultar no Prometheus:

1. Acesse `http://localhost:9090`.
2. Pesquise por `p2p_active_peers`.
3. Clique em **Execute**.

## 10. Solucao de Problemas

### A GUI nao conecta no tracker

Verifique se o tracker esta rodando:

```bash
python3 tracker/tracker.py
```

Ou, se estiver usando Docker:

```bash
docker compose ps
docker compose logs tracker
```

Confirme tambem se `TRACKER_HOST` e `TRACKER_PORT` estao corretos.

### Erro de porta em uso

Use outra porta para o peer:

```bash
export PEER_PORT="6010"
cd peer
python3 peer_gui.py
```

Ou deixe automatico:

```bash
export PEER_PORT="0"
```

### Interface grafica nao abre

Teste o Tkinter:

```bash
python3 -c "import tkinter; print('OK')"
```

Se falhar no Linux, instale:

```bash
sudo apt-get install python3-tk
```

### Arquivo nao aparece na busca

Confira:

- se o arquivo foi publicado com sucesso;
- se o peer que publicou continua ativo;
- se o termo de busca corresponde ao nome do arquivo;
- se o tracker esta recebendo heartbeats.

### Download falha

Possiveis causas:

- nenhum peer ativo possui o arquivo;
- o peer fonte foi desligado;
- a porta do peer fonte nao esta acessivel;
- o arquivo local foi removido manualmente;
- houve falha de hash apos a transferencia.

### Grafana nao mostra dados

Verifique se os containers estao ativos:

```bash
docker compose ps
```

Verifique os targets do Prometheus:

```text
http://localhost:9090/targets
```

Os jobs `node_exporter` e `tracker_app` devem aparecer como `UP`.

Se o dashboard ainda nao existir, rode:

```bash
./setup_grafana.sh
```

## 11. Comandos Uteis

Subir tudo:

```bash
docker compose up -d --build
```

Ver logs:

```bash
docker compose logs -f
```

Entrar no peer 1:

```bash
docker exec -it p2p_peer1 python peer.py
```

Parar um peer:

```bash
docker stop p2p_peer1
```

Subir novamente um peer:

```bash
docker start p2p_peer1
```

Parar toda a stack:

```bash
docker compose down
```

Recriar tudo:

```bash
docker compose down
docker compose up -d --build
./setup_grafana.sh
```

## 12. Observacoes

- O tracker nao armazena arquivos, apenas metadados.
- As transferencias de arquivo acontecem diretamente entre peers.
- O heartbeat mantem a lista de peers ativos atualizada.
- A replicacao tenta manter pelo menos duas copias de cada arquivo quando houver peers suficientes.
- A GUI e recomendada para uso local; em Docker, use a CLI.
- O Grafana usa `admin/admin` conforme configurado no `docker-compose.yml`.
