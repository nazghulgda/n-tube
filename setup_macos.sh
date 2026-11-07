#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

if ! command -v python3 >/dev/null; then
    echo "ERROR: Python 3 not found. Install it from https://www.python.org/downloads/macos/"
    exit 1
fi

# python.org Python has tkinter, Homebrew one needs python-tk
if ! python3 -c "import tkinter" 2>/dev/null; then
    if command -v brew >/dev/null; then
        echo "Installing tkinter for Homebrew Python..."
        PY_VER=$(python3 -c 'import sys; print(f"{sys.version_info[0]}.{sys.version_info[1]}")')
        brew install "python-tk@$PY_VER"
    else
        echo "ERROR: tkinter is missing. Install Python from https://www.python.org/downloads/macos/"
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
echo "Setup finished. Run ./build_macos.sh to build the app."
