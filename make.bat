@echo off
setlocal
py -3 -m venv .venv || exit /b 1
call .venv\Scripts\python.exe -m pip install ".[build]" || exit /b 1
call .venv\Scripts\python.exe -m PyInstaller --clean --noconfirm build.spec || exit /b 1
echo Executable: dist\OpenFrontAutoPlacer.exe
