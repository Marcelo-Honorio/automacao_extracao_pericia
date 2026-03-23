@echo off
cd /d %~dp0

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

pyinstaller ^
  --clean ^
  --onedir ^
  --noconsole ^
  --name ExtratorFichaGrafica ^
  --add-data "laudo\templates\*.xlsx;laudo\templates" ^
  --add-data "laudo\templates\*.docx;laudo\templates" ^
  --add-data "indices\dados\bcb\*.csv;indices\dados\bcb" ^
  app.py

pause