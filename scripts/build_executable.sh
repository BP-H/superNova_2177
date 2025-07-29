#!/usr/bin/env bash
# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
set -euo pipefail

# Build the superNova_2177 CLI into a platform specific package.
# This script relies on PyInstaller and additional packaging tools
# depending on the operating system.  The PYTHON environment variable
# can be used to explicitly specify the Python executable (defaults
# to "python3").

PYTHON="${PYTHON:-python3}"

"$PYTHON" -m pip install --upgrade pip >/dev/null
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
        echo "Packaging macOS DMG with py2app..."
        "$PYTHON" -m pip install --upgrade py2app >/dev/null
        "$PYTHON" scripts/py2app_setup.py py2app
        hdiutil create dist/supernova-cli.dmg -volname "SuperNova2177" -srcfolder "dist/SuperNova 2177.app" >/dev/null
        ;;
    Linux*)
        echo "Packaging AppImage..."
        bash scripts/build_appimage.sh
        ;;
    MINGW*|MSYS*|CYGWIN*|Windows_NT*)
        echo "Packaging Windows MSI with NSIS..."
        makensis -DMSI=1 scripts/supernova_installer.nsi
        ;;
    *)
        echo "No additional packaging steps for $OS_NAME"
        ;;
esac

