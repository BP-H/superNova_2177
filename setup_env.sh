#!/usr/bin/env bash
set -euo pipefail

ENV_DIR="venv"

# Determine Python interpreter
if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
else
    echo "Python not found. Please install Python 3.12 or newer." >&2
    exit 1
fi

# Ensure Python version is >= 3.12
if ! "$PYTHON_CMD" -c 'import sys; exit(0 if sys.version_info >= (3,12) else 1)'; then
    echo "Python 3.12 or higher is required. Current version: $($PYTHON_CMD --version 2>&1)" >&2
    exit 1
fi

# Create virtual environment if missing
if [ ! -d "$ENV_DIR" ]; then
    "$PYTHON_CMD" -m venv "$ENV_DIR"
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
