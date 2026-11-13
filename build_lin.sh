#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

# python -m PyInstaller instead of .venv/bin/pyinstaller - the script has the venv
# path hardcoded in its shebang and breaks when the folder is moved/renamed
if ! .venv/bin/python -m PyInstaller --version >/dev/null 2>&1; then
    echo "ERROR: PyInstaller not found. Run ./setup_lin.sh first."
    exit 1
fi

# newest yt-dlp (and solver scripts matching it) inside the app
.venv/bin/python -m pip install -U yt-dlp yt-dlp-ejs

# only icons used by n-tube-gui.py (set_icon)
ICONS=()
for size in 16 32 48 64 128 256; do
    ICONS+=(--add-data "assets/png/n-tube-$size.png:assets/png")
done

# --collect-binaries imageio_ffmpeg - ffmpeg inside the executable
.venv/bin/python -m PyInstaller \
    --onefile \
    --windowed \
    --clean \
    --noconfirm \
    --name n-tube \
    "${ICONS[@]}" \
    --collect-binaries imageio_ffmpeg \
    n-tube-gui.py

# no icon in linux executable, install_lin.sh adds it
cp install_lin.sh dist/
cp assets/png/n-tube-256.png dist/n-tube.png

echo
echo "Done: dist/n-tube"
echo "Run dist/install_lin.sh to add app to the menu."
