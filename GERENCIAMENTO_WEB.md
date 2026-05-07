# Gerenciamento de Peers na Interface Web 🌐

## 📋 Visão Geral

O sistema P2P agora possui **gerenciamento completo de peers através da interface web**, acessível em `http://localhost:8081`.

Esta funcionalidade permite administrar a rede P2P diretamente pelo navegador, sem necessidade de acesso CLI aos containers.

---

## 🎨 Interface Web de Gerenciamento

### Localização

Na página principal do hotsite (`http://localhost:8081`), logo após a seção "Ações da CLI", há um painel roxo com o título:

```
🔧 Gerenciamento de Peers
Administração completa da rede
[EXPANDIR]
```

### Como Acessar

1. Acesse `http://localhost:8081`
2. Role até a seção "Painel Operacional P2P"
3. Localize o painel "🔧 Gerenciamento de Peers"
4. Clique no botão **EXPANDIR**

---

## 🔧 Funcionalidades Disponíveis

### 1. ➕ Adicionar Peer

**Descrição:** Registrar manualmente um novo peer no tracker.

**Campos:**
- **Peer ID:** Identificador único do peer (ex: `peer_backup_001`)
- **IP:** Endereço IP do peer (ex: `192.168.1.50`)
- **Porta:** Porta TCP do peer (ex: `6010`)

**Passos:**
1. Preencher os 3 campos
2. Clicar em **+ Adicionar Peer**
3. Aguardar confirmação ✅

**Exemplo de uso:**
```
Peer ID: peer_manual_123
IP: 172.18.0.20
Porta: 6005
```

**Resultado esperado:**
```
✅ Peer peer_manual_123 adicionado com sucesso
```

**API Endpoint:** `POST /api/peer/add`

---

### 2. ✏️ Editar Peer

**Descrição:** Atualizar IP e/ou porta de um peer existente.

**Campos:**
- **Peer ID:** ID do peer a editar (obrigatório)
- **Novo IP:** Novo endereço IP (opcional)
- **Nova Porta:** Nova porta TCP (opcional)

**Regras:**
- Pelo menos um campo (IP ou Porta) deve ser preenchido
- Campos vazios mantêm o valor atual

**Passos:**
1. Informar o Peer ID
2. Preencher novo IP e/ou nova porta
3. Clicar em **✏️ Editar Peer**
4. Aguardar confirmação ✅

**Exemplo de uso:**
```
Peer ID: peer_52d1f8ae
Novo IP: 172.18.0.25
Nova Porta: (deixar vazio para manter)
```

**Resultado esperado:**
```
✅ Peer peer_52d1f8ae atualizado com sucesso
```

**API Endpoint:** `POST /api/peer/edit`

---

### 3. 🗑️ Remover Peer

**Descrição:** Remover um peer da rede (ação administrativa).

**Campos:**
- **Peer ID a remover:** ID do peer a ser removido

**Passos:**
1. Informar o Peer ID
2. Clicar em **🗑️ Remover**
3. Confirmar no diálogo
4. Aguardar confirmação ✅

**Atenção:** ⚠️ Esta ação é irreversível e pode causar perda de réplicas.

**Exemplo de uso:**
```
Peer ID a remover: peer_antigo_999
```

**Diálogo de confirmação:**
```
Confirma remoção do peer 'peer_antigo_999'?
[ Cancelar ] [ OK ]
```

**Resultado esperado:**
```
✅ Peer peer_antigo_999 removido com sucesso
```

**API Endpoint:** `POST /api/peer/remove`

---

### 4. 🔍 Ver Detalhes

**Descrição:** Visualizar informações completas de um peer, incluindo arquivos compartilhados.

**Campos:**
- **Peer ID:** ID do peer a consultar

**Passos:**
1. Informar o Peer ID
2. Clicar em **🔍 Ver Detalhes**
3. Informações aparecem abaixo

**Exemplo de uso:**
```
Peer ID: web-ui
```

**Resultado esperado:**
```
┌─────────────────────────────────────┐
│ Peer ID: web-ui                     │
│ IP: 172.18.0.8                      │
│ Porta: 6200                         │
│ Último Heartbeat: 2026-05-06T...    │
│ ─────────────────────────────────   │
│ Arquivos (2):                       │
│  📄 tcc_exemplo.zip (a3f5b9c2...)   │
│  📄 artigo.zip (b7e2c8d9...)        │
└─────────────────────────────────────┘
```

**API Endpoint:** `GET /api/peer/details?peer_id=<id>`

---

## 🔌 Endpoints da API

### Resumo dos Endpoints Implementados

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/api/peers` | Listar todos os peers ativos |
| `GET` | `/api/peer/details?peer_id=<id>` | Obter detalhes de um peer |
| `POST` | `/api/peer/add` | Adicionar peer manualmente |
| `POST` | `/api/peer/edit` | Editar IP/porta de peer |
| `POST` | `/api/peer/remove` | Remover peer administrativamente |

### Exemplo de Requisição (cURL)

#### Adicionar Peer
```bash
curl -X POST http://localhost:8082/api/peer/add \
  -H "Content-Type: application/json" \
  -d '{
    "peer_id": "peer_novo_001",
    "ip": "192.168.1.100",
    "port": 6010
  }'
```

#### Editar Peer
```bash
curl -X POST http://localhost:8082/api/peer/edit \
  -H "Content-Type: application/json" \
  -d '{
    "peer_id": "peer_novo_001",
    "new_ip": "192.168.1.101",
    "new_port": 6011
  }'
```

#### Remover Peer
```bash
curl -X POST http://localhost:8082/api/peer/remove \
  -H "Content-Type: application/json" \
  -d '{
    "peer_id": "peer_novo_001"
  }'
```

#### Ver Detalhes
```bash
curl http://localhost:8082/api/peer/details?peer_id=web-ui
```

---

## 📊 Integração com a Interface

### Feedback Visual

Todas as operações fornecem feedback visual em tempo real:

- ⏳ **Amarelo:** Operação em andamento
- ✅ **Verde:** Sucesso
- ❌ **Vermelho:** Erro

### Log de Operações

Todas as ações são registradas no **Log do Gateway** na interface:

```
[14:32:10] Peer peer_backup_001 adicionado
[14:32:25] Peer peer_52d1f8ae editado
[14:32:40] Detalhes de web-ui carregados
[14:33:15] Erro ao remover peer: Peer não encontrado
```

### Atualização Automática

Após adicionar, editar ou remover peers, a lista de peers ativos é automaticamente atualizada sem necessidade de reload da página.

---

## 🎯 Casos de Uso Práticos

### Caso 1: Adicionar Peer de Backup
```
Cenário: Preparar peer de backup antes de iniciar
Ação: Adicionar peer manualmente
Peer ID: peer_backup_001
IP: 192.168.1.50
Porta: 6010
Resultado: Peer registrado e aguardando conexão
```

### Caso 2: Reconfigurar Rede
```
Cenário: IP do peer mudou após reconfiguração
Ação: Editar peer existente
Peer ID: peer_52d1f8ae
Novo IP: 172.18.0.30
Resultado: Peer atualizado sem perder arquivos
```

### Caso 3: Remover Peer Problemático
```
Cenário: Peer com problema precisa ser removido imediatamente
Ação: Remover peer sem esperar timeout
Peer ID: peer_problem_123
Resultado: Peer removido, re-replicação iniciada
```

### Caso 4: Auditoria de Arquivos
```
Cenário: Verificar quais arquivos um peer específico compartilha
Ação: Ver detalhes do peer
Peer ID: web-ui
Resultado: Lista completa de arquivos exibida
```

---

## 🔒 Segurança e Boas Práticas

### ⚠️ Atenções Importantes

1. **Remoção de Peers:** Pode causar perda de réplicas se o peer for o único detentor de um arquivo
2. **Edição de IP/Porta:** Valores incorretos podem tornar o peer inacessível
3. **Duplicação de IDs:** Não adicione peers com IDs já existentes
4. **Validação de Porta:** Porta deve estar entre 1024 e 65535

### 📝 Recomendações

- **Backup antes de remover:** Verifique réplicas antes de remover peers
- **Validar conectividade:** Teste ping/telnet antes de adicionar peer
- **Usar nomes descritivos:** IDs como `peer_backup_001` são melhores que `peer1`
- **Documentar mudanças:** Registre edições em ambiente de produção

---

## 🧪 Como Testar

### Teste 1: Adicionar e Verificar

1. Acesse `http://localhost:8081`
2. Expanda "Gerenciamento de Peers"
3. Adicione peer com ID `teste_001`, IP `192.168.1.99`, porta `7000`
4. Observe lista de peers atualizada
5. Use "Ver Detalhes" para confirmar

### Teste 2: Editar e Confirmar

1. Edite o peer `teste_001`
2. Mude IP para `192.168.1.100`
3. Confirme que IP foi atualizado na lista

### Teste 3: Remover e Observar

1. Remova o peer `teste_001`
2. Confirme no diálogo
3. Verifique que peer não aparece mais na lista

### Teste 4: Detalhes de Peer Real

1. Consulte detalhes do peer `web-ui`
2. Verifique que informações estão corretas
3. Confirme que arquivos publicados aparecem

---

## 📈 Melhorias Futuras

Possíveis extensões desta funcionalidade:

- **Autenticação:** Login de administrador
- **Histórico de mudanças:** Log de alterações de peers
- **Estatísticas:** Gráficos de uso por peer
- **Notificações:** Alertas quando peer cai
- **Bulk operations:** Adicionar/remover múltiplos peers
- **Import/Export:** Backup de configuração de peers

---

## 🎓 Resumo Técnico

### Arquivos Modificados

1. **`peer/web_gateway.py`**
   - Novos endpoints: `/api/peer/add`, `/api/peer/edit`, `/api/peer/remove`, `/api/peer/details`
   - Validação de parâmetros
   - Tratamento de erros

2. **`hotsite/index.html`**
   - Nova seção de UI para gerenciamento
   - Formulários para cada operação
   - Event listeners para botões
   - Feedback visual e logs

### Fluxo de Dados

```
Interface Web (HTML/JS)
    ↓ HTTP POST/GET
Web Gateway (Python)
    ↓ Chama métodos
NetworkManager (peer/network.py)
    ↓ Envia comandos JSON
Tracker (tracker/tracker.py)
    ↓ Atualiza estruturas
self.peers{} (memória)
```

### Comandos do Tracker Utilizados

- `ADD_PEER` - Adicionar peer
- `EDIT_PEER` - Editar peer  
- `REMOVE_PEER` - Remover peer
- `GET_PEER_DETAILS` - Detalhes completos

---

## ✅ Conclusão

O gerenciamento de peers via interface web torna o sistema **mais acessível e prático** para administradores, permitindo:

- ✅ Operações CRUD completas sem CLI
- ✅ Feedback visual em tempo real
- ✅ Validação de entrada
- ✅ Integração com log do sistema
- ✅ Atualização automática da interface

**Acesse agora:** `http://localhost:8081` e experimente! 🚀
