@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    py -3 -m venv .venv 2>nul || python -m venv .venv
    if errorlevel 1 (
        echo ERROR: Python not found. Install it from https://www.python.org/downloads/
        pause
        exit /b 1
    )
)

echo Installing dependencies...
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -U -r requirements.txt pyinstaller
if errorlevel 1 (
    echo ERROR: Installing dependencies failed.
    pause
    exit /b 1
)

echo.
echo Setup finished. Run build.bat to build the exe.
pause
