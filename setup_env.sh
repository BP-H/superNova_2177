#!/usr/bin/env bash
set -euo pipefail

ENV_DIR="venv"

# Create virtual environment if missing
if [ ! -d "$ENV_DIR" ]; then
    if command -v python3 >/dev/null 2>&1; then
        python3 -m venv "$ENV_DIR"
    else
        python -m venv "$ENV_DIR"
    fi
fi

# Activate the virtual environment
if [[ "${OSTYPE:-}" == msys* || "${OSTYPE:-}" == cygwin* || "${OSTYPE:-}" == win32* ]]; then
    source "$ENV_DIR/Scripts/activate"
else
    source "$ENV_DIR/bin/activate"
fi

# Upgrade pip and install dependencies
pip install --upgrade pip
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi
pip install .

# Copy example environment file if needed
if [ -f ".env.example" ] && [ ! -f ".env" ]; then
    cp .env.example .env
fi

# Final message
if [[ "${OSTYPE:-}" == msys* || "${OSTYPE:-}" == cygwin* || "${OSTYPE:-}" == win32* ]]; then
    echo "Setup complete. Activate with venv\\Scripts\\activate"
else
    echo "Setup complete. Activate with 'source venv/bin/activate'"
fi
