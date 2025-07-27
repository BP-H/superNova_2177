$ErrorActionPreference = 'Stop'

# Build a standalone executable using PyInstaller
pip install pyinstaller

# Package the CLI entry point validate_hypothesis.py
pyinstaller --onefile validate_hypothesis.py --name supernova-cli

Write-Host "Executable created in dist/ directory"
