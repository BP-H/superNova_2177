#!/usr/bin/env bash
set -euo pipefail

# Build a standalone executable using PyInstaller
# The resulting binary will be placed in the dist/ directory
# Ensure PyInstaller is installed
pip install pyinstaller

# Package the CLI entry point validate_hypothesis.py
pyinstaller --onefile validate_hypothesis.py --name supernova-cli

echo "Executable created in dist/ directory"
