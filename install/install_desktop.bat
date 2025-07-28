@echo off
python -m venv venv
call venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
set FRONTEND_DIR=transcendental_resonance_frontend
if not exist %FRONTEND_DIR% if exist web_ui (
    echo Warning: 'web_ui' has been renamed to 'transcendental_resonance_frontend'
    set FRONTEND_DIR=web_ui
)
if exist %FRONTEND_DIR% (
    pip install -r %FRONTEND_DIR%\requirements.txt
    start nicegui %FRONTEND_DIR%\src\main.py
)
start uvicorn superNova_2177:app --reload
timeout /t 2
start http://localhost:8080
