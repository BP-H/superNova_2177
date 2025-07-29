# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards

from __future__ import annotations

from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    offending = [str(p) for p in repo_root.rglob("streamlit.py")]
    if offending:
        print("Found shadowing streamlit.py files:")
        for path in offending:
            print(path)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
