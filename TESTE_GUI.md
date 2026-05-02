# 🚀 Teste Rápido da Interface Gráfica

Este guia ajuda você a testar a nova interface gráfica em menos de 2 minutos!

## ✅ Pré-requisitos

- Python 3.8 ou superior instalado
- tkinter (já incluído no Python padrão)

Verifique rapidamente:
```bash
python --version
python -c "import tkinter; print('tkinter OK')"
```

## 🎯 Teste em 3 Passos

### 1️⃣ Iniciar o Tracker

Abra um terminal/PowerShell e execute:

**Windows (PowerShell):**
```powershell
cd tracker
python tracker.py
```

**Linux/Mac:**
```bash
cd tracker
python3 tracker.py
```

Você verá:
```
[TRACKER] Servidor iniciado na porta 5000
```

### 2️⃣ Iniciar o Peer com GUI

Abra um **NOVO** terminal/PowerShell e execute:

**Windows (PowerShell):**
```powershell
cd peer
python peer_gui.py
```

**Linux/Mac:**
```bash
cd peer
python3 peer_gui.py
```

**Ou use o script automatizado (Windows):**
```powershell
.\run_gui.ps1
```

### 3️⃣ Explorar a Interface

A janela da GUI será aberta automaticamente! 

#### Teste 1: Publicar um Arquivo
1. Clique na aba **"📤 Publicar Arquivo"**
2. Clique em **"Selecionar Arquivo"**
3. Escolha qualquer arquivo do seu computador
4. Clique em **"Publicar na Rede"**
5. ✅ Veja o arquivo sendo publicado nos logs!

#### Teste 2: Ver Arquivos Locais
1. Clique na aba **"💾 Arquivos Locais"**
2. Veja o arquivo que você acabou de publicar
3. Note o tamanho formatado e o hash

#### Teste 3: Iniciar Outro Peer
1. Abra mais um terminal
2. Execute novamente:
   ```powershell
   cd peer
   $env:PEER_PORT = "6002"  # Porta diferente!
   python peer_gui.py
   ```
3. Uma segunda janela será aberta

#### Teste 4: Buscar e Baixar
1. Na segunda janela (Peer 2)
2. Vá para **"🔍 Buscar Arquivos"**
3. Clique em **"Listar Todos"**
4. Selecione o arquivo publicado pelo Peer 1
5. Clique em **"⬇ Baixar Arquivo Selecionado"**
6. ✅ Arquivo baixado com sucesso!

#### Teste 5: Ver Peers Ativos
1. Em qualquer janela, vá para **"🌐 Peers Ativos"**
2. Clique em **"🔄 Atualizar Lista"**
3. Veja os 2 peers conectados!

#### Teste 6: Monitorar Logs
1. Vá para **"📋 Logs"**
2. Veja todas as operações registradas
3. Cada log tem timestamp

## 🎨 Recursos Visuais

A interface possui:

- **Tema Escuro** moderno e agradável
- **Abas Organizadas** para cada funcionalidade
- **Tabelas Interativas** para visualização de dados
- **Botões Coloridos** para diferentes ações
- **Logs em Tempo Real** para monitoramento
- **Barra de Status** com estatísticas

## 🔍 Comparação Rápida: CLI vs GUI

| Ação | CLI | GUI |
|------|-----|-----|
| Publicar arquivo | Digitar caminho | Selecionar visualmente |
| Buscar arquivos | Digitar comando | Clicar botão |
| Baixar arquivo | Digitar nome exato | Clicar na tabela |
| Ver arquivos | Lista texto | Tabela formatada |
| Ver peers | Lista texto | Tabela formatada |
| Monitorar | Não disponível | Logs em tempo real |

## 🐛 Problemas Comuns

### "tkinter não encontrado" (Linux)
```bash
sudo apt-get install python3-tk
```

### "Não foi possível conectar ao tracker"
- Certifique-se de que o tracker está executando (`python tracker.py`)
- Verifique se a porta 5000 está livre
- Aguarde alguns segundos e tente novamente

### "Porta já em uso"
Se a porta 6001 já estiver em uso, defina outra:
```powershell
$env:PEER_PORT = "6002"
python peer_gui.py
```

### Interface não abre
- Verifique se você está usando Python 3.8+
- Teste: `python -c "import tkinter; tkinter.Tk()"`
- No Windows, reinstale Python e marque "tcl/tk and IDLE"

## 📚 Próximos Passos

- 📖 Leia o [GUI_GUIDE.md](GUI_GUIDE.md) para guia completo
- 📖 Veja [README.md](README.md) para arquitetura do sistema
- 🧪 Execute testes de falha com múltiplos peers
- ⚙️ Personalize configurações

## 💡 Dica

Para melhor experiência:
1. Execute 3 peers simultaneamente
2. Publique arquivos em um
3. Baixe em outro
4. Monitore os logs em tempo real
5. Veja a replicação automática funcionando!

## 🎉 Aproveite!

A interface gráfica torna o sistema P2P muito mais fácil e intuitivo de usar!

---

**Criado com:** Python + tkinter  
**Tema:** Escuro moderno  
**Versão:** 2.0.0
