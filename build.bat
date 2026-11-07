@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\pyinstaller.exe" (
    echo ERROR: PyInstaller not found. Run setup.bat first.
    pause
    exit /b 1
)

rem newest yt-dlp inside the exe
".venv\Scripts\python.exe" -m pip install -U yt-dlp
if errorlevel 1 (
    echo ERROR: Updating yt-dlp failed.
    pause
    exit /b 1
)

rem --collect-binaries imageio_ffmpeg - ffmpeg inside the exe
".venv\Scripts\pyinstaller.exe" ^
    --onefile ^
    --windowed ^
    --clean ^
    --noconfirm ^
    --name n-tube ^
    --icon assets\n-tube.ico ^
    --add-data "assets\n-tube.ico;assets" ^
    --collect-binaries imageio_ffmpeg ^
    n-tube-gui.py
if errorlevel 1 (
    echo ERROR: Build failed.
    pause
    exit /b 1
)

echo.
echo Done: dist\n-tube.exe
pause
