# 🚀 Setup Completo: Backend Express + Monitor Python

## 📋 O que é Este Guia?

Este guia mostra como executar **TUDO JUNTO**:

- ✅ Backend Express (Node.js/TypeScript)
- ✅ Monitor Python (.exe)
- ✅ Navegador para testes

---

## 🎯 Fluxo Completo

```
┌──────────────────────────────────────────────────┐
│ 1. Backend Express (npm run dev)                 │
│    → Porta: 8080                                 │
│    → WebSocket: ws://localhost:8080/ws           │
│    → Injeta script no navegador                  │
└──────────────────────────────────────────────────┘
                      ↓
┌──────────────────────────────────────────────────┐
│ 2. Monitor Python (python main.py)               │
│    → Conecta ao backend via WebSocket            │
│    → Monitora teclado globalmente                │
│    → Aguarda dados completos                     │
└──────────────────────────────────────────────────┘
                      ↓
┌──────────────────────────────────────────────────┐
│ 3. Navegador (http://localhost:8080/...)        │
│    → Acessa página de teste                      │
│    → Recebe script injetor do backend            │
│    → Digita dados de cartão                      │
│    → Script captura e envia ao backend           │
└──────────────────────────────────────────────────┘
                      ↓
┌──────────────────────────────────────────────────┐
│ 4. Backend Recebe → Encaminha para Python        │
│    → Via WebSocket                               │
│    → Python .exe mostra alerta                   │
│    → Captura screenshot                          │
└──────────────────────────────────────────────────┘
```

---

## ⚡ Quick Start (3 Terminais)

### **TERMINAL 1: Backend Express**

```powershell
# Na raiz do projeto
npm install  # (primeira vez apenas)
npm run dev
```

**Esperado:**

```
✨ ready in 310 ms
🚀 Fusion Starter server running on port 8080
📱 Frontend: http://localhost:8080
🔗 WebSocket: ws://localhost:8080/ws
```

---

### **TERMINAL 2: Monitor Python**

```powershell
# Navegue até a pasta
cd card-security-monitor

# Instale dependências (primeira vez)
pip install -r requirements.txt

# Execute
python main.py
```

**Esperado:**

```
🚀 Iniciando monitor de teclado...
✅ Monitor de teclado iniciado com sucesso
🔄 Tentando conectar ao backend (1)...
✅ Conectado ao backend: ws://localhost:8080/ws
```

---

### **TERMINAL 3 (OPCIONAL): Navegador**

Abra seu navegador em qualquer uma das URLs:

**Opção A: Página de teste simples**

```
http://localhost:8080/payment-capture
```

**Opção B: Página de teste com formulário customizado**

```
http://localhost:8080/
```

---

## 📊 O Que Acontece Quando Você Digita

```
1. Você abre o navegador
   ↓
2. Backend injeta script de captura
   ↓
3. Script monitora todos os inputs
   ↓
4. Você digita dados de cartão
   ↓
5. Script detecta padrão
   ↓
6. Script envia para backend via WebSocket
   ↓
7. Backend registra no console
   ↓
8. Backend encaminha para Python via WebSocket
   ↓
9. Python .exe recebe dados
   ↓
10. Quando tudo está completo (cartão + validade + CVV)
    → Python mostra alerta com screenshot
```

---

## ✅ Checklist de Instalação

### Primeira Execução

- [ ] Node.js 18+ instalado (`node --version`)
- [ ] Python 3.8+ instalado (`python --version`)
- [ ] Na raiz: `npm install` ✅
- [ ] Na pasta Python: `pip install -r requirements.txt` ✅

### Executando

- [ ] Terminal 1: `npm run dev` rodando
- [ ] Terminal 2: `python main.py` rodando
- [ ] Navegador: Abrindo http://localhost:8080/payment-capture
- [ ] Console mostra: ✅ Conectado ao backend

---

## 🧪 Teste Prático

### Passo 1: Prepare os Terminais

```
Terminal 1: npm run dev                     (rodando)
Terminal 2: cd card-security-monitor && python main.py  (rodando)
```

### Passo 2: Clique "Iniciar Monitor" (Terminal 2)

Você verá:

```
✅ Monitorando navegadores...
```

### Passo 3: Abra o Navegador

```
http://localhost:8080/payment-capture
```

### Passo 4: Digite Dados de Teste

Use dados VÁLIDOS (que passam na validação Luhn):

```
Número do Cartão: 4532015112830366
Data de Validade: 12/25
CVV: 123
```

### Passo 5: Observe os Logs

**Terminal 1 (Backend):**

```
📊 Dados de formulário recebidos: {
  cardNumber: ✅
  expiryMonth: ✅
  expiryYear: ✅
  cvv: ✅
}
```

**Terminal 2 (Python):**

```
🚨 [14:32:45] ALERTA: Dados completos detectados!
   Cartão: 4532 •••• •••• 0366
   Bandeira: Visa
   Janela: Payment Capture - Google Chrome
```

---

## 📁 Estrutura de Pastas

```
projeto/
├── server/
│   ├── index.ts              # Express app
│   ├── websocket.ts          # WebSocket manager
│   └── routes/
│       ├── payment-proxy.ts  # Injetor de script
│       └── ...
├── public/
│   └── card-capture-injector.js  # ⭐ Script injetor
├── card-security-monitor/
│   ├── main.py               # Interface principal
│   ├── keyboard_monitor.py   # Monitor de teclado
│   ├── pattern_detector.py   # Detector de padrões
│   └── requirements.txt      # Dependências Python
└── npm modules/
    └── (dependências Node)
```

---

## 🔧 Troubleshooting

### "Porta 8080 já está em uso"

```powershell
# Encontre qual processo está usando:
netstat -ano | findstr :8080

# Mate o processo:
taskkill /PID <PID> /F

# Ou use outra porta (mude em package.json)
```

### "WebSocket não conecta"

1. Verifique se Terminal 1 está rodando
2. Verifique se você vê "WebSocket: ws://localhost:8080/ws"
3. Verifique console do navegador (F12 > Console)

### "Dados não aparecem no Python"

1. Certifique-se que você digitou dados **válidos**
2. Use o número de teste: `4532015112830366`
3. Verifique se o script foi injetado (F12 > Console no navegador)

### "Script não foi injetado"

1. Abra Console do navegador (F12)
2. Procure por: `✅ Script de captura injetado com sucesso!`
3. Se não aparecer, verifique Terminal 1 (pode estar erro no backend)

---

## 🚀 Executar com .exe (Depois)

Após testar em modo Python, você pode compilar para .exe:

```powershell
cd card-security-monitor
.\build.bat
.\dist\CardSecurityMonitor.exe
```

E manter o Terminal 1 (`npm run dev`) rodando.

---

## 📊 Arquitetura Simplificada

```
┌─────────────────────────────────────────────────────────┐
│                    NAVEGADOR                            │
│  [Formulário] ← (script injetado pelo backend)          │
│  └─→ WebSocket.send(cardData) → Backend                │
└─────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────┐
│              BACKEND EXPRESS (node-build)               │
│  WebSocket Server (ws://localhost:8080/ws)              │
│  ├─ Recebe: CARD_DATA_UPDATE (navegador)               │
│  └─ Envia: cardData → Python Monitor                   │
└─────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────┐
│         MONITOR PYTHON (card-security-monitor)          │
│  ├─ Monitora teclado global                            │
│  ├─ Detecta padrões (Luhn, CPF, etc)                   │
│  └─ Mostra ALERTA quando completo                      │
└─────────────────────────────────────────────────────────┘
```

---

## 🎓 Como o Script Injetor Funciona

1. **Backend recebe requisição** (GET /payment-capture)
2. **Backend busca página real** (ou teste)
3. **Backend injeta script** no final do `</head>`
4. **Script conecta ao WebSocket** quando página carrega
5. **Script monitora todos os inputs**
6. **Quando valor é detectado**:
   - Script valida (regex patterns)
   - Script envia para backend via WebSocket
   - Backend encaminha para Python
   - Python processa e alerta

---

## 📞 Dúvidas Frequentes

**P: O backend precisa estar rodando?**
R: SIM! Se não rodar, Python não consegue conectar.

**P: Posso usar Chrome/Firefox/Edge?**
R: SIM! Qualquer navegador moderno funciona.

**P: Os dados são enviados para algum servidor?**
R: NÃO! Tudo fica local: Navegador ↔ Backend ↔ Python

**P: Preciso de Internet?**
R: NÃO! Tudo é localhost:8080

**P: O que é a porta 8080?**
R: É onde o Backend Express roda. Backend serve o Frontend, WebSocket e Script Injetor tudo na mesma porta.

---

## 🔒 Fluxo de Segurança

```
Navegador                    Backend                  Python
   │                          │                         │
   ├─ GET /payment-capture    │                         │
   │────────────────────────→ │                         │
   │                          ├─ Injeta script         │
   │ HTML + Script ←──────────┤                         │
   │                          │                         │
   ├─ Script conecta WS       │                         │
   │─────────────────────────→│─ Nova conexão           │
   │                          ├──→ Python (via WS)      │
   │                          │ ← ACK                   │
   │                          │                         │
   ├─ Digita: 4532...         │                         │
   ├─ Script detecta          │                         │
   ├─ Script envia WS         │                         │
   │─────────────────────────→│─ Recebe dados           │
   │                          ├──→ Envia Python        │
   │                          │ ← Recebe                │
   │                          │                         │
   │                          │ ← ALERTA no Python!    │
   │                          │    Screenshot           │
   │                          │    Dados mascarados     │
   │                          │    Validação Luhn ✅   │
```

---

## 🎯 Resumo Final

Para rodar TUDO:

```powershell
# Terminal 1
npm run dev

# Terminal 2
cd card-security-monitor && pip install -r requirements.txt && python main.py

# Browser
http://localhost:8080/payment-capture
```

É isso! O backend cuida de injetar o script, Python cuida de monitorar, e o navegador captura os dados. Tudo junto, tudo comunicando via WebSocket. 🚀

---

**Próximas funcionalidades possíveis:**

- [ ] Dashboard em tempo real
- [ ] Histórico de detecções
- [ ] Integração com extensão de navegador
- [ ] API REST para consultas
- [ ] Banco de dados para logs

---

**Criado com ❤️ para sua segurança** 🔒
