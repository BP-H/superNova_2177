# RFC_V5_1_INIT
"""CLI stub for future federation workflows."""

import argparse
import json
import uuid
from pathlib import Path
from datetime import datetime

from db_models import SessionLocal, Harmonizer, UniverseFork
from governance_config import is_eligible_for_fork
from superNova_2177 import Config

OUTBOX = Path(__file__).resolve().parent / "federation" / "outbox.json"


def create_fork(args: argparse.Namespace) -> None:
    db = SessionLocal()
    try:
        user = db.query(Harmonizer).filter_by(username=args.creator).first()
        if not user:
            print("Creator not found")
            return
        if not is_eligible_for_fork(user, db):
            print("Creator not eligible for forking")
            return
        config = dict(pair.split("=", 1) for pair in args.config or [])
        invalid_keys = [k for k in config if not hasattr(Config, k)]
        if invalid_keys:
            print(f"Invalid config keys: {', '.join(invalid_keys)}")
            return
        cooldown = Config.FORK_COOLDOWN_SECONDS
        if (
            user.last_passive_aura_timestamp
            and (datetime.utcnow() - user.last_passive_aura_timestamp).total_seconds()
            < cooldown
        ):
            print("Fork cooldown active. Please wait before forking again.")
            return
        fork = UniverseFork(
            id=str(uuid.uuid4()),
            creator_id=user.id,
            karma_at_fork=user.karma_score,
            config=config,
            timestamp=datetime.utcnow(),
            status="active",
        )
        db.add(fork)
        user.last_passive_aura_timestamp = datetime.utcnow()
        db.commit()
        print(f"Created fork {fork.id}")
    finally:
        db.close()


def list_forks(_args: argparse.Namespace) -> None:
    db = SessionLocal()
    try:
        forks = db.query(UniverseFork).all()
        for f in forks:
            print(f.id, json.dumps(f.config))
    finally:
        db.close()


def fork_info(args: argparse.Namespace) -> None:
    db = SessionLocal()
    try:
        fork = db.query(UniverseFork).filter_by(id=args.fork_id).first()
        if not fork:
            print("Fork not found")
            return
        info = {
            "id": fork.id,
            "creator_id": fork.creator_id,
            "karma_at_fork": fork.karma_at_fork,
            "config": fork.config,
            "timestamp": fork.timestamp.isoformat() if fork.timestamp else None,
            "status": fork.status,
        }
        print(json.dumps(info, indent=2))
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Federation and fork utilities")
    sub = parser.add_subparsers(dest="command")

    parser.add_argument("--send", help="Path to message JSON", required=False)

    create_p = sub.add_parser("create", help="Create a universe fork")
    create_p.add_argument("--creator", required=True)
    create_p.add_argument("--config", nargs="*", help="key=value pairs")
    create_p.set_defaults(func=create_fork)

    list_p = sub.add_parser("list", help="List forks")
    list_p.set_defaults(func=list_forks)

    info_p = sub.add_parser("info", help="Show fork info")
    info_p.add_argument("fork_id")
    info_p.set_defaults(func=fork_info)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
        return
    if args.send:
        print(f"Queuing {args.send} for federation")
    else:
        print(f"Outbox located at {OUTBOX}")


if __name__ == "__main__":
    main()
