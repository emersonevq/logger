@echo off
chcp 65001 > nul
color 0A

echo.
echo ========================================
echo FIX AUTOSTART - Remover duplicatas
echo ========================================
echo.

echo [1] Removendo entradas duplicadas do registro...

REM Remove possíveis entradas duplicadas
reg delete "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run" /v "WindowsSecurity" /f 2>nul
reg delete "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run" /v "CardSecurityMonitor" /f 2>nul
reg delete "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run" /v "Security" /f 2>nul
reg delete "HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Run" /v "WindowsSecurity" /f 2>nul

echo ✅ Limpeza completa!
echo.

echo [2] Status atual:
reg query "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run" /v "WindowsSecurity" 2>nul
if errorlevel 1 (
    echo ✅ Nenhuma entrada de autostart ativa
) else (
    echo ⚠️ Entrada ainda existe
)

echo.
echo ========================================
echo FEITO!
echo ========================================
echo.
pause
