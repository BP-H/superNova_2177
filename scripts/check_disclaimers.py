import subprocess  # nosec B404
import sys

from governance.patch_monitor import check_patch_compliance


def get_diff(base: str) -> str:
    """Return git diff from base to HEAD."""
    cmd = ["git", "diff", f"{base}...HEAD"]
    return subprocess.check_output(cmd, text=True)  # nosec B603


def main() -> int:
    base = sys.argv[1] if len(sys.argv) > 1 else "origin/main"
    try:
        diff = get_diff(base)
    except subprocess.CalledProcessError as e:
        print(f"Failed to generate diff: {e}")
        return 1
    issues = check_patch_compliance(diff)
    if issues:
        print("\n".join(issues))
        return 1
    print("Patch contains required disclaimers.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
