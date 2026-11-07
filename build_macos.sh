#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

if [ ! -x ".venv/bin/pyinstaller" ]; then
    echo "ERROR: PyInstaller not found. Run ./setup_macos.sh first."
    exit 1
fi

# .icns from png files
ICONSET=build/n-tube.iconset
rm -rf "$ICONSET"
mkdir -p "$ICONSET"
for size in 16 32 128 256; do
    cp "assets/png/n-tube-$size.png" "$ICONSET/icon_${size}x${size}.png"
    cp "assets/png/n-tube-$((size * 2)).png" "$ICONSET/icon_${size}x${size}@2x.png"
done
cp assets/png/n-tube-512.png "$ICONSET/icon_512x512.png"
iconutil -c icns "$ICONSET" -o build/n-tube.icns

# newest yt-dlp inside the app
.venv/bin/python -m pip install -U yt-dlp

# only icons used by n-tube-gui.py (set_icon)
ICONS=()
for size in 16 32 48 64 128 256; do
    ICONS+=(--add-data "assets/png/n-tube-$size.png:assets/png")
done

# no --onefile, it's deprecated for .app on macOS
.venv/bin/pyinstaller \
    --windowed \
    --clean \
    --noconfirm \
    --name n-tube \
    --icon build/n-tube.icns \
    "${ICONS[@]}" \
    --collect-binaries imageio_ffmpeg \
    n-tube-gui.py

# ditto keeps symlinks and permissions in .app
ditto -c -k --keepParent dist/n-tube.app dist/n-tube-macos.zip

echo
echo "Done: dist/n-tube.app (zipped: dist/n-tube-macos.zip)"
