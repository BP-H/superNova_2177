#!/usr/bin/env bash
set -euo pipefail

# Build a standalone executable using PyInstaller and create a
# platform specific installer. Requires Python 3.12.

PYTHON_BIN=${PYTHON_BIN:-python3}
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    echo "Python interpreter '$PYTHON_BIN' not found."
    exit 1
fi

# Ensure PyInstaller and platform helpers are installed
"$PYTHON_BIN" -m pip install --upgrade pyinstaller >/dev/null

# Build the CLI entry point with hidden imports
"$PYTHON_BIN" -m PyInstaller \
    --onefile \
    --name supernova-cli \
    --hidden-import sqlalchemy \
    --hidden-import networkx \
    --hidden-import numpy \
    validate_hypothesis.py

OS_NAME=$(uname -s)

case "$OS_NAME" in
    MINGW*|MSYS*|CYGWIN*|Windows_NT)
        if command -v makensis >/dev/null 2>&1; then
            makensis scripts/supernova.nsi
        else
            echo "NSIS not found. Skipping Windows installer creation."
        fi
        ;;
    Darwin)
        "$PYTHON_BIN" -m pip install --upgrade py2app >/dev/null || true
        if [ -f setup.py ]; then
            "$PYTHON_BIN" setup.py py2app -A
        else
            echo "setup.py not found for py2app build"
        fi
        ;;
    Linux)
        if command -v appimagetool >/dev/null 2>&1; then
            APPDIR=dist/AppDir
            mkdir -p "$APPDIR/usr/bin"
            cp dist/supernova-cli "$APPDIR/usr/bin/"
            appimagetool "$APPDIR" dist/supernova-cli.AppImage
        else
            echo "appimagetool not found. Skipping AppImage creation."
        fi
        ;;
    *)
        echo "Unknown platform $OS_NAME. Only the executable will be built."
        ;;
esac

echo "Build artifacts created in the dist/ directory"
