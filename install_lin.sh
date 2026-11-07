#!/usr/bin/env bash
# adds app to the menu, --uninstall removes it
set -e
cd "$(dirname "$0")"

BIN="$HOME/.local/bin/yt-downloader"
ICON="$HOME/.local/share/icons/hicolor/256x256/apps/yt-downloader.png"
DESKTOP="$HOME/.local/share/applications/yt-downloader.desktop"

if [ "$1" = "--uninstall" ]; then
    rm -f "$BIN" "$ICON" "$DESKTOP"
    echo "Removed."
    exit 0
fi

if [ ! -f yt-downloader ] || [ ! -f yt-downloader.png ]; then
    echo "ERROR: yt-downloader and yt-downloader.png not found. Run ./build_lin.sh first."
    exit 1
fi

mkdir -p "$(dirname "$BIN")" "$(dirname "$ICON")" "$(dirname "$DESKTOP")"
install -m 755 yt-downloader "$BIN"
install -m 644 yt-downloader.png "$ICON"

cat > "$DESKTOP" <<EOF
[Desktop Entry]
Type=Application
Name=n-tube - video downloader
Comment=Download videos from YouTube, Facebook, X and many other sites
Exec=$BIN
Icon=yt-downloader
Terminal=false
Categories=AudioVideo;Network;
StartupWMClass=Yt-downloader
EOF

update-desktop-database "$(dirname "$DESKTOP")" 2>/dev/null || true
gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" 2>/dev/null || true

echo "Installed: $BIN"
