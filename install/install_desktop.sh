#!/usr/bin/env bash
set -euo pipefail

PYTHON="${PYTHON:-python3}"
if ! command -v "$PYTHON" >/dev/null 2>&1; then
    PYTHON=python
fi

"$PYTHON" -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
uvicorn superNova_2177:app --reload &
sleep 2
xdg-open http://localhost:8080 || open http://localhost:8080
