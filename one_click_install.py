import os
import platform
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import argparse

OFFLINE_DIR = "offline_deps"
ENV_DIR = "venv"


def download(url: str, dest: str) -> None:
    print(f"Downloading {url}...")
    urllib.request.urlretrieve(url, dest)


def ensure_python(version: str) -> str:
    """Return path to a Python ``version`` interpreter, installing if necessary."""
    target_tuple = tuple(int(v) for v in version.split("."))
    if sys.version_info >= target_tuple:
        return sys.executable
    exes = (
        f"python{version}",
        f"python{version.replace('.', '')}",
        f"python{version}.exe",
        "python.exe",
    )
    for exe in exes:
        path = shutil.which(exe)
        if path:
            try:
                out = subprocess.check_output([path, "--version"], text=True)
            except Exception:
                continue
            if out.startswith(f"Python {version}"):
                return path
    system = platform.system()
    tmp = tempfile.gettempdir()
    if system == "Windows":
        installer = os.path.join(tmp, f"python{version.replace('.', '')}.exe")
        py_patch = f"{version}.0"
        download(
            f"https://www.python.org/ftp/python/{py_patch}/python-{py_patch}-amd64.exe",
            installer,
        )
        subprocess.check_call([installer, "/quiet", "InstallAllUsers=1", "PrependPath=1"])
        os.remove(installer)
    elif system == "Darwin":
        pkg = os.path.join(tmp, f"python{version.replace('.', '')}.pkg")
        py_patch = f"{version}.0"
        download(
            f"https://www.python.org/ftp/python/{py_patch}/python-{py_patch}-macos11.pkg",
            pkg,
        )
        subprocess.check_call(["sudo", "installer", "-pkg", pkg, "-target", "/"])
        os.remove(pkg)
    else:
        if shutil.which("apt-get"):
            subprocess.check_call(["sudo", "apt-get", "update"])
            pkg = f"python{version}"
            subprocess.check_call(["sudo", "apt-get", "install", "-y", pkg, f"{pkg}-venv"])
        else:
            py_patch = f"{version}.0"
            tarball = os.path.join(tmp, f"Python-{py_patch}.tgz")
            download(
                f"https://www.python.org/ftp/python/{py_patch}/Python-{py_patch}.tgz",
                tarball,
            )
            build_dir = os.path.join(tmp, "python-build")
            os.makedirs(build_dir, exist_ok=True)
            subprocess.check_call(["tar", "xf", tarball, "-C", build_dir])
            src = os.path.join(build_dir, f"Python-{py_patch}")
            subprocess.check_call([
                "bash",
                "-c",
                f"cd {src} && ./configure --prefix=/usr/local && make -j$(nproc) && sudo make install",
            ])
    path = shutil.which(f"python{version}")
    if path:
        return path
    raise RuntimeError(f"Python {version} installation failed")


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
    parser = argparse.ArgumentParser(description="Set up the development environment")
    parser.add_argument(
        "--python-version",
        default="3.12",
        help="Python version to use/install (default: 3.12)",
    )
    args = parser.parse_args()

    python = ensure_python(args.python_version)
    bundle_dependencies(python)
    setup_environment(python)
    if os.name == "nt":
        activate = f"{ENV_DIR}\\Scripts\\activate"
    else:
        activate = f"source {ENV_DIR}/bin/activate"
    print("Installation complete. Activate the environment with '\"%s\"'" % activate)


if __name__ == "__main__":
    main()
