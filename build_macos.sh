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

# no --onefile, it's deprecated for .app on macOS
.venv/bin/pyinstaller \
    --windowed \
    --clean \
    --noconfirm \
    --name yt-downloader \
    --icon build/n-tube.icns \
    --add-data "assets:assets" \
    --collect-binaries imageio_ffmpeg \
    pull-yt-video-gui.py

# ditto keeps symlinks and permissions in .app
ditto -c -k --keepParent dist/yt-downloader.app dist/yt-downloader-macos.zip

echo
echo "Done: dist/yt-downloader.app (zipped: dist/yt-downloader-macos.zip)"
