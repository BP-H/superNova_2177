import datetime
import pytest
from sqlalchemy.exc import IntegrityError

import argparse
import federation_cli
from db_models import Harmonizer, UniverseBranch, BranchVote


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


def test_vote_fork_updates_existing_vote(monkeypatch, test_db):
    """vote_fork should update duplicate votes rather than create a new record."""
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

    class NonClosingSession:
        def __init__(self, db):
            self._db = db

        def __getattr__(self, name):
            return getattr(self._db, name)

        def close(self):  # override to keep session open
            pass

    monkeypatch.setattr(federation_cli, "SessionLocal", lambda: NonClosingSession(test_db))

    args = argparse.Namespace(fork_id=fork.id, voter=voter.username, vote="yes")
    federation_cli.vote_fork(args)

    args = argparse.Namespace(fork_id=fork.id, voter=voter.username, vote="no")
    federation_cli.vote_fork(args)

    votes = test_db.query(BranchVote).filter_by(branch_id=fork.id, voter_id=voter.id).all()
    assert len(votes) == 1
    assert votes[0].vote is False

    updated_fork = test_db.query(UniverseBranch).filter_by(id=fork.id).first()
    assert updated_fork.consensus == pytest.approx(0.0)
