#!/usr/bin/env bash
# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
set -euo pipefail

PYTHON="${PYTHON:-python3}"
if ! command -v "$PYTHON" >/dev/null 2>&1; then
    PYTHON=python
fi

"$PYTHON" -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
FRONTEND_DIR=transcendental_resonance_frontend
if [ -d "$FRONTEND_DIR" ]; then
    pip install -r "$FRONTEND_DIR/requirements.txt"
    nicegui "$FRONTEND_DIR/src/main.py" &
fi
uvicorn superNova_2177:app --reload &
sleep 2
xdg-open http://localhost:8080 || open http://localhost:8080
