@echo off
rem Inicia a Loja Didatica 2 (Windows). Usa o "py" launcher ou o python do PATH.
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 loja_didatica_2_v2.py %*
  goto :fim
)
where python >nul 2>nul
if %errorlevel%==0 (
  python loja_didatica_2_v2.py %*
  goto :fim
)
echo Python 3 nao encontrado. Instale em https://www.python.org/downloads/
echo (marque "Add python.exe to PATH" no instalador) e rode este arquivo de novo.
pause
:fim
