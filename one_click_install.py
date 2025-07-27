"""One-click installer for superNova_2177."""
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

PYTHON_VERSION = (3, 12)


def ensure_python() -> str:
    """Ensure Python 3.12 is available. Download installer if missing."""
    if sys.version_info >= PYTHON_VERSION:
        return sys.executable

    if shutil.which("python3.12"):
        return "python3.12"

    system = platform.system()
    tmp_dir = Path(tempfile.mkdtemp())
    if system == "Windows":
        url = "https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe"
        installer = tmp_dir / "python-3.12.exe"
    elif system == "Darwin":
        url = "https://www.python.org/ftp/python/3.12.0/python-3.12.0-macos11.pkg"
        installer = tmp_dir / "python-3.12.pkg"
    else:
        url = "https://www.python.org/ftp/python/3.12.0/Python-3.12.0.tgz"
        installer = tmp_dir / "Python-3.12.tgz"

    print(f"Downloading Python 3.12 from {url} ...")
    try:
        urllib.request.urlretrieve(url, installer)
        print(f"Installer downloaded to {installer}")
    except Exception as exc:
        print(f"Failed to download Python: {exc}")
        return sys.executable

    if system == "Linux":
        print("Please install Python 3.12 manually from the downloaded archive.")
    else:
        subprocess.run([str(installer)], check=False)
    return shutil.which("python3.12") or sys.executable


def main() -> None:
    python_bin = ensure_python()
    os.environ.setdefault("PYTHON_BIN", python_bin)

    system = platform.system()
    build_script = Path("scripts/build_executable.sh").resolve()

    if system == "Windows":
        subprocess.check_call(["bash", str(build_script)])
    elif system == "Darwin":
        subprocess.check_call(["bash", str(build_script)])
    else:
        subprocess.check_call(["bash", str(build_script)])


if __name__ == "__main__":
    main()
