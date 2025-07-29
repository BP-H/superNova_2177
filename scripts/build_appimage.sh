#!/usr/bin/env bash
# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
set -euo pipefail

APP=supernova-cli
APPDIR=AppDir

rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/bin"

cp "dist/$APP" "$APPDIR/usr/bin/"

cat > "$APPDIR/AppRun" <<'EOR'
#!/bin/sh
DIR="$(dirname "$0")"
exec "$DIR/usr/bin/supernova-cli" "$@"
EOR
chmod +x "$APPDIR/AppRun"

appimagetool "$APPDIR" "dist/${APP}.AppImage"

echo "AppImage created at dist/${APP}.AppImage"
