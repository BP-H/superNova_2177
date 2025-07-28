import subprocess  # nosec B404
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from governance.patch_monitor import check_patch_compliance  # noqa: E402


def main() -> int:
    try:
        diff = subprocess.check_output(  # nosec B607,B603
            ["git", "diff", "--cached"], text=True
        )
    except FileNotFoundError:
        print("git executable not found")
        return 1
    except subprocess.CalledProcessError as e:
        print(f"Failed to generate diff: {e}")
        return 1
    issues = check_patch_compliance(diff)
    if issues:
        print("\n".join(issues))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
