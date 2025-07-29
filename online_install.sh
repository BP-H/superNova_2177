#!/usr/bin/env bash
# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
set -euo pipefail

ENV_DIR="venv"
PYTHON="${PYTHON:-python3}"
if ! command -v "$PYTHON" >/dev/null 2>&1; then
    PYTHON=python
fi

CREATED_ENV=0
if [[ -z "${VIRTUAL_ENV:-}" ]]; then
    if [ ! -d "$ENV_DIR" ]; then
        "$PYTHON" -m venv "$ENV_DIR"
        CREATED_ENV=1
    fi
    # shellcheck disable=SC1090
    source "$ENV_DIR/bin/activate"
fi

pip install --upgrade pip
pip install "git+https://github.com/BP-H/superNova_2177.git"
pip install -r requirements.txt

if [ -f ".env.example" ] && [ ! -f ".env" ]; then
    cp .env.example .env
fi

echo "Installation complete." 
if [[ $CREATED_ENV -eq 1 ]]; then
    echo "Activate the environment with 'source $ENV_DIR/bin/activate'"
fi
echo "Set SECRET_KEY in the environment or the .env file before running the app."
