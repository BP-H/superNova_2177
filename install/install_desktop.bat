# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
@echo off
python -m venv venv
call venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
set FRONTEND_DIR=transcendental_resonance_frontend
if exist %FRONTEND_DIR% (
    pip install -r %FRONTEND_DIR%\requirements.txt
    start nicegui %FRONTEND_DIR%\src\main.py
)
start uvicorn superNova_2177:app --reload
timeout /t 2
start http://localhost:8080
