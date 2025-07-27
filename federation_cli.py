# RFC_V5_1_INIT
"""CLI stub for future federation workflows."""

import argparse
from pathlib import Path

OUTBOX = Path(__file__).resolve().parent / "federation" / "outbox.json"


def main() -> None:
    parser = argparse.ArgumentParser(description="Federation stub")
    parser.add_argument("--send", help="Path to message JSON", required=False)
    args = parser.parse_args()
    if args.send:
        print(f"Queuing {args.send} for federation")
    else:
        print(f"Outbox located at {OUTBOX}")


if __name__ == "__main__":
    main()
