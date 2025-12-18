# 🔍 Guia de Debug e Troubleshooting

## 📋 Índice

1. [Checklist Rápido](#checklist-rápido)
2. [Problemas Comuns](#problemas-comuns)
3. [Como Debugar](#como-debugar)
4. [Logs e Erros](#logs-e-erros)
5. [Testes](#testes)
6. [Restaurar Padrões](#restaurar-padrões)

---

## ✅ Checklist Rápido

Use este checklist para verificar se tudo está configurado corretamente:

### Antes de Executar

- [ ] Python 3.8+ instalado
- [ ] Python adicionado ao PATH (teste com `python --version`)
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] .exe gerado com sucesso (`.\build.bat`)
- [ ] Executando como **Administrador**
- [ ] Antivírus não está bloqueando

### Durante a Execução

- [ ] Janela principal aparece
- [ ] Botão "▶ Iniciar" está visível
- [ ] Clicou em "▶ Iniciar Monitor"
- [ ] Status mostra "✅ Monitorando navegadores..."
- [ ] Console mostra mensagens sem erros

### Com Navegador Aberto

- [ ] Navegador ativo (Chrome, Firefox, Edge, etc)
- [ ] Você está digitando em um campo de formulário
- [ ] Digitou número de cartão válido (16 dígitos, passa Luhn)
- [ ] Digitou data de validade (MM/AA)
- [ ] Digitou CVV (3 dígitos)
- [ ] Aguardou 1-2 segundos após digitar tudo

---

## 🐛 Problemas Comuns

### 1. "Python não encontrado"

**Sintoma:** Erro ao executar `build.bat` ou `python main.py`

**Causa:** Python não instalado ou não está no PATH

**Solução:**

```powershell
# Verificar se Python está instalado
python --version

# Se não encontrar:
# 1. Baixe Python: https://python.org
# 2. Instale com "Add Python to PATH" marcado
# 3. Reinicie PowerShell e tente novamente
```

---

### 2. "Módulo não encontrado"

**Sintoma:**

```
ModuleNotFoundError: No module named 'pynput'
```

**Causa:** Dependências não instaladas

**Solução:**

```powershell
# Reinstalar todas as dependências
pip install -r requirements.txt --force-reinstall

# Ou instalar individual:
pip install pynput pywin32 psutil Pillow pystray websockets
```

---

### 3. "Permissão negada"

**Sintoma:** Erro ao tentar instalar pacotes ou executar

**Causa:** PowerShell sem permissão de administrador

**Solução:**

```powershell
# 1. Abra PowerShell como Administrador:
#    Win + X > Terminal (Admin)
#    ou
#    clique direito no PowerShell > "Executar como administrador"

# 2. Depois tente novamente
pip install -r requirements.txt
```

---

### 4. "Programa abre mas não funciona"

**Sintomas:**

- Janela abre
- Monitor está "parado" ou mostra erro
- Nenhuma detecção acontece
- Console vazio ou cheio de erros

**Possíveis causas:**

1. **Dependências não carregadas corretamente no .exe**
   - Recrie: `.\build.bat`
   - Execute como Administrador

2. **win32 não funcionando**

   ```powershell
   pip install pywin32 --force-reinstall
   python -m pip install pywin32 --upgrade --force-reinstall
   pywin32_postinstall -install
   ```

3. **Antivírus bloqueando**
   - Verifique logs do antivírus
   - Adicione exceção para CardSecurityMonitor.exe
   - Temporariamente desative para testar

4. **Sem privilégios de administrador**
   - Sempre execute como Admin
   - Clique direito > "Executar como administrador"

---

### 5. "Nenhuma detecção acontece"

**Checklist:**

```
□ Monitor iniciado? (Status: ✅ Monitorando)
   └─ Se não: Clique em "▶ Iniciar Monitor"

□ Navegador em foco? (Chrome, Firefox, Edge, etc)
   └─ Se não: Clique na janela do navegador

□ Digitando em campo? (input, textarea, etc)
   └─ Se não: Clique em um campo de formulário

□ Dados são válidos?
   └─ Cartão: Deve passar na validação Luhn
   └─ CPF: 11 dígitos válidos (se digitando)
   └─ Validade: MM/AA ou MM/AAAA

□ Aguardou tempo suficiente?
   └─ Aguarde 1-2 segundos após digitar tudo
   └─ Ou mude para outro campo
```

**Testes de dados:**

```
Número do cartão válido:  4532015112830366
Data de Validade:         12/25
CVV:                      123
Nome:                     JOÃO SILVA
CPF:                      12345678901 (use um válido)
```

---

### 6. "Antivírus bloqueia o .exe"

**Normal!** Programas compilados com PyInstaller frequentemente recebem alertas falsos.

**Solução:**

```
1. Clique em "Mais informações"
2. Clique em "Executar mesmo assim"
3. Ou adicione exceção no antivírus
4. Ou desative temporariamente para testar
```

---

### 7. "WebSocket não conecta"

**Sintoma:** Console mostra `❌ Erro de conexão WebSocket`

**Causa:** Backend Express não está rodando

**Nota:** Isso é NORMAL se você não está usando o backend.
O programa ainda funciona para monitorar localmente!

**Solução:**

```powershell
# Se quer usar WebSocket com Backend:
# 1. Na raiz do projeto:
npm run dev
# 2. Depois execute o Python app

# Se não quer usar Backend:
# Apenas use o programa normalmente,
# a detecção local continua funcionando!
```

---

## 🔧 Como Debugar

### Modo Desenvolvimento (com console visível)

```powershell
# 1. Abra PowerShell na pasta do projeto
cd C:\caminho\para\card-security-monitor

# 2. Execute com Python diretamente (não o .exe)
python main.py

# 3. Você verá as mensagens de debug no console
```

### Mensagens de Debug Esperadas

Quando você clica em "▶ Iniciar Monitor":

```
🚀 Iniciando monitor de teclado...
✅ Monitor de teclado iniciado com sucesso
🚀 Conectando ao backend Express...
🔄 Tentando conectar ao backend (1)...
❌ Conexão recusada. Servidor não disponível?
⏳ Tentando reconectar em 5 segundos...

(Isso é NORMAL se o backend não está rodando)
```

Quando você digita em um navegador:

```
✅ Monitor de teclado iniciado (aguardando dados completos)
```

Quando detecta uma completa:

```
============================================================
🚨 [14:32:45] ALERTA: Dados completos detectados!
   Cartão: 4532 •••• •••• 0366
   Bandeira: Visa
   Janela: Pagamento - Google Chrome
============================================================
```

---

## 📊 Logs e Erros

### Onde ver logs?

**No desenvolvimento:**

- Console PowerShell mostra mensagens em tempo real

**No .exe:**

- Abra PowerShell e execute: `.\CardSecurityMonitor.exe`
- Você verá os logs no mesmo PowerShell

### Mensagens Importantes

| Mensagem                                     | Significa                     | Ação            |
| -------------------------------------------- | ----------------------------- | --------------- |
| ✅ Monitor de teclado iniciado               | Teclado está sendo monitorado | Tudo OK         |
| ⚠️ Aviso: win32 não disponível               | Modo compatível ativado       | OK (compatível) |
| ❌ Erro ao obter janela ativa                | Win32 falhou                  | Reinicie app    |
| 🔄 Tentando conectar ao backend              | Procurando Express server     | Aguarde/OK      |
| ✅ Conectado ao backend                      | WebSocket funcionando         | Ótimo!          |
| ❌ Conexão recusada. Servidor não disponível | Backend não está rodando      | OK (opcional)   |
| 🚨 ALERTA: Dados completos detectados!       | **Cartão foi detectado!**     | **Verifique!**  |

---

## 🧪 Testes

### Teste 1: Verificar Instalação

```powershell
# Execute isto:
python -c "import pynput, pywin32, psutil, PIL, pystray; print('✅ Todas as dependências OK')"

# Deve mostrar:
# ✅ Todas as dependências OK
```

### Teste 2: Executar em Modo Desenvolvimento

```powershell
# Vai mostrar logs detalhados:
python main.py

# Você verá mensagens como:
# ✅ Monitor de teclado iniciado
# 🚀 Iniciando monitor de teclado...
```

### Teste 3: Teste com Dados Válidos

Use dados de teste conhecidos:

```
Número:   4532015112830366  (Visa válido)
Data:     12/25
CVV:      123
Nome:     JOÃO DA SILVA
CPF:      12345678901       (não valide se estiver testando)
```

### Teste 4: Teste de Navegador

```
1. Abra browser (Chrome, Firefox, Edge)
2. Abra DevTools (F12)
3. Vá para aba "Console"
4. Inicie o monitor
5. Digite em um campo
6. Verifique se aparece mensagens de detecção
```

---

## 🔄 Restaurar Padrões

### Reiniciar do Zero

Se algo der muito errado:

```powershell
# 1. Limpar tudo
rmdir /s /q build
rmdir /s /q dist
del *.spec

# 2. Reinstalar dependências
pip install -r requirements.txt --force-reinstall

# 3. Reconstruir
.\build.bat

# 4. Executar
.\dist\CardSecurityMonitor.exe
```

### Resetar Configurações

```powershell
# Para remover auto-inicialização:
# Menu Windows > Inicialização > Desabilitar CardSecurityMonitor

# Ou execute:
python .\uninstall.bat
```

### Limpar Cache Python

```powershell
# Remover bytecode
rmdir /s /q __pycache__

# Remover cache pip
pip cache purge

# Reinstalar
pip install -r requirements.txt
```

---

## 📞 Se Nada Funcionar

### Coleta de Informações

Quando reportar um problema, recolha:

```powershell
# 1. Versão do Python
python --version

# 2. Versão do Windows
wmic os get caption

# 3. Status das dependências
pip list | find "pynput"

# 4. Logs da execução
python main.py 2>&1 | Out-File -FilePath debug.log

# 5. Informações do sistema
systeminfo > systeminfo.txt
```

### Passos de Debug Finais

1. **Abra Console PowerShell como Admin**
2. **Navegue até a pasta:**

   ```powershell
   cd C:\caminho\para\card-security-monitor
   ```

3. **Execute em modo debug:**

   ```powershell
   python main.py
   ```

4. **Note todas as mensagens que aparecem**

5. **Abra um navegador e tente digitar**

6. **Observe os erros no console**

7. **Se houver erro, copie a mensagem completa**

---

## 🎓 Entendendo o Fluxo

```
┌─────────────────────────────────────────┐
│     Você executa CardSecurityMonitor    │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  Interface Tkinter aparece              │
│  Status: ⏸️ Monitor parado               │
└────────────────┬────────────────────────┘
                 │
                 ▼ (Você clica em ▶ Iniciar)
┌─────────────────────────────────────────┐
│  KeyboardMonitor.start()                │
│  ✅ Escutando teclas no sistema         │
│  WebSocketInjector.start()              │
│  🔄 Tentando conectar ao backend        │
└────────────────┬────────────────────────┘
                 │
                 ▼ (Você abre navegador e digita)
┌─────────────────────────────────────────┐
│  on_key_press() é chamado para cada     │
│  tecla digitada                          │
│  PatternDetector.add_character(char)    │
└────────────────┬────────────────────────┘
                 │
                 ▼ (Periodicamente)
┌─────────────────────────────────────────┐
│  analyze() procura padrões              │
│  ✅ Cartão detectado?                   │
│  ✅ Validade detectada?                 │
│  ✅ CVV detectado?                      │
└────────────────┬────────────────────────┘
                 │
         NÃO    ┌─────────┐    SIM
                 │         │
                 ▼         ▼
            Aguardar   🚨 ALERTA!
                       on_card_detected()
                       └─> AlertWindow.show()
                       └─> Screenshot
                       └─> Som de alerta
```

---

## 💡 Dicas Úteis

1. **Sempre use Administrador** - Win32 precisa de privilégios
2. **Verifique Firewall** - Pode bloquear conexões
3. **Teste sem WebSocket primeiro** - Localmente funciona
4. **Use dados válidos** - Luhn validation é obrigatória
5. **Aguarde a detecção** - Não é instantâneo, leva 1-2 seg
6. **Verifique Antivírus** - Blocos silenciosos são comuns

---

## 📚 Referências

- [pynput docs](https://pynput.readthedocs.io/)
- [pywin32 docs](https://pypi.org/project/pywin32/)
- [psutil docs](https://psutil.readthedocs.io/)
- [Pillow docs](https://pillow.readthedocs.io/)
- [Luhn Algorithm](https://en.wikipedia.org/wiki/Luhn_algorithm)

---

**Boa sorte! 🍀 Se tiver dúvidas, revise este guia. 🔒**
