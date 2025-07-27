@echo off
python -m venv venv
call venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
start uvicorn superNova_2177:app --reload
timeout /t 2
start http://localhost:8000/web_ui/index.html
