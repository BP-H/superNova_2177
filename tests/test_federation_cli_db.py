"""End-to-end tests for :mod:`federation_cli` using a real SQLite database."""

from __future__ import annotations

import argparse
import datetime
from datetime import UTC
from decimal import Decimal

import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import federation_cli
import governance_config
from db_models import Base, Harmonizer, UniverseBranch, BranchVote


@pytest.fixture
def cli_db(tmp_path, monkeypatch):
    """Provide a temporary database and patch session factories."""

    engine = create_engine(
        f"sqlite:///{tmp_path}/cli.db", connect_args={"check_same_thread": False}
    )
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)

    monkeypatch.setattr(federation_cli, "SessionLocal", Session)
    monkeypatch.setattr(governance_config, "SessionLocal", Session)

    yield Session

    Base.metadata.drop_all(bind=engine)


def _make_user(**kw) -> Harmonizer:
    username = kw.get("username", "u")
    defaults = dict(
        username=username,
        email=f"{username}@example.com",
        hashed_password="x",
        karma_score=10.0,
        last_passive_aura_timestamp=datetime.datetime.now(UTC)
        - datetime.timedelta(hours=2),
    )
    defaults.update(kw)
    return Harmonizer(**defaults)


def _make_fork(creator: Harmonizer) -> UniverseBranch:
    return UniverseBranch(
        id="fid",
        creator_id=creator.id,
        karma_at_fork=creator.karma_score,
        config={"d": "1.5"},
        timestamp=datetime.datetime.now(UTC),
        status="active",
    )


def test_create_fork_success(cli_db, monkeypatch, capsys):
    monkeypatch.setattr(federation_cli.Config, "FORK_COOLDOWN_SECONDS", 3600, raising=False)
    db = cli_db()
    user = _make_user(username="alice")
    db.add(user)
    db.commit()
    db.close()

    args = argparse.Namespace(creator="alice", config=["KARMA_MINT_THRESHOLD=150"])
    federation_cli.create_fork(args)
    out = capsys.readouterr().out
    assert "Created fork" in out

    db = cli_db()
    assert db.query(UniverseBranch).count() == 1
    db.close()


def test_create_fork_invalid_creator(cli_db, monkeypatch, capsys):
    monkeypatch.setattr(federation_cli.Config, "FORK_COOLDOWN_SECONDS", 0, raising=False)
    args = argparse.Namespace(creator="nobody", config=None)
    federation_cli.create_fork(args)
    out = capsys.readouterr().out.strip()
    assert out == "Creator not found"


def test_create_fork_invalid_config(cli_db, monkeypatch, capsys):
    monkeypatch.setattr(federation_cli.Config, "FORK_COOLDOWN_SECONDS", 0, raising=False)
    db = cli_db()
    user = _make_user(username="bob")
    db.add(user)
    db.commit()
    db.close()

    args = argparse.Namespace(creator="bob", config=["BAD_KEY=1"])
    federation_cli.create_fork(args)
    out = capsys.readouterr().out.strip()
    assert out.startswith("Invalid config keys")


def test_create_fork_cooldown(cli_db, monkeypatch, capsys):
    monkeypatch.setattr(federation_cli.Config, "FORK_COOLDOWN_SECONDS", 3600, raising=False)
    now = datetime.datetime.now(UTC)
    db = cli_db()
    user = _make_user(username="carol", last_passive_aura_timestamp=now)
    db.add(user)
    db.commit()
    db.close()

    args = argparse.Namespace(creator="carol", config=None)
    federation_cli.create_fork(args)
    out = capsys.readouterr().out.strip()
    assert out.startswith("Fork cooldown active")


def test_list_forks_and_info(cli_db, monkeypatch, capsys):
    monkeypatch.setattr(federation_cli.Config, "FORK_COOLDOWN_SECONDS", 0, raising=False)
    db = cli_db()
    user = _make_user(username="dan")
    db.add(user)
    db.commit()
    fork = _make_fork(user)
    db.add(fork)
    db.commit()
    fid = fork.id
    db.close()

    federation_cli.list_forks(argparse.Namespace())
    out = capsys.readouterr().out
    assert '"d": "1.5"' in out

    federation_cli.fork_info(argparse.Namespace(fork_id=fid))
    info_out = capsys.readouterr().out
    assert '"d": "1.5"' in info_out


def test_fork_info_not_found(cli_db, capsys):
    federation_cli.fork_info(argparse.Namespace(fork_id="missing"))
    out = capsys.readouterr().out.strip()
    assert out == "Fork not found"


def test_vote_fork_success_and_duplicate(cli_db, monkeypatch, capsys):
    monkeypatch.setattr(federation_cli.Config, "FORK_COOLDOWN_SECONDS", 0, raising=False)
    db = cli_db()
    voter = _make_user(username="eve")
    creator = _make_user(username="creator")
    db.add_all([voter, creator])
    db.commit()
    fork = _make_fork(creator)
    db.add(fork)
    db.commit()
    fid = fork.id
    db.close()

    args = argparse.Namespace(fork_id=fid, voter="eve", vote="yes")
    federation_cli.vote_fork(args)
    out = capsys.readouterr().out
    assert "Vote recorded" in out

    # duplicate vote
    federation_cli.vote_fork(args)
    dup = capsys.readouterr().out.strip()
    assert dup == "Vote already recorded for this fork"


def test_vote_fork_missing_records(cli_db, capsys):
    args = argparse.Namespace(fork_id="none", voter="nobody", vote="yes")
    federation_cli.vote_fork(args)
    out = capsys.readouterr().out.strip()
    assert out == "Fork or voter not found"
