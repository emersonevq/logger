# 🔒 Credit Card Security Monitor v2.0

## Guia Completo em Português

---

## 📚 Índice

1. [O que é?](#o-que-é)
2. [Funcionalidades](#funcionalidades)
3. [Instalação e Uso](#instalação-e-uso)
4. [Gerar o .exe](#gerar-o-exe)
5. [Solução de Problemas](#solução-de-problemas)
6. [Perguntas Frequentes](#perguntas-frequentes)

---

## O que é?

Um **monitor de segurança inteligente** que:

- ✅ Detecta quando você digita dados de cartão de crédito
- ✅ Valida se os números são reais (usando algoritmo de Luhn)
- ✅ Aguarda você completar O FORMULÁRIO INTEIRO
- ✅ Mostra um alerta com screenshot no exato momento
- ✅ NÃO armazena ou envia seus dados em lugar nenhum

### Proteção contra:

- 🚨 Phishing (sites falsos)
- 🚨 Formulários inseguros
- 🚨 Roubo de dados
- 🚨 Digitação acidental em sites inseguros

---

## Funcionalidades

### 5 Campos Monitorados

1. **💳 Número do Cartão** (16 dígitos)
   - Valida com algoritmo de Luhn
   - Detecta bandeira (Visa, Mastercard, etc)
2. **📅 Data de Validade** (MM/AA ou MM/AAAA)
   - Exemplo: 12/25 ou 12/2025
3. **🔐 CVV** (3-4 dígitos)
   - Código de segurança do cartão
4. **👤 Nome do Titular**
   - Mínimo 2 palavras
5. **📄 CPF** (11 dígitos)
   - Valida com algoritmo oficial brasileiro

### Alerta Somente Quando Tudo Está Pronto

O monitor **NÃO alerta** se você digitar parcialmente. Ele só mostra a janela de alerta quando:

- ✅ Cartão detectado
- ✅ Validade detectada
- ✅ CVV detectado

Os outros 2 campos (nome e CPF) são opcionais para o alerta.

---

## Instalação e Uso

### Opção 1: Executar com Python (Modo Desenvolvimento)

**Pré-requisito:** Python 3.8+ instalado

#### Passo 1: Abrir PowerShell/CMD

Windows 11/10:

- Pressione `Win + X`
- Selecione **"Terminal"** ou **"PowerShell"**

#### Passo 2: Navegar para a pasta

```powershell
cd C:\caminho\da\pasta\card-security-monitor
```

#### Passo 3: Instalar dependências

```powershell
pip install -r requirements.txt
```

Você verá mensagens tipo:

```
Collecting pynput...
Collecting Pillow...
Installing collected packages...
Successfully installed...
```

#### Passo 4: Executar

```powershell
python main.py
```

Uma janela aparecerá! 🎉

### Opção 2: Gerar .exe (Sem precisar Python)

Veja a seção **"Gerar o .exe"** abaixo.

---

## Gerar o .exe

### Por que gerar .exe?

- ✅ Não precisa Python instalado
- ✅ Um único arquivo executável
- ✅ Fácil de distribuir
- ✅ Melhor para usar no Windows

### Passo a Passo

#### **PASSO 1: Instalar Python** (se não tiver)

1. Baixe em: https://www.python.org/downloads/
2. Execute o instalador
3. **✅ IMPORTANTE**: Marque "Add Python to PATH"
4. Clique em "Install Now"

Verifique se funcionou:

- Abra PowerShell
- Digite: `python --version`
- Deve aparecer algo como: `Python 3.11.0`

#### **PASSO 2: Abrir PowerShell como Admin**

1. Pressione `Win + X`
2. Selecione **"Terminal (Admin)"** ou **"PowerShell (Admin)"**
3. Clique em "Sim" se pedir permissão

#### **PASSO 3: Navegar para a pasta**

```powershell
cd C:\caminho\da\pasta\card-security-monitor
```

Exemplo completo:

```powershell
cd C:\Users\SEU_USUARIO\Downloads\card-security-monitor
```

#### **PASSO 4: Executar build.bat (Automático)**

Opção A - **RECOMENDADO** (mais fácil):

Abra a pasta do projeto no Windows Explorer e **clique duas vezes** em `build.bat`

Opção B - Manual via PowerShell:

```powershell
.\build.bat
```

Você verá:

```
[1/4] Verificando Python...
Python 3.11.0
[2/4] Instalando dependências...
[3/4] Compilando executável...
[4/4] Limpando arquivos temporários...
✅ BUILD CONCLUÍDO COM SUCESSO!
Executável: dist\CardSecurityMonitor.exe
```

#### **PASSO 5: Encontrar o .exe**

O arquivo estará em:

```
card-security-monitor/dist/CardSecurityMonitor.exe
```

Você pode:

- ✅ Clicar 2x para executar
- ✅ Copiar para Desktop
- ✅ Criar atalho
- ✅ Colocar na pasta de Inicialização do Windows

---

## Como Usar a Aplicação

### Iniciando

1. Execute `CardSecurityMonitor.exe` (ou `python main.py`)
2. Uma janela aparecerá com botões e campos

### Interface Principal

```
┌─────────────────────────────────────────┐
│  🔒 Credit Card Security Monitor        │
│                                         │
│  Status: ⏸️ Monitor parado              │
│                                         │
│  [▶ Iniciar Monitor]  [⏹ Parar]        │
│                                         │
│  📋 Campos detectados em tempo real:    │
│  ⬜ 💳 Número do Cartão                │
│  ⬜ 📅 Data de Validade                │
│  ⬜ 🔐 CVV                             │
│  ⬜ 👤 Nome do Titular                 │
│  ⬜ 📄 CPF                             │
│                                         │
│  Progresso: [░░░░░░░░░░░░░] 0%          │
└─────────────────────────────────────────┘
```

### Usando o Monitor

**Passo 1: Clicar em "▶ Iniciar Monitor"**

A interface muda para:

```
Status: ✅ Monitorando navegadores...
```

**Passo 2: Abrir um navegador** (Chrome, Firefox, Edge, etc)

**Passo 3: Acessar um formulário de pagamento**

O monitor detecta automaticamente quando você está em uma página com formulário.

**Passo 4: Preencher os campos**

Conforme você digita:

- Os campos vão ficando ✅ (verde)
- A barra de progresso sobe
- O monitor conta em tempo real

**Passo 5: Quando tudo está preenchido**

Uma janela de alerta aparece mostrando:

- 💳 Seu cartão (mascarado) - Últimos 4 dígitos visíveis
- 📅 Validade que você digitou
- 🔐 CVV mascarado (\*\*\*)
- 👤 Nome do titular
- 📄 CPF (mascarado)
- 📸 Screenshot exato do navegador

**Passo 6: Verificar se é seguro**

A janela pede para você confirmar:

- ✓ O site tem HTTPS? (cadeado verde)
- ✓ É o site oficial?
- ✓ Você confia neste site?

Clique em:

- **"✓ Verifiquei, é seguro continuar"** - Se tudo está OK
- **"🛑 Não tenho certeza - PARAR"** - Se algo parecer errado

---

## Solução de Problemas

### Problema: "Python não encontrado"

**Solução:**

1. Baixe Python em: https://www.python.org/downloads/
2. **IMPORTANTE**: Marque "Add Python to PATH" na instalação
3. Reinicie o PowerShell
4. Tente novamente

### Problema: "Permissão negada"

**Solução:**

- Execute PowerShell como **Administrador** (Win + X > Terminal Admin)

### Problema: "módulo não encontrado"

**Erro:**

```
ModuleNotFoundError: No module named 'pynput'
```

**Solução:**

```powershell
pip install -r requirements.txt
```

### Problema: O executável não funciona

**Tente:**

1. Execute como Administrador (clique direito > Executar como administrador)
2. Verifique antivírus (alguns bloqueiam .exe gerado)
3. Recrie o .exe: `.\build.bat`

### Problema: Monitor não detecta nada

**Verificar:**

1. ✓ Monitor está iniciado? (Status mostra "✅ Monitorando")
2. ✓ Você está em um navegador? (Chrome, Firefox, Edge, etc)
3. ✓ A digitação está sendo feita no campo de formulário?
4. ✓ Você digitou dados **válidos**? (cartão que passa Luhn, CPF válido)

**Teste:**
Tente digitar dados de teste:

- Número: `4532015112830366` (número válido de teste)
- Validade: `12/25`
- CVV: `123`

### Problema: Antivírus bloqueia o .exe

**Normal!** Programas compilados com PyInstaller às vezes recebem alertas falsos.

**Soluções:**

1. Adicione à "exceção" do antivírus
2. Desative temporariamente para testes
3. Confie no programa (ele foi criado localmente)

---

## Perguntas Frequentes

### P: Meus dados são enviados para alguém?

**R:** NÃO! Tudo é processado localmente no seu computador. Nada é enviado.

### P: O monitor grava minha digitação?

**R:** NÃO! O buffer é limpado após o alerta. Apenas detecta os padrões.

### P: Posso confiar neste programa?

**R:** SIM! O código-fonte está disponível. Você pode revisar tudo.

### P: Funciona em Mac/Linux?

**R:** Principalmente em Windows. Mac/Linux requerem adaptações.

### P: O que é o algoritmo de Luhn?

**R:** Validação matemática de números de cartão. Detecta erros de digitação.

### P: Como diferencio um cartão válido de inválido?

**R:**

- **Válido:** Passa na validação Luhn + 16 dígitos
- **Inválido:** Falha na validação ou dígitos errados

### P: Qual é o CPF de teste?

**R:** Não existe CPF válido de teste. Use um CPF real para testes.

### P: Posso usar em redes Wi-Fi públicas?

**R:** Não recomendado. Mesmo com monitor, a rede pode interceptar.

### P: O monitor consome muitos recursos?

**R:** NÃO! Usa menos de 50MB de RAM.

---

## 📋 Checklist de Instalação

- [ ] Python 3.8+ instalado
- [ ] Python adicionado ao PATH
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] .exe gerado com sucesso (`.\build.bat`)
- [ ] Arquivo em `dist\CardSecurityMonitor.exe`
- [ ] Executável testado
- [ ] Sem erros de antivírus

---

## 🎯 Resumo de Uso

```
1️⃣  Instale Python
        ↓
2️⃣  pip install -r requirements.txt
        ↓
3️⃣  .\build.bat
        ↓
4️⃣  Execute dist\CardSecurityMonitor.exe
        ↓
5️⃣  Clique "Iniciar Monitor"
        ↓
6️⃣  Acesse um site de pagamento
        ↓
7️⃣  O monitor alertará quando formulário estiver completo
```

---

## 📞 Suporte

Se tiver problemas:

1. **Verifique o console** - Aparecem mensagens de erro?
2. **Reinstale dependências** - `pip install -r requirements.txt --force-reinstall`
3. **Recrie o .exe** - `.\build.bat`
4. **Verifique antivírus** - Desative temporariamente

---

## 📄 Informações Técnicas

### Arquivos Principais

- **main.py** - Interface gráfica (Tkinter)
- **keyboard_monitor.py** - Monitor de teclado
- **pattern_detector.py** - Detector de padrões com Luhn/CPF
- **alert_window.py** - Janela de alerta com screenshot
- **screenshot_capture.py** - Captura de tela
- **build.bat** - Script para gerar .exe

### Dependências

```
pynput          - Monitor de teclado
Pillow          - Manipulação de imagens
pywin32         - APIs do Windows
psutil          - Informações do sistema
PyInstaller     - Gerador de .exe
```

---

## 🔒 Privacidade

✅ **Nenhum dado é enviado**
✅ **Processamento local apenas**
✅ **Sem conexão com internet obrigatória**
✅ **Código-fonte disponível para revisar**
✅ **Desenvolvimento aberto**

---

## 📅 Versão

- **Versão:** 2.0
- **Data:** 2024
- **Status:** Completo e testado

---

## 🎓 Educacional

Este projeto demonstra:

- Monitoramento de entrada do usuário
- Validação de dados financeiros
- Processamento de padrões com regex
- Desenvolvimento de interfaces gráficas em Python
- Empacotamento de aplicações Python

Use para aprender e se proteger!

---

**Criado com ❤️ para sua segurança**
