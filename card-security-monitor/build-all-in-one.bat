@echo off
chcp 65001 > nul
title Credit Card Security Monitor - All-in-One Build
color 0A

echo.
echo  ╔═══════════════════════════════════════════════════════════╗
echo  ║                                                           ║
echo  ║   🔒 CREDIT CARD SECURITY MONITOR                        ║
echo  ║      All-in-One EXE Builder (Backend + Monitor + Browser)║
echo  ║      v3.0                                                 ║
echo  ║                                                           ║
echo  ╚═══════════════════════════════════════════════════════════╝
echo.
echo  NOTA: Este processo vai compilar TUDO em um único .exe
echo  Inclui: Backend Express + Monitor + Navegador
echo.

echo  [1/7] Verificando dependências...
python --version > nul 2>&1
if errorlevel 1 (
    color 0C
    echo  ❌ ERRO: Python não encontrado!
    pause
    exit /b 1
)
python --version
node --version 2>nul || (
    color 0C
    echo  ❌ ERRO: Node.js não encontrado!
    echo  Instale em: https://nodejs.org
    pause
    exit /b 1
)
node --version
echo.

echo  [2/7] Instalando/Atualizando dependências Python...
pip install -r requirements.txt -q --disable-pip-version-check
if errorlevel 1 (
    color 0C
    echo  ❌ ERRO ao instalar dependências Python!
    pause
    exit /b 1
)
echo  ✅ Dependências Python OK
echo.

echo  [3/7] Compilando projeto Node/Express (Frontend + Backend)...
cd ..
call npm run build
if errorlevel 1 (
    color 0C
    echo  ❌ ERRO ao compilar projeto Node!
    pause
    exit /b 1
)
echo  ✅ Projeto Node compilado
cd card-security-monitor
echo.

echo  [4/7] Limpando builds anteriores...
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
del /q *.spec 2>nul
echo  ✅ Limpo
echo.

echo  [5/7] Instalando PyInstaller (se necessário)...
pip install pyinstaller -q --disable-pip-version-check
echo  ✅ PyInstaller pronto
echo.

echo  [6/7] Compilando executável all-in-one...
echo     (Isto pode levar 3-5 minutos)
echo.

REM Criar executável do launcher
pyinstaller --onefile ^
    --windowed ^
    --name "CardSecurityMonitor" ^
    --add-data "main.py;." ^
    --add-data "keyboard_monitor.py;." ^
    --add-data "pattern_detector.py;." ^
    --add-data "alert_window.py;." ^
    --add-data "screenshot_capture.py;." ^
    --add-data "autostart.py;." ^
    --add-data "system_tray.py;." ^
    --add-data "websocket.py;." ^
    --add-data "../dist/server;../dist/server" ^
    --add-data "../dist/spa;../dist/spa" ^
    --hidden-import=pynput.keyboard._win32 ^
    --hidden-import=pynput.mouse._win32 ^
    --hidden-import=PIL._tkinter_finder ^
    --hidden-import=win32gui ^
    --hidden-import=win32process ^
    --hidden-import=psutil ^
    --hidden-import=pystray ^
    --hidden-import=websockets ^
    --uac-admin ^
    launcher.py

if errorlevel 1 (
    color 0C
    echo.
    echo  ❌ ERRO na compilação!
    pause
    exit /b 1
)
echo  ✅ Executável compilado
echo.

echo  [7/7] Finalizando...
rmdir /s /q build 2>nul
del /q *.spec 2>nul
echo  ✅ Construção finalizada
echo.

echo.
echo  ╔═══════════════════════════════════════════════════════════╗
echo  ║                                                           ║
echo  ║   ✅ BUILD CONCLUÍDO COM SUCESSO!                        ║
echo  ║                                                           ║
echo  ║   📦 Executável: dist\CardSecurityMonitor.exe             ║
echo  ║                                                           ║
echo  ║   ⚡ O que ele faz:                                      ║
echo  ║   1. Inicia o Backend Express (porta 8080)               ║
echo  ║   2. Inicia o Monitor de Cartão                          ║
echo  ║   3. Abre navegador automaticamente                      ║
echo  ║   4. Tudo em um único executável!                        ║
echo  ║                                                           ║
echo  ║   🚀 Para usar:                                          ║
echo  ║   Clique 2x em: dist\CardSecurityMonitor.exe             ║
echo  ║                                                           ║
echo  ║   ⚠️  IMPORTANTE:                                         ║
echo  ║   • Execute como Administrador (direitos elevados)       ║
echo  ║   • Pode demorar 10-15s na primeira inicialização        ║
echo  ║   • Verifique firewall/antivírus                         ║
echo  ║                                                           ║
echo  ╚═══════════════════════════════════════════════════════════╝
echo.

set /p open="  Deseja abrir a pasta dist? (S/N): "
if /i "%open%"=="S" explorer dist

echo.
echo  💡 Dicas:
echo  • Se não abrir o navegador, acesse: http://localhost:8080/payment-test
echo  • Console mostrará os logs de tudo que está acontecendo
echo  • Pressione Ctrl+C no console para encerrar tudo
echo.

pause
