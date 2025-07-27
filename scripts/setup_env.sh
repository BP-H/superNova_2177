#!/usr/bin/env bash
set -euo pipefail

# Create virtual environment if missing
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate the virtual environment
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Copy example environment if .env doesn't exist
if [ -f ".env.example" ] && [ ! -f ".env" ]; then
    cp .env.example .env
fi

echo "Environment setup complete."
