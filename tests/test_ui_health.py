import os
import socket
import subprocess
import sys
import time

import requests


# Utility to find a free TCP port
def _free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("localhost", 0))
        return s.getsockname()[1]


def _start_server(port):
    env = os.environ.copy()
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "ui.py",
        "--server.headless",
        "true",
        "--server.port",
        str(port),
    ]
    return subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env
    )


def test_healthz_endpoint():
    port = _free_port()
    proc = _start_server(port)
    try:
        # Wait for server to come up
        for _ in range(30):
            try:
                res = requests.get(f"http://localhost:{port}/?healthz=1", timeout=1)
                if res.status_code == 200:
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
