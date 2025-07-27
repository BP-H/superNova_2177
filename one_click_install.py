import os
import platform
import shutil
import subprocess
import sys
import tempfile
import urllib.request


def _download(url: str, dest: str) -> None:
    print(f"Downloading {url}...")
    urllib.request.urlretrieve(url, dest)


def _ensure_python312() -> str:
    """Return path to a Python 3.12 interpreter, installing if necessary."""
    if sys.version_info >= (3, 12):
        return sys.executable

    for exe in ("python3.12", "python312", "python3.12.exe", "python.exe"):
        path = shutil.which(exe)
        if path:
            try:
                out = subprocess.check_output([path, "--version"], text=True)
            except Exception:
                continue
            if out.startswith("Python 3.12"):
                return path

    system = platform.system()
    tmp = tempfile.gettempdir()
    if system == "Windows":
        installer = os.path.join(tmp, "python312.exe")
        _download(
            "https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe",
            installer,
        )
        subprocess.check_call([installer, "/quiet", "InstallAllUsers=1", "PrependPath=1"])
    elif system == "Darwin":
        pkg = os.path.join(tmp, "python312.pkg")
        _download(
            "https://www.python.org/ftp/python/3.12.0/python-3.12.0-macos11.pkg",
            pkg,
        )
        subprocess.check_call(["sudo", "installer", "-pkg", pkg, "-target", "/"])
    else:  # Linux and others
        if shutil.which("apt-get"):
            subprocess.check_call(["sudo", "apt-get", "update"])
            subprocess.check_call(["sudo", "apt-get", "install", "-y", "python3.12", "python3.12-venv"])
        else:
            tarball = os.path.join(tmp, "Python-3.12.0.tgz")
            _download(
                "https://www.python.org/ftp/python/3.12.0/Python-3.12.0.tgz",
                tarball,
            )
            build_dir = os.path.join(tmp, "python-build")
            os.makedirs(build_dir, exist_ok=True)
            subprocess.check_call(["tar", "xf", tarball, "-C", build_dir])
            src = os.path.join(build_dir, "Python-3.12.0")
            subprocess.check_call(
                ["bash", "-c", f"cd {src} && ./configure --prefix=/usr/local && make -j$(nproc) && sudo make install"]
            )

    # After installation attempt
    path = shutil.which("python3.12")
    if path:
        return path
    raise RuntimeError("Python 3.12 installation failed")


def main() -> None:
    python_path = _ensure_python312()
    env = os.environ.copy()
    env["PYTHON"] = python_path
    script = os.path.join(os.path.dirname(__file__), "scripts", "build_executable.sh")
    if platform.system() == "Windows":
        cmd = ["bash", script]
    else:
        cmd = ["bash", script]
    subprocess.check_call(cmd, env=env)


if __name__ == "__main__":
    main()
