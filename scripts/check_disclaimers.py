# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
import subprocess  # nosec B404
import sys
from shutil import which

from governance.patch_monitor import check_patch_compliance


def get_diff(base: str, git_cmd: str) -> str:
    """Return git diff from base to HEAD using ``git_cmd``."""
    cmd = [git_cmd, "diff", f"{base}...HEAD"]
    return subprocess.check_output(cmd, text=True)  # nosec B603


def main() -> int:
    base = sys.argv[1] if len(sys.argv) > 1 else "origin/main"
    git_cmd = which("git")
    if git_cmd is None:
        print("git executable not found; install git with `apt install git`")
        return 1
    try:
        diff = get_diff(base, git_cmd)
    except FileNotFoundError:
        print("git executable not found; install git with `apt install git`")
        return 1
    except subprocess.CalledProcessError as e:
        print(f"Failed to generate diff: {e}")
        return 1
    issues = check_patch_compliance(diff)
    if issues:
        print("\n".join(issues))
        return 1
    print("Patch contains required disclaimers or they already exist in files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
