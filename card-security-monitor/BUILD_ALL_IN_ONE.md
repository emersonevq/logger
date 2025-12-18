# 🚀 Build All-in-One: Tudo em Um Único .exe

## 📊 O que é?

Um executável único que contém:

- ✅ Backend Express (servidor Node.js)
- ✅ Monitor Python (detecção de cartão)
- ✅ Frontend React (interface web)
- ✅ Script Injetor (captura no navegador)
- ✅ Abre navegador automaticamente

**Um clique = Tudo roda!** 🎯

---

## ⚡ Quick Start

### 1. Build

```powershell
cd card-security-monitor
.\build-all-in-one.bat
```

### 2. Execute

```powershell
.\dist\CardSecurityMonitor.exe
```

**Pronto!** Tudo roda automaticamente. 🎉

---

## 📋 O Que o Build Faz

```
[1/7] Verifica Python + Node
     ↓
[2/7] Instala dependências Python
     ↓
[3/7] Compila projeto Node (npm run build)
     → Gera: dist/spa (Frontend compilado)
     → Gera: dist/server (Backend compilado)
     ↓
[4/7] Limpa builds antigos
     ↓
[5/7] Instala PyInstaller
     ↓
[6/7] Compila .exe com PyInstaller
     → Empacota launcher.py + toda a pasta
     → Inclui Backend compilado
     → Inclui Monitor + dependências Python
     ↓
[7/7] Finaliza
     ↓
✅ dist/CardSecurityMonitor.exe pronto!
```

---

## 🧪 O Que Acontece ao Executar

```
CardSecurityMonitor.exe
     │
     ├─→ 🚀 Inicia Backend Express
     │   └─→ Porta: 8080
     │   └─→ Aguarda ficar pronto
     │
     ├─→ 🔒 Inicia Monitor Python
     │   └─→ Monitora teclado
     │   └─→ Conecta ao Backend via WebSocket
     │
     └─→ 🌐 Abre Navegador
         └─→ http://localhost:8080/payment-test
         └─→ Pronto para testar!
```

**Tempo total:** ~10-15 segundos na primeira inicialização

---

## ⚙️ Passos Detalhados

### Passo 1: Verificar Pré-requisitos

```powershell
# Python 3.8+
python --version

# Node.js 18+
node --version

# npm
npm --version
```

Se algum estiver faltando, instale:

- **Python**: https://python.org
- **Node.js**: https://nodejs.org

### Passo 2: Na Raiz do Projeto

```powershell
# Certifique-se que você tem dependências do projeto
npm install
```

### Passo 3: Na Pasta card-security-monitor

```powershell
cd card-security-monitor

# Instale dependências Python (primeira vez)
pip install -r requirements.txt

# Execute o build
.\build-all-in-one.bat
```

### Passo 4: Aguarde

```
[1/7] Verificando dependências...
    ✅ Python 3.11.0
    ✅ Node.js v18.16.0

[2/7] Instalando/Atualizando dependências Python...
    ✅ Dependências Python OK

[3/7] Compilando projeto Node/Express...
    (alguns minutos)
    ✅ Projeto Node compilado

[4/7] Limpando builds anteriores...
    ✅ Limpo

[5/7] Instalando PyInstaller...
    ✅ PyInstaller pronto

[6/7] Compilando executável all-in-one...
    (3-5 minutos)
    ✅ Executável compilado

[7/7] Finalizando...
    ✅ Construção finalizada

✅ BUILD CONCLUÍDO COM SUCESSO!
   📦 Executável: dist\CardSecurityMonitor.exe
```

### Passo 5: Execute o .exe

```powershell
.\dist\CardSecurityMonitor.exe
```

**Ou clique 2x em:**

```
dist/CardSecurityMonitor.exe
```

---

## 📍 Como Usar

### Ao Iniciar

```
[14:30:00] 🚀 Iniciando servidor Backend...
[14:30:01] ✅ Backend iniciado (PID: 1234)
[14:30:02] ℹ️ Aguardando backend ficar pronto...
[14:30:05] ✅ Backend está pronto em http://localhost:8080
[14:30:06] 🔒 Iniciando monitor de cartão...
[14:30:07] ✅ Monitor iniciado (PID: 5678)
[14:30:08] 🌐 Abrindo navegador...
[14:30:09] ✅ Navegador aberto: http://localhost:8080/payment-test

============================================================
✅ SISTEMA PRONTO!
============================================================
Backend:  http://localhost:8080
Monitor:  Rodando em background
Browser:  Aberto automaticamente

Pressione Ctrl+C para encerrar
============================================================
```

### No Navegador

1. Você verá a página de teste
2. Digite dados de cartão
3. Console (F12) mostra detecção em tempo real
4. Quando completo, Monitor mostra alerta

### Para Encerrar

```
Pressione Ctrl+C no console
```

Isso encerra:

- Backend
- Monitor
- Navegador

---

## 🐛 Troubleshooting

### Erro: "Python não encontrado"

```
❌ ERRO: Python não encontrado!
```

**Solução:**

1. Instale Python de https://python.org
2. Marque "Add Python to PATH"
3. Reinicie PowerShell
4. Tente novamente

### Erro: "Node.js não encontrado"

```
❌ ERRO: Node.js não encontrado!
```

**Solução:**

1. Instale Node.js de https://nodejs.org
2. Reinicie PowerShell
3. Tente novamente

### Erro: "Porta 8080 em uso"

```
❌ ERRO: Porta 8080 ainda em uso!
```

**Solução:**

```powershell
# Matar processo usando porta
netstat -ano | findstr :8080
taskkill /PID <PID> /F
```

### Executável não abre

**Verificar:**

1. ✓ Executar como Administrador (direitos elevados)
2. ✓ Antivírus bloqueando? Adicione exceção
3. ✓ Verifique firewall

---

## 📊 Arquitetura do Executável

```
CardSecurityMonitor.exe (~ 200-300 MB)
├── launcher.py (executor principal)
├── main.py (interface monitor)
├── keyboard_monitor.py (monitor de teclado)
├── pattern_detector.py (detector de padrões)
├── alert_window.py (janela de alerta)
├── screenshot_capture.py (captura de tela)
├── websocket.py (gerenciador WebSocket)
├── Python runtime (3.11)
├── Dependências Python (pynput, pywin32, etc)
├── Node.js runtime
├── dist/server/ (Backend compilado)
│   └── node-build.mjs (executável Node)
└── dist/spa/ (Frontend compilado)
    ├── index.html
    └── assets/

Total: ~250-350 MB
```

---

## 🎯 Fluxo Completo

```
CardSecurityMonitor.exe
    ↓
launcher.py executa
    ↓
[1] npm run build → dist/spa + dist/server
    ↓
[2] Inicia Node process → node dist/server/node-build.mjs
    ├── Porta 8080
    ├── Serve dist/spa (Frontend React)
    ├── Serve public/ (arquivos estáticos)
    ├── WebSocket server (ws://localhost:8080/ws)
    └── Endpoints API (/payment-test, /payment-capture, etc)
    ↓
[3] Inicia Python process → python main.py
    ├── Interface Tkinter
    ├── Monitor de teclado
    ├── Conecta ao Backend via WebSocket
    └── Aguarda dados para alertar
    ↓
[4] Abre navegador → http://localhost:8080/payment-test
    ├── Backend injeta script de captura
    ├── Script detecta formulários
    ├── Envia dados via WebSocket para Backend
    └── Backend encaminha para Python
    ↓
[5] Usuário digita dados de cartão
    ├── Script detecta e envia
    ├── Backend recebe e log
    ├── Python recebe e processa
    └── Quando completo → ALERTA + SCREENSHOT
```

---

## 💡 Dicas Úteis

1. **Primeira inicialização demora mais (10-15s)**
   - Próximas vezes são mais rápidas

2. **Pode parecer travado por uns segundos**
   - Node.js está compilando/iniciando
   - Isso é normal!

3. **Se não abrir navegador**
   - Abra manualmente: http://localhost:8080/payment-test

4. **Verifique console para logs**
   - Mosstra tudo que está acontecendo
   - Útil para debug

5. **Ctrl+C encerra tudo**
   - Backend + Monitor + Navegador

---

## 🔒 Segurança

✅ **Nenhum dado é enviado para internet**
✅ **Tudo roda localmente**
✅ **WebSocket criptografável (wss://)**
✅ **Dados nunca são armazenados**
✅ **Processamento local apenas**

---

## 📦 Distribuição

Para distribuir para outros:

```powershell
# Zip o arquivo
dist\CardSecurityMonitor.exe

# Envie o .exe para outras pessoas
# Eles não precisa de Python, Node, ou dependências
# Só executar o .exe!
```

---

## 🎓 Próximas Melhorias Possíveis

- [ ] Ícone customizado (.ico)
- [ ] Splash screen na inicialização
- [ ] Build para macOS/Linux
- [ ] Versão portable (sem instalação)
- [ ] Auto-update automático
- [ ] Múltiplas idiomas

---

## 📞 Suporte

Se algo não funcionar:

1. **Verifique pré-requisitos**
   - Python 3.8+
   - Node.js 18+

2. **Limpe e reconstrua**

   ```powershell
   rmdir /s /q dist build
   del *.spec
   .\build-all-in-one.bat
   ```

3. **Consulte DEBUG.md e SETUP_COMPLETO.md**

---

## 🎯 Resumo

```
1. .\build-all-in-one.bat      (5-10 minutos)
2. .\dist\CardSecurityMonitor.exe  (clique 2x)
3. 🎉 Tudo funciona automaticamente!
```

**É isso!** Um executável, tudo incluído, funciona em qualquer Windows! 🚀

---

**Criado com ❤️ para facilitar sua vida** 🔒
