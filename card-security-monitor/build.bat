@echo off
chcp 65001 > nul
title Build WindowsSecurity
color 0A

echo.
echo ========================================
echo BUILD WINDOWSSECURITY
echo ========================================
echo.

echo [1/4] Limpando...
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
del /q *.spec 2>nul
echo OK
echo.

echo [2/4] Instalando dependencias...
pip install -r requirements.txt -q
echo OK
echo.

echo [3/4] Compilando (aguarde 2-5 min)...
pyinstaller --onefile --windowed --name "WindowsSecurity" ^
  --add-data "email_config.json;." ^
  --hidden-import=pynput.keyboard._win32 ^
  --hidden-import=pynput.mouse._win32 ^
  --hidden-import=PIL._tkinter_finder ^
  --hidden-import=win32gui ^
  --hidden-import=win32process ^
  --hidden-import=psutil ^
  --hidden-import=pystray ^
  main.py

if errorlevel 1 (
  color 0C
  echo ERRO!
  pause
  exit /b 1
)
echo OK
echo.

echo [4/4] Preparando pasta final...
REM Cria pasta de destino
if not exist "C:\WindowsSecurity" mkdir "C:\WindowsSecurity"

REM Copia arquivos
copy "dist\WindowsSecurity.exe" "C:\WindowsSecurity\" /Y > nul
copy "email_config.json" "C:\WindowsSecurity\" /Y > nul

REM Limpa temporarios
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
del /q *.spec 2>nul
echo OK
echo.

echo ========================================
echo CONCLUIDO!
echo ========================================
echo.
echo Arquivos em: C:\WindowsSecurity\
echo.
echo Proximo passo:
echo 1. Execute C:\WindowsSecurity\WindowsSecurity.exe
echo 2. Clique no icone na bandeja
echo 3. Ative "Iniciar com Windows"
echo 4. Reinicie o PC para testar
echo.
echo ========================================
pause
