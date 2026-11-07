#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

# venv and tkinter are separate packages on most distros
if ! python3 -c "import venv, ensurepip, tkinter" 2>/dev/null; then
    echo "Installing system packages (python3-venv, python3-tk)..."
    if command -v apt-get >/dev/null; then
        sudo apt-get update
        sudo apt-get install -y python3-venv python3-pip python3-tk
    elif command -v dnf >/dev/null; then
        sudo dnf install -y python3-pip python3-tkinter
    elif command -v pacman >/dev/null; then
        sudo pacman -S --needed --noconfirm python-pip tk
    elif command -v zypper >/dev/null; then
        sudo zypper install -y python3-pip python3-tk
    else
        echo "ERROR: Unknown package manager. Install Python 3 with venv and tkinter manually."
        exit 1
    fi
fi

if [ ! -x ".venv/bin/python" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

echo "Installing dependencies..."
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -U -r requirements.txt pyinstaller

echo
echo "Setup finished. Run ./build_lin.sh to build the app."
