import os
import socket
import subprocess  # nosec B404
import time

import requests  # type: ignore

# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards


# Utility to find a free TCP port
def _free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("localhost", 0))
        return s.getsockname()[1]


def _start_server(port):
    env = os.environ.copy()
    cmd = [
        "streamlit",
        "run",
        "streamlit_app.py",
        "--server.headless",
        "true",
        "--server.port",
        str(port),
    ]
    return subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env
    )  # nosec B603


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
            except Exception:  # nosec B110
                pass
            if proc.poll() is not None:
                raise RuntimeError("Streamlit failed to start")
            time.sleep(1)
        else:
            raise RuntimeError("Streamlit did not start in time")

        start = time.time()
        resp = requests.get(f"http://localhost:{port}/?healthz=1", timeout=5)
        elapsed = time.time() - start
        assert resp.status_code == 200  # nosec B101
        assert "ok" in resp.text.lower()  # nosec B101
        assert elapsed < 3  # nosec B101
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
