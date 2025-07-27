import os
import platform
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import hashlib
from tqdm import tqdm

OFFLINE_DIR = "offline_deps"
ENV_DIR = "venv"


def download(
    url: str,
    dest: str,
    expected_sha256: str | None = None,
    *,
    mirror_url: str | None = None,
    retries: int = 3,
) -> None:
    """Download a file with optional retries and mirror fallback."""

    attempt = 0
    current_url = url
    while True:
        try:
            print(f"Downloading {current_url}...")
            with urllib.request.urlopen(current_url) as resp, open(dest, "wb") as f:
                total = resp.length or int(resp.headers.get("Content-Length", 0))
                with tqdm(total=total, unit="B", unit_scale=True, desc=os.path.basename(dest)) as pbar:
                    while True:
                        chunk = resp.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
                        pbar.update(len(chunk))
            break
        except Exception as e:  # pragma: no cover - network dependent
            attempt += 1
            if attempt < retries:
                print(f"Download failed: {e}. Retrying ({attempt}/{retries})...")
                continue
            if mirror_url and current_url != mirror_url:
                print(f"Download failed: {e}. Falling back to mirror {mirror_url}...")
                current_url = mirror_url
                attempt = 0
                continue
            raise RuntimeError(f"Failed to download {current_url}: {e}") from e

    if expected_sha256:
        hasher = hashlib.sha256()
        with open(dest, "rb") as f:
            for block in iter(lambda: f.read(8192), b""):
                hasher.update(block)
        digest = hasher.hexdigest()
        if digest.lower() != expected_sha256.lower():
            raise ValueError(
                f"SHA256 mismatch for {dest}: expected {expected_sha256}, got {digest}"
            )


def ensure_python312() -> str:
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
        download("https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe", installer)
        subprocess.check_call([installer, "/quiet", "InstallAllUsers=1", "PrependPath=1"])
        os.remove(installer)
    elif system == "Darwin":
        pkg = os.path.join(tmp, "python312.pkg")
        download("https://www.python.org/ftp/python/3.12.0/python-3.12.0-macos11.pkg", pkg)
        subprocess.check_call(["sudo", "installer", "-pkg", pkg, "-target", "/"])
        os.remove(pkg)
    else:
        if shutil.which("apt-get"):
            subprocess.check_call(["sudo", "apt-get", "update"])
            subprocess.check_call(["sudo", "apt-get", "install", "-y", "python3.12", "python3.12-venv"])
        else:
            tarball = os.path.join(tmp, "Python-3.12.0.tgz")
            download("https://www.python.org/ftp/python/3.12.0/Python-3.12.0.tgz", tarball)
            build_dir = os.path.join(tmp, "python-build")
            os.makedirs(build_dir, exist_ok=True)
            subprocess.check_call(["tar", "xf", tarball, "-C", build_dir])
            src = os.path.join(build_dir, "Python-3.12.0")
            subprocess.check_call(["bash", "-c", f"cd {src} && ./configure --prefix=/usr/local && make -j$(nproc) && sudo make install"])
    path = shutil.which("python3.12")
    if path:
        return path
    raise RuntimeError("Python 3.12 installation failed")


def bundle_dependencies(python: str) -> None:
    if not os.path.isdir(OFFLINE_DIR):
        print("Downloading dependencies for offline use...")
        subprocess.check_call([python, "-m", "pip", "download", "-r", "requirements.txt", "-d", OFFLINE_DIR])
        subprocess.check_call([python, "-m", "pip", "download", ".", "-d", OFFLINE_DIR])


def setup_environment(python: str) -> None:
    if not os.path.isdir(ENV_DIR):
        subprocess.check_call([python, "-m", "venv", ENV_DIR])
    pip = os.path.join(ENV_DIR, "Scripts" if os.name == "nt" else "bin", "pip")
    subprocess.check_call([pip, "install", "--no-index", "--find-links", OFFLINE_DIR, "--upgrade", "pip"])
    subprocess.check_call([pip, "install", "--no-index", "--find-links", OFFLINE_DIR, "-r", "requirements.txt"])
    subprocess.check_call([pip, "install", "--no-index", "--find-links", OFFLINE_DIR, "-e", "."])
    if os.path.isfile(".env.example") and not os.path.isfile(".env"):
        shutil.copy(".env.example", ".env")
        print("Copied .env.example to .env")


def main() -> None:
    python = ensure_python312()
    bundle_dependencies(python)
    setup_environment(python)
    if os.name == "nt":
        activate = f"{ENV_DIR}\\Scripts\\activate"
    else:
        activate = f"source {ENV_DIR}/bin/activate"
    print("Installation complete. Activate the environment with '\"%s\"'" % activate)


if __name__ == "__main__":
    main()
