# RFC_V5_1_INIT
"""CLI stub for future federation workflows."""

import argparse
import json
import uuid
from pathlib import Path
from datetime import datetime

from db_models import (
    SessionLocal,
    Harmonizer,
    UniverseBranch,
    BranchVote,
)
from governance_config import (
    is_eligible_for_fork,
    calculate_entropy_divergence,
    quantum_consensus,
)
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
        invalid_keys = [k for k in config if not hasattr(Config, k) and k != "entropy_threshold"]
        if invalid_keys:
            print(f"Invalid config keys: {', '.join(invalid_keys)}")
            return

        numeric_errors = []
        for key, value in config.items():
            try:
                if float(value) <= 0:
                    numeric_errors.append(key)
            except ValueError:
                # Non-numeric values are ignored
                continue
        if numeric_errors:
            joined = ", ".join(numeric_errors)
            print(f"Parameters must be > 0: {joined}")
            return
        cooldown = Config.FORK_COOLDOWN_SECONDS
        if (
            user.last_passive_aura_timestamp
            and (datetime.utcnow() - user.last_passive_aura_timestamp).total_seconds()
            < cooldown
        ):
            print("Fork cooldown active. Please wait before forking again.")
            return
        divergence = calculate_entropy_divergence(config)
        fork = UniverseBranch(
            id=str(uuid.uuid4()),
            creator_id=user.id,
            karma_at_fork=user.karma_score,
            config=config,
            timestamp=datetime.utcnow(),
            status="active",
            entropy_divergence=divergence,
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
        forks = db.query(UniverseBranch).all()
        for f in forks:
            print(
                f.id,
                json.dumps(f.config),
                f"consensus={f.consensus:.2f}",
                f"divergence={f.entropy_divergence:.2f}",
            )
    finally:
        db.close()


def fork_info(args: argparse.Namespace) -> None:
    db = SessionLocal()
    try:
        fork = db.query(UniverseBranch).filter_by(id=args.fork_id).first()
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
            "entropy_divergence": fork.entropy_divergence,
            "consensus": fork.consensus,
        }
        print(json.dumps(info, indent=2))
    finally:
        db.close()


def vote_fork(args: argparse.Namespace) -> None:
    """Cast a DAO vote for a universe fork."""
    db = SessionLocal()
    try:
        fork = db.query(UniverseBranch).filter_by(id=args.fork_id).first()
        voter = db.query(Harmonizer).filter_by(username=args.voter).first()
        if not fork or not voter:
            print("Fork or voter not found")
            return
        # Avoid duplicate votes from the same harmonizer
        existing = db.query(BranchVote).filter_by(
            branch_id=fork.id, voter_id=voter.id
        ).first()
        if existing:
            print("Vote already recorded for this fork")
            return
        vote_bool = args.vote.lower() == "yes"
        record = BranchVote(
            branch_id=fork.id,
            voter_id=voter.id,
            vote=vote_bool,
        )
        db.add(record)
        db.commit()

        votes = [v.vote for v in db.query(BranchVote).filter_by(branch_id=fork.id).all()]
        fork.consensus = quantum_consensus(votes)
        db.commit()
        print(
            f"Vote recorded. Current consensus for {fork.id}: {fork.consensus:.2f}"
        )
    finally:
        db.close()
    # TODO: Add web UI for vote submission


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

    vote_p = sub.add_parser("vote", help="Vote on a fork")
    vote_p.add_argument("fork_id")
    vote_p.add_argument("--voter", required=True)
    vote_p.add_argument("--vote", choices=["yes", "no"], required=True)
    vote_p.set_defaults(func=vote_fork)

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
