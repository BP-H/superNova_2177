# RFC_V5_1_INIT
"""CLI stub for future federation workflows."""

import argparse
import json
import uuid
from pathlib import Path
from datetime import datetime
# SQLAlchemy 2.x exposes `select` at the top level. Importing from
# `sqlalchemy.orm` is no longer valid, so we import from the main package
# for compatibility with newer versions.
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from db_models import (
    SessionLocal,
    Harmonizer,
    UniverseBranch,
    BranchVote,
)
from governance_config import (
    is_eligible_for_fork,
    calculate_entropy_divergence,
    basis,
)
from config import Config

OUTBOX = Path(__file__).resolve().parent / "federation" / "outbox.json"


def create_fork(args: argparse.Namespace) -> None:
    db = SessionLocal()
    try:
        stmt = (
            select(Harmonizer)  # from sqlalchemy.orm
            .where(Harmonizer.username == args.creator)
        )
        user = db.execute(stmt).scalar_one_or_none()
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
            and (
                datetime.utcnow() - user.last_passive_aura_timestamp
            ).total_seconds()
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
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            print("Failed to create fork due to database constraint")
            return
        print(f"Created fork {fork.id}")
    finally:
        db.close()


def list_forks(_args: argparse.Namespace) -> None:
    db = SessionLocal()
    try:
        stmt = select(UniverseBranch)  # from sqlalchemy.orm
        forks = db.execute(stmt).scalars().all()
        for f in forks:
            try:
                config_json = json.dumps(f.config, default=str)
            except TypeError as exc:
                # pragma: no cover - unexpected type error
                config_json = f"<serialization error: {exc}>"
            print(
                f.id,
                config_json,
                f"consensus={f.consensus:.2f}",
                f"divergence={f.entropy_divergence:.2f}",
            )
    finally:
        db.close()


def fork_info(args: argparse.Namespace) -> None:
    db = SessionLocal()
    try:
        stmt = (
            select(UniverseBranch)  # from sqlalchemy.orm
            .where(UniverseBranch.id == args.fork_id)
        )
        fork = db.execute(stmt).scalar_one_or_none()
        if not fork:
            print("Fork not found")
            return
        info = {
            "id": fork.id,
            "creator_id": fork.creator_id,
            "karma_at_fork": fork.karma_at_fork,
            "config": fork.config,
            "timestamp": (
                fork.timestamp.isoformat() if fork.timestamp else None
            ),
            "status": fork.status,
            "entropy_divergence": fork.entropy_divergence,
            "consensus": fork.consensus,
        }
        try:
            print(json.dumps(info, indent=2, default=str))
        except TypeError as exc:  # pragma: no cover - unexpected type error
            print(f"Error serializing fork info: {exc}")
    finally:
        db.close()


def vote_fork(args: argparse.Namespace) -> None:
    """Cast a DAO vote for a universe fork."""
    db = SessionLocal()
    try:
        stmt = (
            select(UniverseBranch)  # from sqlalchemy.orm
            .where(UniverseBranch.id == args.fork_id)
        )
        fork = db.execute(stmt).scalar_one_or_none()
        stmt = (
            select(Harmonizer)  # from sqlalchemy.orm
            .where(Harmonizer.username == args.voter)
        )
        voter = db.execute(stmt).scalar_one_or_none()
        if not fork or not voter:
            print("Fork or voter not found")
            return
        # Avoid duplicate votes from the same harmonizer
        stmt = (
            select(BranchVote)  # from sqlalchemy.orm
            .where(
                BranchVote.branch_id == fork.id,
                BranchVote.voter_id == voter.id,
            )
        )
        existing = db.execute(stmt).scalar_one_or_none()
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
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            print("Vote already recorded for this fork")
            return

        fork.vote_count = (fork.vote_count or 0) + 1
        if vote_bool:
            fork.yes_count = (fork.yes_count or 0) + 1
        if basis is None:
            fork.consensus = fork.yes_count / fork.vote_count
        else:  # parity-based quantum consensus
            expectation = 1.0 if fork.yes_count % 2 == 0 else -1.0
            fork.consensus = (expectation + 1) / 2
        db.commit()
        print(
            f"Vote recorded. Current consensus for {fork.id}: "
            f"{fork.consensus:.2f}"
        )
    finally:
        db.close()
    # Web UI for vote submission implemented in ``forks_page``


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Federation and fork utilities"
    )
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
