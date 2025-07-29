import os
import socket
import subprocess
import time

import requests


def _free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("localhost", 0))
        return s.getsockname()[1]


def _start_server(port):
    cmd = [
        "streamlit",
        "run",
        "ui.py",
        "--server.headless",
        "true",
        "--server.port",
        str(port),
    ]
    env = os.environ.copy()
    return subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env
    )


def test_ui_healthz_query():
    port = _free_port()
    proc = _start_server(port)
    try:
        for _ in range(30):
            try:
                resp = requests.get(f"http://localhost:{port}/?healthz=1", timeout=1)
                if resp.status_code == 200:
                    break
            except Exception:
                pass
            if proc.poll() is not None:
                raise RuntimeError("Streamlit failed to start")
            time.sleep(1)
        else:
            raise RuntimeError("Streamlit did not start in time")

        resp = requests.get(f"http://localhost:{port}/?healthz=1", timeout=5)
        assert resp.status_code == 200
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
