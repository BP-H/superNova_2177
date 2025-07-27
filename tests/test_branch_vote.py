import argparse
import datetime
import pytest
from sqlalchemy.exc import IntegrityError

from db_models import (
    SessionLocal,
    init_db,
    Base,
    engine,
    Harmonizer,
    UniverseBranch,
    BranchVote,
)
from federation_cli import vote_fork


def test_branch_vote_unique_constraint():
    init_db()
    db = SessionLocal()
    try:
        h = Harmonizer(
            id=1,
            username="alice",
            email="alice@example.com",
            hashed_password="x",
            karma_score=0,
        )
        b = UniverseBranch(
            id="b1",
            creator_id=1,
            karma_at_fork=0,
            config={},
            timestamp=datetime.datetime.utcnow(),
            status="active",
        )
        db.add_all([h, b])
        db.commit()

        vote1 = BranchVote(branch_id="b1", voter_id=1, vote=True)
        db.add(vote1)
        db.commit()

        vote2 = BranchVote(branch_id="b1", voter_id=1, vote=False)
        db.add(vote2)
        with pytest.raises(IntegrityError):
            db.commit()
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_vote_fork_prevents_duplicate(capsys):
    init_db()
    db = SessionLocal()
    try:
        h = Harmonizer(
            id=2,
            username="bob",
            email="bob@example.com",
            hashed_password="y",
            karma_score=0,
        )
        b = UniverseBranch(
            id="b2",
            creator_id=2,
            karma_at_fork=0,
            config={},
            timestamp=datetime.datetime.utcnow(),
            status="active",
        )
        db.add_all([h, b])
        db.commit()
    finally:
        db.close()

    args = argparse.Namespace(fork_id="b2", voter="bob", vote="yes")
    vote_fork(args)
    vote_fork(args)
    out = capsys.readouterr().out.lower()
    assert "already voted" in out
    Base.metadata.drop_all(bind=engine)


