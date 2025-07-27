#!/usr/bin/env bash
set -euo pipefail

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate the virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install the package
pip install .

# Install additional dependencies
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi

# Copy example environment file if needed
if [ -f ".env.example" ] && [ ! -f ".env" ]; then
    cp .env.example .env
fi

echo "Installation complete. Activate the environment with 'source venv/bin/activate'"
