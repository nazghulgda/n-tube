#!/usr/bin/env bash
# adds app to the menu, --uninstall removes it
set -e
cd "$(dirname "$0")"

BIN="$HOME/.local/bin/n-tube"
ICON="$HOME/.local/share/icons/hicolor/256x256/apps/n-tube.png"
DESKTOP="$HOME/.local/share/applications/n-tube.desktop"

if [ "$1" = "--uninstall" ]; then
    rm -f "$BIN" "$ICON" "$DESKTOP"
    # yt-dlp updates downloaded by the app
    rm -rf "$HOME/.local/share/n-tube"
    echo "Removed."
    exit 0
fi

if [ ! -f n-tube ] || [ ! -f n-tube.png ]; then
    echo "ERROR: n-tube and n-tube.png not found. Run ./build_lin.sh first."
    exit 1
fi

# old name of the app
rm -f "$HOME/.local/bin/yt-downloader" \
    "$HOME/.local/share/icons/hicolor/256x256/apps/yt-downloader.png" \
    "$HOME/.local/share/applications/yt-downloader.desktop"

mkdir -p "$(dirname "$BIN")" "$(dirname "$ICON")" "$(dirname "$DESKTOP")"
install -m 755 n-tube "$BIN"
install -m 644 n-tube.png "$ICON"

cat > "$DESKTOP" <<EOF
[Desktop Entry]
Type=Application
Name=n-tube - video downloader
Comment=Download videos from YouTube, Facebook, X and many other sites
Exec=$BIN
Icon=n-tube
Terminal=false
Categories=AudioVideo;Network;
StartupWMClass=N-tube
EOF

update-desktop-database "$(dirname "$DESKTOP")" 2>/dev/null || true
gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" 2>/dev/null || true

echo "Installed: $BIN"
