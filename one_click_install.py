import os
import platform
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import hashlib

try:
    from tqdm import tqdm
except Exception:  # pragma: no cover - optional dependency
    subprocess.run([sys.executable, "-m", "pip", "install", "tqdm"], check=True)
    from tqdm import tqdm

OFFLINE_DIR = "offline_deps"
ENV_DIR = "venv"


def run_cmd(cmd: list[str]) -> None:
    """Run *cmd* with logging."""
    print(f"$ {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


def remove_temp_files() -> None:
    """Delete known leftover files if they exist."""
    for name in ["graph.html"]:
        try:
            os.remove(name)
            print(f"Removed stale file {name}")
        except FileNotFoundError:
            continue
        except Exception as exc:  # pragma: no cover - ignore cleanup issues
            print(f"Could not remove {name}: {exc}")

# Known SHA-256 checksums for bundled Python installers
# These values are used to verify downloads before execution.
PYTHON_INSTALLER_HASHES = {
    # SHA256 values for the Windows and macOS installers are not currently
    # bundled. Verification will be skipped for these downloads with a warning.
    "https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe": None,
    "https://www.python.org/ftp/python/3.12.0/python-3.12.0-macos11.pkg": None,
    "https://www.python.org/ftp/python/3.12.0/Python-3.12.0.tgz": "51412956d24a1ef7c97f1cb5f70e185c13e3de1f50d131c0aac6338080687afb",
}


def download(url: str, dest: str, expected_sha256: str | None = None) -> None:
    """Fetch *url* to *dest* and verify its SHA-256 if known."""
    if expected_sha256 is None:
        expected_sha256 = PYTHON_INSTALLER_HASHES.get(url)
        if expected_sha256 is None:
            print(
                f"Warning: no SHA256 checksum available for {url}; skipping verification."
            )
    print(f"Downloading {url}...")
    with urllib.request.urlopen(url) as resp, open(dest, "wb") as f:
        total = resp.length or int(resp.headers.get("Content-Length", 0))
        with tqdm(total=total, unit="B", unit_scale=True, desc=os.path.basename(dest)) as pbar:
            while True:
                chunk = resp.read(8192)
                if not chunk:
                    break
                f.write(chunk)
                pbar.update(len(chunk))
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
                out = subprocess.run(
                    [path, "--version"], capture_output=True, text=True, check=True
                ).stdout
            except Exception:
                continue
            if out.startswith("Python 3.12"):
                return path
    system = platform.system()
    tmp = tempfile.gettempdir()
    if system == "Windows":
        installer = os.path.join(tmp, "python312.exe")
        download("https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe", installer)
        run_cmd([installer, "/quiet", "InstallAllUsers=1", "PrependPath=1"])
        os.remove(installer)
    elif system == "Darwin":
        pkg = os.path.join(tmp, "python312.pkg")
        download("https://www.python.org/ftp/python/3.12.0/python-3.12.0-macos11.pkg", pkg)
        run_cmd(["sudo", "installer", "-pkg", pkg, "-target", "/"])
        os.remove(pkg)
    else:
        if shutil.which("apt-get"):
            run_cmd(["sudo", "apt-get", "update"])
            run_cmd(["sudo", "apt-get", "install", "-y", "python3.12", "python3.12-venv"])
        else:
            tarball = os.path.join(tmp, "Python-3.12.0.tgz")
            download("https://www.python.org/ftp/python/3.12.0/Python-3.12.0.tgz", tarball)
            build_dir = os.path.join(tmp, "python-build")
            os.makedirs(build_dir, exist_ok=True)
            run_cmd(["tar", "xf", tarball, "-C", build_dir])
            src = os.path.join(build_dir, "Python-3.12.0")
            run_cmd([
                "bash",
                "-c",
                f"cd {src} && ./configure --prefix=/usr/local && make -j$(nproc) && sudo make install",
            ])
    path = shutil.which("python3.12")
    if path:
        return path
    raise RuntimeError("Python 3.12 installation failed")


def bundle_dependencies(python: str) -> None:
    if not os.path.isdir(OFFLINE_DIR):
        print("Downloading dependencies for offline use...")
        run_cmd([python, "-m", "pip", "download", "-r", "requirements.txt", "-d", OFFLINE_DIR])
        run_cmd([python, "-m", "pip", "download", ".", "-d", OFFLINE_DIR])


def setup_environment(python: str) -> None:
    if not os.path.isdir(ENV_DIR):
        run_cmd([python, "-m", "venv", ENV_DIR])
    pip = os.path.join(ENV_DIR, "Scripts" if os.name == "nt" else "bin", "pip")
    run_cmd([pip, "install", "--no-index", "--find-links", OFFLINE_DIR, "--upgrade", "pip"])
    run_cmd([pip, "install", "--no-index", "--find-links", OFFLINE_DIR, "-r", "requirements.txt"])
    run_cmd([pip, "install", "--no-index", "--find-links", OFFLINE_DIR, "-e", "."])
    if os.path.isfile(".env.example") and not os.path.isfile(".env"):
        shutil.copy(".env.example", ".env")
        print("Copied .env.example to .env")


def main() -> None:
    print("\n## superNova_2177 One Click Installer")
    remove_temp_files()
    try:
        print("### Ensuring Python 3.12...")
        python = ensure_python312()
        print(f"Using interpreter: {python}")
        print("### Bundling dependencies...")
        bundle_dependencies(python)
        print("### Setting up virtual environment...")
        setup_environment(python)
    except Exception as exc:
        print(f"❌ Installation failed: {exc}")
        sys.exit(1)

    if os.name == "nt":
        activate = f"{ENV_DIR}\\Scripts\\activate"
    else:
        activate = f"source {ENV_DIR}/bin/activate"
    print(f"✅ Installation complete. Activate the environment with '{activate}'")


if __name__ == "__main__":
    main()
