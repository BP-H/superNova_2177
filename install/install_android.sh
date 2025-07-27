#!/data/data/com.termux/files/usr/bin/bash
# Termux setup script for superNova_2177
set -e
pkg install -y python git
pip install --upgrade pip uvicorn
cd $HOME
if [ ! -d superNova_2177 ]; then
    git clone https://github.com/BP-H/superNova_2177.git
fi
cd superNova_2177
pip install -r requirements.txt
uvicorn superNova_2177:app --host 0.0.0.0 --port 8000 &
sleep 2
python - <<'PY'
import qrcode, os
url = 'http://'+os.popen('ip addr show wlan0 | grep "inet "').read().split()[1].split('/')[0]+':8000/web_ui/index.html'
print('Scan to open:', url)
qrcode.make(url).print_ascii(invert=True)
PY
