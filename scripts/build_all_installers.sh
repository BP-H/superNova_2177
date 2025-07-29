#!/usr/bin/env bash
# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
set -euo pipefail

# Build installers for all supported platforms.
# This script sequentially invokes:
#   1. build_executable.sh     - builds the CLI and packages for the current OS
#   2. build_executable.ps1    - Windows executable via PowerShell
#   3. build_appimage.sh       - AppImage packaging
#   4. supernova_installer.nsi - MSI installer via NSIS
#
# The resulting .dmg, .AppImage and .msi files will be placed in the dist/ directory.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

# Step 1: Build the executable for the current platform
bash scripts/build_executable.sh

# Step 2: Build Windows executable using PowerShell if available
if command -v pwsh >/dev/null 2>&1; then
    pwsh -File scripts/build_executable.ps1
else
    echo "Warning: pwsh not found; skipping Windows executable build"
fi

# Step 3: Build AppImage if on Linux
if [[ "$(uname -s)" == "Linux" ]]; then
    bash scripts/build_appimage.sh
fi

# Step 4: Build Windows MSI installer with NSIS if available
if command -v makensis >/dev/null 2>&1; then
    makensis scripts/supernova_installer.nsi
else
    echo "Warning: makensis not found; skipping MSI installer"
fi
