@echo off
setlocal

cd /d "%~dp0"

echo ======================================
echo Limpando build anterior...
echo ======================================

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo ======================================
echo Gerando executavel...
echo ======================================

pyinstaller AutoPericia.spec

echo.
echo ======================================
echo Build concluido!
echo ======================================
echo Executavel em:
echo dist\AutoPericia\AutoPericia.exe

pause