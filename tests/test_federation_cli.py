import types
import datetime
import pytest

from federation_cli import create_fork, list_forks, vote_fork
from db_models import Harmonizer, UniverseBranch, BranchVote
from superNova_2177 import Config


def ns(**kwargs):
    return types.SimpleNamespace(**kwargs)


def test_create_and_list_fork(test_db, capsys, monkeypatch):
    monkeypatch.setattr(Config, "FORK_COOLDOWN_SECONDS", 0, raising=False)
    user = Harmonizer(username="u1", email="u1@example.com", hashed_password="x", karma_score=10)
    test_db.add(user)
    test_db.commit()

    create_fork(ns(creator="u1", config=None))

    fork = test_db.query(UniverseBranch).filter_by(creator_id=user.id).first()
    assert fork is not None

    list_forks(ns())
    output = capsys.readouterr().out
    assert fork.id in output


def test_vote_fork_updates_consensus(test_db, monkeypatch):
    monkeypatch.setattr(Config, "FORK_COOLDOWN_SECONDS", 0, raising=False)
    alice = Harmonizer(username="alice", email="a@example.com", hashed_password="x", karma_score=5)
    bob = Harmonizer(username="bob", email="b@example.com", hashed_password="x", karma_score=5)
    test_db.add_all([alice, bob])
    test_db.commit()

    create_fork(ns(creator="alice", config=None))
    fork = test_db.query(UniverseBranch).filter_by(creator_id=alice.id).first()

    vote_fork(ns(fork_id=fork.id, voter="alice", vote="yes"))
    test_db.refresh(fork)
    assert pytest.approx(1.0) == fork.consensus
    assert test_db.query(BranchVote).filter_by(branch_id=fork.id).count() == 1

    vote_fork(ns(fork_id=fork.id, voter="bob", vote="no"))
    test_db.refresh(fork)
    assert pytest.approx(0.5) == fork.consensus
    assert test_db.query(BranchVote).filter_by(branch_id=fork.id).count() == 2


def test_vote_fork_duplicate_vote(test_db, capsys, monkeypatch):
    monkeypatch.setattr(Config, "FORK_COOLDOWN_SECONDS", 0, raising=False)
    voter = Harmonizer(username="dave", email="d@example.com", hashed_password="x", karma_score=5)
    test_db.add(voter)
    test_db.commit()

    create_fork(ns(creator="dave", config=None))
    fork = test_db.query(UniverseBranch).filter_by(creator_id=voter.id).first()

    vote_fork(ns(fork_id=fork.id, voter="dave", vote="yes"))
    vote_fork(ns(fork_id=fork.id, voter="dave", vote="yes"))
    out = capsys.readouterr().out
    assert "already recorded" in out
    assert test_db.query(BranchVote).filter_by(branch_id=fork.id).count() == 1
    test_db.refresh(fork)
    assert pytest.approx(1.0) == fork.consensus


def test_expired_vote_still_counted(test_db, monkeypatch):
    monkeypatch.setattr(Config, "FORK_COOLDOWN_SECONDS", 0, raising=False)
    u1 = Harmonizer(username="u1", email="u1@example.com", hashed_password="x", karma_score=5)
    u2 = Harmonizer(username="u2", email="u2@example.com", hashed_password="x", karma_score=5)
    test_db.add_all([u1, u2])
    test_db.commit()

    create_fork(ns(creator="u1", config=None))
    fork = test_db.query(UniverseBranch).filter_by(creator_id=u1.id).first()

    vote_fork(ns(fork_id=fork.id, voter="u1", vote="yes"))
    old_vote = test_db.query(BranchVote).filter_by(branch_id=fork.id, voter_id=u1.id).first()
    old_vote.timestamp = datetime.datetime.utcnow() - datetime.timedelta(hours=Config.VOTING_DEADLINE_HOURS + 1)
    test_db.commit()

    vote_fork(ns(fork_id=fork.id, voter="u2", vote="yes"))
    test_db.refresh(fork)
    assert test_db.query(BranchVote).filter_by(branch_id=fork.id).count() == 2
    assert pytest.approx(1.0) == fork.consensus
