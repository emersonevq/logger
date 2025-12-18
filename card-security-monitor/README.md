# 🔒 Credit Card Security Monitor v2.1

## Monitor de Segurança Inteligente para Cartão de Crédito

Um programa que protege você contra phishing e digitação insegura de dados de cartão, detectando quando você digita informações sensíveis e alertando antes que complete a transação.

---

## ✨ Funcionalidades Principais

✅ **Detecção Inteligente** - Valida padrões de cartão com algoritmo de Luhn  
✅ **Alerta Completo** - Só notifica quando TODOS os dados estão preenchidos  
✅ **Screenshot Automático** - Captura a tela do navegador no momento da detecção  
✅ **Auto-Inicialização** - Inicia automaticamente com o Windows  
✅ **Bandeja do Sistema** - Executa discretamente em segundo plano  
✅ **100% Local** - Nenhum dado é enviado para servidores  
✅ **Interface Amigável** - Mostra progresso em tempo real

---

## 🚀 Começando Rápido

### Opção 1: Usar o Executável (Recomendado)

1. **Baixar/Clonar** este repositório
2. **Abrir PowerShell** como Administrador
3. **Executar**:
   ```powershell
   cd caminho\da\pasta\card-security-monitor
   .\build.bat
   ```
4. **Instalar**:
   ```powershell
   cd dist
   .\CardSecurityMonitor.exe
   ```

### Opção 2: Modo Desenvolvimento (com Python)

```powershell
# Instalar Python 3.8+
# Depois:
pip install -r requirements.txt
python main.py
```

---

## 📋 O que Monitora

| Campo                   | Descrição                 | Exemplo             |
| ----------------------- | ------------------------- | ------------------- |
| 💳 **Número do Cartão** | 16 dígitos válidos (Luhn) | 4532 0151 1283 0366 |
| 📅 **Data de Validade** | MM/AA ou MM/AAAA          | 12/25               |
| 🔐 **CVV**              | 3-4 dígitos de segurança  | 123                 |
| 👤 **Nome Titular**     | Opcional                  | JOÃO DA SILVA       |
| 📄 **CPF**              | Opcional                  | 123.456.789-10      |

**Alerta só aparece quando:** Cartão + Validade + CVV são detectados

---

## 🛠️ Como Usar

### Iniciar o Programa

1. Execute `CardSecurityMonitor.exe`
2. Clique em **"▶ Iniciar Monitor"**
3. Abra um navegador e acesse um site com formulário de pagamento

### Indicadores Visuais

```
⬜ Campo não detectado
✅ Campo detectado
[████░░░░░░░░░░░░░░] 60% - Progresso
```

### Quando Alerta Aparece

Uma janela de alerta mostra:

- 💳 Cartão (último 4 dígitos visíveis)
- 📅 Data de validade
- 🔐 CVV (mascarado como \*\*\*)
- 👤 Nome do titular (se detectado)
- 📄 CPF (mascarado)
- 📸 Screenshot da tela

**Você deve verificar:**

- ✓ O site tem HTTPS? (cadeado verde)
- ✓ É o site oficial?
- ✓ Você confia neste site?

---

## ⚙️ Instalação com Auto-Inicialização

### Windows

1. **Build** o executável:

   ```powershell
   .\build.bat
   ```

2. **Instalar** na pasta de aplicativos:

   ```powershell
   cd dist
   .\CardSecurityMonitor.exe
   ```

   Ou marque a opção **"🚀 Iniciar automaticamente com o Windows"**

3. **Executar** na bandeja (System Tray):
   - O programa inicia minimizado
   - Clique no ícone 🔒 para abrir
   - Minimize novamente para continuar em segundo plano

---

## 🖥️ Estrutura do Projeto

```
card-security-monitor/
├── main.py                      # Interface principal
├── keyboard_monitor.py          # Monitor de teclado
├── pattern_detector.py          # Detector de padrões
├── alert_window.py              # Janela de alerta
├── screenshot_capture.py        # Captura de tela
├── autostart.py                 # Auto-inicialização
├── system_tray.py               # Ícone na bandeja
├── requirements.txt             # Dependências
├── build.bat                    # Build script
├── install.bat                  # Instalador
├── uninstall.bat                # Desinstalador
├── README.md                    # Este arquivo
└── GUIA_COMPLETO.md             # Guia completo em PT-BR
```

---

## 📦 Dependências

```
pynput                 # Monitor de teclado
pywin32                # APIs do Windows
psutil                 # Info do sistema
Pillow                 # Manipulação de imagens
pystray                # Ícone na bandeja
PyInstaller            # Gerador de .exe
```

Instaladas automaticamente com:

```powershell
pip install -r requirements.txt
```

---

## 🔧 Compilar Manualmente

```powershell
# Limpar builds antigos
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul

# Compilar com PyInstaller
pyinstaller --onefile --windowed --name "CardSecurityMonitor" main.py
```

---

## 🔍 Validações Implementadas

### Cartão de Crédito

- ✅ Validação com **algoritmo de Luhn**
- ✅ Detecta bandeira (Visa, Mastercard, etc)
- ✅ 16 dígitos obrigatórios

### CPF

- ✅ Validação algoritmo brasileiro oficial
- ✅ 11 dígitos obrigatórios
- ✅ Rejeita CPFs com dígitos repetidos

### Data de Validade

- ✅ Formato MM/AA ou MM/AAAA
- ✅ Mês: 01-12
- ✅ Ano: 24+

### CVV

- ✅ 3-4 dígitos isolados
- ✅ Removidos números de cartão e datas para evitar falsos positivos

---

## ❓ Perguntas Frequentes

**P: Meus dados são enviados para alguém?**  
R: NÃO! Tudo é processado localmente no seu computador.

**P: O programa pode ver minha senha?**  
R: NÃO! Monitora apenas padrões de números de cartão.

**P: Funciona em Mac/Linux?**  
R: Atualmente apenas Windows. Mac/Linux necessitam adaptações.

**P: Quanto de memória consome?**  
R: Menos de 50MB de RAM.

**P: Como desinstalar?**  
R: Execute `uninstall.bat` ou remova da inicialização do Windows manualmente.

---

## 🐛 Solução de Problemas

### "Python não encontrado"

- Instale Python 3.8+ de https://python.org
- Marque "Add Python to PATH" durante instalação

### "Módulo não encontrado"

```powershell
pip install -r requirements.txt --force-reinstall
```

### "Permissão negada"

- Execute PowerShell como **Administrador**

### Antivírus bloqueia o .exe

- Adicione exceção no seu antivírus
- É normal em programas compilados com PyInstaller

### Monitor não detecta nada

1. ✓ Monitor está iniciado? (Status: ✅ Monitorando)
2. ✓ Você está em um navegador ativo?
3. ✓ Os dados são válidos? (cartão passa Luhn, CPF válido)
4. ✓ Aguarde 60 segundos do último alerta (cooldown)

---

## 🔒 Segurança e Privacidade

✅ **Análise Local** - Tudo processado no seu computador  
✅ **Sem Registro** - Dados não são salvos em disco  
✅ **Sem Transmissão** - Nenhuma conexão com internet necessária  
✅ **Código Aberto** - Você pode revisar o código-fonte  
✅ **Mascaramento** - Alerta mostra apenas últimos 4 dígitos

---

## 📊 Como Funciona Internamente

### 1. **Monitor de Teclado**

- Captura teclas digitadas APENAS em navegadores
- Detecta qual aplicativo está em foco
- Ignora digitação em outros programas

### 2. **Detector de Padrões**

- Procura por padrões de cartão em tempo real
- Valida com algoritmo de Luhn
- Acumula dados em um buffer

### 3. **Validações**

- Cartão: 16 dígitos + Luhn
- CPF: 11 dígitos + algoritmo brasileiro
- Validade: MM/AA ou MM/AAAA

### 4. **Alerta**

- Quando Cartão + Validade + CVV estão completos
- Captura screenshot automático
- Mostra janela na frente de tudo
- Toca som de alerta

### 5. **Mascaramento**

- Cartão: 4532 •••• •••• 8901
- CPF: •••.456.•••-••
- CVV: •••

---

## 🎓 Uso Educacional

Este projeto demonstra técnicas de:

- Monitoramento de entrada do usuário
- Padrão matching com regex
- Validação de dados financeiros
- Interfaces gráficas em Python
- Empacotamento de aplicações

Use para **aprender e se proteger**!

---

## 📄 Licença

Código fornecido como está para fins de proteção contra fraude.

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

1. Verifique a console (mensagens de erro)
2. Leia o GUIA_COMPLETO.md
3. Reinstale dependências: `pip install -r requirements.txt --force-reinstall`
4. Recrie o .exe: `.\build.bat`

---

## 📈 Versão

**v2.1** - Versão Final Completa

- ✅ Auto-inicialização com Windows
- ✅ Ícone na bandeja do sistema
- ✅ Instalador automático
- ✅ Desinstalador automático
- ✅ Interface visual completa
- ✅ 5 campos de detecção
- ✅ Screenshot automático
- ✅ Validações rigorosas

---

## 🎯 Próximas Melhorias Possíveis

- [ ] Suporte a Mac/Linux
- [ ] Múltiplas línguas
- [ ] Histórico de alertas
- [ ] Integração com antivírus
- [ ] Extensão de navegador
- [ ] Dashboard web
- [ ] API REST

---

**Criado com ❤️ para sua segurança**

🔒 Proteja seus dados. Use com segurança.
