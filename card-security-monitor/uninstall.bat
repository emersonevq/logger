@echo off
chcp 65001 > nul
title Desinstalador - Card Security Monitor
color 0C

echo.
echo  ╔═══════════════════════════════════════════════════════════╗
echo  ║                                                           ║
echo  ║   🔒 CARD SECURITY MONITOR - DESINSTALADOR               ║
echo  ║                                                           ║
echo  ╚═══════════════════════════════════════════════════════════╝
echo.
echo  Este desinstalador irá:
echo.
echo    ✗ Remover o programa da inicialização automática
echo    ✗ Excluir arquivos do programa
echo    ✗ Remover atalho do Menu Iniciar
echo.
echo  ─────────────────────────────────────────────────────────────
echo.

set /p confirm="  Tem certeza que deseja desinstalar? (S/N): "
if /i not "%confirm%"=="S" exit /b 0

echo.
echo  [1/4] Fechando o programa...

taskkill /f /im CardSecurityMonitor.exe > nul 2>&1
timeout /t 2 > nul

echo  ✅ Programa fechado

echo.
echo  [2/4] Removendo da inicialização automática...

reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "CardSecurityMonitor" /f > nul 2>&1
echo  ✅ Removido da inicialização

echo.
echo  [3/4] Excluindo arquivos...

set INSTALL_DIR=%LOCALAPPDATA%\CardSecurityMonitor
rmdir /s /q "%INSTALL_DIR%" 2>nul
echo  ✅ Arquivos excluídos

echo.
echo  [4/4] Removendo atalho...

del /q "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Card Security Monitor.lnk" 2>nul
echo  ✅ Atalho removido

echo.
echo  ─────────────────────────────────────────────────────────────
echo.
echo  ╔═══════════════════════════════════════════════════════════╗
echo  ║                                                           ║
echo  ║   ✅ DESINSTALAÇÃO CONCLUÍDA!                            ║
echo  ║                                                           ║
echo  ║   O Card Security Monitor foi removido do sistema.       ║
echo  ║                                                           ║
echo  ╚═══════════════════════════════════════════════════════════╝
echo.
pause
