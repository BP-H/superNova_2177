#!/usr/bin/env python3
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parent
    system = platform.system()

    if system == "Windows":
        ps1 = root / "online_install.ps1"
        bat = root / "install" / "install_desktop.bat"
        if shutil.which("powershell"):
            cmd = ["powershell", "-ExecutionPolicy", "Bypass", str(ps1)]
        else:
            cmd = ["cmd", "/c", str(bat)]
    elif system == "Darwin":
        cmd = ["bash", str(root / "install" / "install_desktop.sh")]
    elif system == "Linux":
        if os.environ.get("ANDROID_ROOT") or os.environ.get("TERMUX_VERSION"):
            cmd = ["bash", str(root / "install" / "install_android.sh")]
        else:
            cmd = ["bash", str(root / "online_install.sh")]
    else:
        print(f"Unsupported operating system: {system}", file=sys.stderr)
        sys.exit(1)

    subprocess.check_call(cmd)


if __name__ == "__main__":
    main()
