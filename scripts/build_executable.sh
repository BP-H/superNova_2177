#!/usr/bin/env bash
set -euo pipefail

# Build the superNova_2177 CLI into a platform specific package.
# This script relies on PyInstaller and additional packaging tools
# depending on the operating system.  The PYTHON environment variable
# can be used to explicitly specify the Python executable (defaults
# to "python3").

PYTHON="${PYTHON:-python3}"

"$PYTHON" -m pip install --upgrade pip
"$PYTHON" -m pip install --upgrade pyinstaller >/dev/null

echo "Building standalone executable with PyInstaller..."
"$PYTHON" -m PyInstaller \
  --onefile \
  --name supernova-cli \
  --hidden-import=sqlalchemy \
  --hidden-import=networkx \
  --hidden-import=numpy \
  validate_hypothesis.py

echo "Executable created in dist/"

OS_NAME=$(uname -s)
case "$OS_NAME" in
    Darwin*)
        echo "Packaging macOS .app with py2app..."
        "$PYTHON" -m pip install --upgrade py2app >/dev/null
        "$PYTHON" scripts/py2app_setup.py py2app
        ;;
    Linux*)
        echo "Packaging AppImage..."
        bash scripts/build_appimage.sh
        ;;
    MINGW*|MSYS*|CYGWIN*|Windows_NT*)
        echo "Packaging Windows installer with NSIS..."
        makensis scripts/supernova_installer.nsi
        ;;
    *)
        echo "No additional packaging steps for $OS_NAME"
        ;;
esac

