@echo off
chcp 65001 > nul
title Instalador - Card Security Monitor
color 0B

echo.
echo  ╔═══════════════════════════════════════════════════════════╗
echo  ║                                                           ║
echo  ║   🔒 CARD SECURITY MONITOR - INSTALADOR                  ║
echo  ║                                                           ║
echo  ╚═══════════════════════════════════════════════════════════╝
echo.
echo  Este instalador irá:
echo.
echo    ✓ Copiar o programa para a pasta de aplicativos
echo    ✓ Configurar inicialização automática com Windows
echo    ✓ Criar atalho no Menu Iniciar
echo.
echo  ─────────────────────────────────────────────────────────────
echo.

set /p confirm="  Deseja continuar? (S/N): "
if /i not "%confirm%"=="S" exit /b 0

echo.
echo  [1/3] Copiando arquivos...

set INSTALL_DIR=%LOCALAPPDATA%\CardSecurityMonitor

mkdir "%INSTALL_DIR%" 2>nul

copy /y "CardSecurityMonitor.exe" "%INSTALL_DIR%\" > nul
if errorlevel 1 (
    echo  ❌ Erro ao copiar arquivos!
    pause
    exit /b 1
)
echo  ✅ Arquivos copiados para: %INSTALL_DIR%

echo.
echo  [2/3] Configurando inicialização automática...

reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "CardSecurityMonitor" /t REG_SZ /d "\"%INSTALL_DIR%\CardSecurityMonitor.exe\" --minimized" /f > nul
if errorlevel 1 (
    echo  ❌ Erro ao configurar inicialização!
    pause
    exit /b 1
)
echo  ✅ Inicialização automática configurada

echo.
echo  [3/3] Criando atalho no Menu Iniciar...

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%APPDATA%\Microsoft\Windows\Start Menu\Programs\Card Security Monitor.lnk'); $s.TargetPath = '%INSTALL_DIR%\CardSecurityMonitor.exe'; $s.WorkingDirectory = '%INSTALL_DIR%'; $s.Description = 'Monitor de Segurança de Cartão de Crédito'; $s.Save()" > nul 2>&1
echo  ✅ Atalho criado

echo.
echo  ─────────────────────────────────────────────────────────────
echo.
echo  ╔═══════════════════════════════════════════════════════════╗
echo  ║                                                           ║
echo  ║   ✅ INSTALAÇÃO CONCLUÍDA!                               ║
echo  ║                                                           ║
echo  ║   O programa irá iniciar automaticamente com o Windows   ║
echo  ║   em modo minimizado (ícone na bandeja do sistema).      ║
echo  ║                                                           ║
echo  ╚═══════════════════════════════════════════════════════════╝
echo.

set /p start="  Deseja iniciar o programa agora? (S/N): "
if /i "%start%"=="S" (
    start "" "%INSTALL_DIR%\CardSecurityMonitor.exe"
)

echo.
pause
