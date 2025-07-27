import datetime
import pytest
from sqlalchemy.exc import IntegrityError

from db_models import Harmonizer, UniverseBranch, BranchVote
import federation_cli
from governance_config import basis
import argparse


def test_branch_vote_unique_constraint(test_db):
    fork = UniverseBranch(
        id="f1",
        creator_id=None,
        karma_at_fork=0.0,
        config={},
        timestamp=datetime.datetime.utcnow(),
        status="active",
    )
    voter = Harmonizer(username="alice", email="a@example.com", hashed_password="x")
    test_db.add_all([fork, voter])
    test_db.commit()

    vote1 = BranchVote(branch_id=fork.id, voter_id=voter.id, vote=True)
    test_db.add(vote1)
    test_db.commit()

    vote2 = BranchVote(branch_id=fork.id, voter_id=voter.id, vote=False)
    test_db.add(vote2)
    with pytest.raises(IntegrityError):
        test_db.commit()
    test_db.rollback()

    votes = test_db.query(BranchVote).filter_by(branch_id=fork.id).all()
    assert len(votes) == 1


def test_vote_updates_counts(monkeypatch, test_db):
    fork = UniverseBranch(
        id="f2",
        creator_id=None,
        karma_at_fork=0.0,
        config={},
        timestamp=datetime.datetime.utcnow(),
        status="active",
    )
    voter = Harmonizer(username="bob", email="b@example.com", hashed_password="x")
    test_db.add_all([fork, voter])
    test_db.commit()

    monkeypatch.setattr(federation_cli, "SessionLocal", lambda: test_db)
    args = argparse.Namespace(fork_id=fork.id, voter=voter.username, vote="yes")
    federation_cli.vote_fork(args)

    refreshed = test_db.query(UniverseBranch).filter_by(id=fork.id).first()
    assert refreshed.vote_count == 1
    assert refreshed.yes_count == 1
    expected = 1.0 if basis is None else (1.0 if refreshed.yes_count % 2 == 0 else 0.0)
    assert refreshed.consensus == expected
