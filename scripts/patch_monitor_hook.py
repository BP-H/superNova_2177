import subprocess  # nosec B404
import sys
import shutil
from pathlib import Path

# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards

sys.path.append(str(Path(__file__).resolve().parent.parent))
from governance.patch_monitor import check_patch_compliance  # noqa: E402


def main() -> int:
    git_bin = shutil.which("git") or "/usr/bin/git"
    diff = subprocess.check_output(  # nosec B607,B603
        [git_bin, "diff", "--cached"], text=True
    )
    issues = check_patch_compliance(diff)
    if issues:
        print("\n".join(issues))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
