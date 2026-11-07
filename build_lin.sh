#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

if [ ! -x ".venv/bin/pyinstaller" ]; then
    echo "ERROR: PyInstaller not found. Run ./setup_lin.sh first."
    exit 1
fi

# --collect-binaries imageio_ffmpeg - ffmpeg inside the executable
.venv/bin/pyinstaller \
    --onefile \
    --windowed \
    --clean \
    --noconfirm \
    --name yt-downloader \
    --add-data "assets:assets" \
    --collect-binaries imageio_ffmpeg \
    pull-yt-video-gui.py

# no icon in linux executable, install_lin.sh adds it
cp install_lin.sh dist/
cp assets/png/n-tube-256.png dist/yt-downloader.png

echo
echo "Done: dist/yt-downloader"
echo "Run dist/install_lin.sh to add app to the menu."
