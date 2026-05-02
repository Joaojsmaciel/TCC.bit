# 🎨 Guia de Uso - Interface Gráfica

## 📋 Requisitos

- Python 3.8 ou superior
- tkinter (geralmente já incluído no Python)
- Conexão com o tracker

## 🚀 Iniciando o Sistema com Interface Gráfica

### Opção 1: Script PowerShell (Recomendado para Windows)

1. Execute o script de inicialização:
```powershell
.\run_gui.ps1
```

2. O script irá:
   - Verificar se o Python está instalado
   - Perguntar se deseja iniciar o tracker
   - Solicitar configurações (host, porta)
   - Iniciar a interface gráfica

### Opção 2: Manual

1. **Iniciar o Tracker** (em um terminal separado):
```bash
cd tracker
python tracker.py
```

2. **Iniciar o Peer com GUI** (em outro terminal):
```bash
cd peer
python peer_gui.py
```

### Opção 3: Docker (Interface CLI)

O Docker atualmente suporta apenas a interface CLI. Para usar a GUI, execute localmente.

```bash
docker-compose up --build
docker exec -it p2p_peer1 python peer.py
```

## 🎯 Funcionalidades da Interface Gráfica

### 📤 Aba "Publicar Arquivo"
- **Selecionar Arquivo**: Abre um diálogo para escolher o arquivo
- **Publicar na Rede**: Publica o arquivo selecionado no sistema P2P
- Após publicar, o arquivo fica disponível para outros peers

### 🔍 Aba "Buscar Arquivos"
- **Campo de Busca**: Digite o nome ou parte do nome do arquivo
- **Botão Buscar**: Realiza a busca na rede
- **Listar Todos**: Mostra todos os arquivos disponíveis na rede
- **Tabela de Resultados**: Exibe:
  - Nome do arquivo
  - Número de réplicas (peers que têm o arquivo)
  - Hash do arquivo (identificador único)
- **Baixar Arquivo Selecionado**: Selecione um arquivo na tabela e clique para baixar

### 💾 Aba "Arquivos Locais"
- Mostra todos os arquivos que você possui localmente
- Informações exibidas:
  - Nome do arquivo
  - Tamanho (formatado em B, KB, MB, GB)
  - Hash do arquivo
- **Botão Atualizar**: Atualiza a lista de arquivos

### 🌐 Aba "Peers Ativos"
- Lista todos os peers conectados à rede
- Informações exibidas:
  - Peer ID (identificador único)
  - Endereço IP
  - Porta de conexão
  - Número de arquivos compartilhados
- **Botão Atualizar**: Atualiza a lista de peers

### 📋 Aba "Logs"
- Mostra logs em tempo real das operações
- Registra:
  - Publicações de arquivos
  - Downloads
  - Buscas realizadas
  - Conexões e desconexões
  - Erros e avisos
- **Botão Limpar Logs**: Remove todos os logs da tela

### ℹ️ Barra de Status
- **Status da Conexão**: Mostra se está conectado ao tracker
- **Estatísticas**: Número de arquivos locais e peers ativos

## 💡 Dicas de Uso

### Como Compartilhar um Arquivo
1. Vá para a aba "📤 Publicar Arquivo"
2. Clique em "Selecionar Arquivo"
3. Escolha o arquivo desejado
4. Clique em "Publicar na Rede"
5. Aguarde a confirmação de sucesso

### Como Baixar um Arquivo
1. Vá para a aba "🔍 Buscar Arquivos"
2. Digite o nome do arquivo no campo de busca OU clique em "Listar Todos"
3. Selecione o arquivo desejado na tabela
4. Clique em "⬇ Baixar Arquivo Selecionado"
5. O arquivo será baixado automaticamente

### Monitorando o Sistema
- Use a aba "📋 Logs" para acompanhar todas as atividades
- Verifique a aba "🌐 Peers Ativos" para ver quem está online
- A aba "💾 Arquivos Locais" mostra seus arquivos disponíveis

## 🔧 Solução de Problemas

### "Não foi possível conectar ao tracker"
- Certifique-se de que o tracker está executando
- Verifique o host e porta configurados
- Tente: `python tracker/tracker.py` em outro terminal

### "Erro ao publicar arquivo"
- Verifique se o arquivo existe
- Certifique-se de que tem permissões de leitura
- Verifique os logs para mais detalhes

### "Erro ao baixar arquivo"
- Verifique se há peers ativos com o arquivo
- Certifique-se de ter espaço em disco
- Tente buscar o arquivo novamente

### Interface não abre
- Verifique se tkinter está instalado:
  ```bash
  python -c "import tkinter; print('OK')"
  ```
- No Windows, tkinter geralmente vem com Python
- No Linux, instale: `sudo apt-get install python3-tk`

## ⚙️ Configurações Avançadas

### Variáveis de Ambiente

Você pode configurar através de variáveis de ambiente:

```powershell
# Windows PowerShell
$env:TRACKER_HOST = "192.168.1.100"
$env:TRACKER_PORT = "5000"
$env:PEER_PORT = "6001"
cd peer
python peer_gui.py
```

```bash
# Linux/Mac
export TRACKER_HOST="192.168.1.100"
export TRACKER_PORT="5000"
export PEER_PORT="6001"
cd peer
python peer_gui.py
```

### Múltiplos Peers

Para executar múltiplos peers na mesma máquina:

1. Abra vários terminais
2. Em cada um, configure uma porta diferente:
```powershell
# Terminal 1
$env:PEER_PORT = "6001"
cd peer; python peer_gui.py

# Terminal 2 (novo)
$env:PEER_PORT = "6002"
cd peer; python peer_gui.py

# Terminal 3 (novo)
$env:PEER_PORT = "6003"
cd peer; python peer_gui.py
```

## 📊 Comparação: CLI vs GUI

| Recurso | CLI | GUI |
|---------|-----|-----|
| Publicar arquivo | ✓ | ✓ |
| Buscar arquivos | ✓ | ✓ |
| Baixar arquivos | ✓ | ✓ |
| Listar arquivos locais | ✓ | ✓ |
| Listar peers | ✓ | ✓ |
| Logs em tempo real | - | ✓ |
| Interface visual | - | ✓ |
| Seleção de arquivo gráfica | - | ✓ |
| Atualização automática | - | ✓ |
| Uso em Docker | ✓ | - |

## 🎨 Atalhos de Teclado

- **Enter** no campo de busca: Executa a busca
- **Seleção na tabela** + **Enter**: (funcionalidade futura)

## 📝 Notas

- A interface gráfica **não** funciona dentro de containers Docker (sem suporte X11)
- Para usar em Docker, utilize a interface CLI: `python peer.py`
- A GUI atualiza automaticamente algumas informações a cada 10 segundos
- Todos os arquivos são armazenados em `files_<peer_id>/`
- A replicação automática garante mínimo de 2 cópias de cada arquivo

## 🆘 Suporte

Para mais informações:
- Veja [README.md](README.md) para arquitetura do sistema
- Veja [QUICKSTART.md](QUICKSTART.md) para início rápido
- Veja [CONFIGURACAO.md](CONFIGURACAO.md) para configurações detalhadas
