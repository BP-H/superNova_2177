import argparse
import datetime
from decimal import Decimal

import pytest

from db_models import Harmonizer, UniverseBranch, BranchVote, SessionLocal
from federation_cli import vote_fork
from governance_config import calculate_entropy_divergence, quantum_consensus
from superNova_2177 import Config


def test_calculate_entropy_divergence_numeric_types():
    cfg = {
        "KARMA_MINT_THRESHOLD": Decimal("150"),
        "SNAPSHOT_INTERVAL": 200,
    }
    result = calculate_entropy_divergence(cfg, base=Config)
    expected = (
        abs(float(cfg["KARMA_MINT_THRESHOLD"]) - float(Config.KARMA_MINT_THRESHOLD))
        + abs(float(cfg["SNAPSHOT_INTERVAL"]) - float(Config.SNAPSHOT_INTERVAL))
    ) / 2
    assert result == pytest.approx(expected)


def test_quantum_consensus_without_qutip(monkeypatch):
    monkeypatch.setattr("governance_config.basis", None)
    votes = [True, False, True, False]
    assert quantum_consensus(votes) == pytest.approx(sum(votes) / len(votes))


def test_quantum_consensus_with_qutip(monkeypatch):
    monkeypatch.setattr("governance_config.basis", lambda _d, idx: idx)
    monkeypatch.setattr("governance_config.tensor", lambda items: list(items))
    monkeypatch.setattr("governance_config.sigmaz", lambda: None)

    def fake_expect(obs, joint):
        avg = sum(joint) / len(joint)
        return 2 * avg - 1

    monkeypatch.setattr("governance_config.expect", fake_expect)
    votes = [True, True, False]
    assert quantum_consensus(votes) == pytest.approx(sum(votes) / len(votes))


def _setup_fork_and_user(db):
    user = Harmonizer(username="alice", email="a@example.com", hashed_password="x")
    fork = UniverseBranch(
        id="fork1",
        creator_id=None,
        karma_at_fork=0.0,
        config={},
        timestamp=datetime.datetime.utcnow(),
        status="active",
    )
    db.add_all([user, fork])
    db.commit()
    return fork, user


def test_vote_fork_success(monkeypatch, capsys, test_db):
    fork, user = _setup_fork_and_user(test_db)
    monkeypatch.setattr("federation_cli.quantum_consensus", lambda v: 0.75)

    args = argparse.Namespace(fork_id=fork.id, voter=user.username, vote="yes")
    vote_fork(args)

    out = capsys.readouterr().out
    assert "Vote recorded" in out
    assert "0.75" in out

    db2 = SessionLocal()
    try:
        votes = db2.query(BranchVote).filter_by(branch_id=fork.id).all()
        assert len(votes) == 1 and votes[0].vote is True
        refreshed = db2.query(UniverseBranch).filter_by(id=fork.id).first()
        assert refreshed.consensus == 0.75
    finally:
        db2.close()


def test_vote_fork_duplicate(monkeypatch, capsys, test_db):
    fork, user = _setup_fork_and_user(test_db)
    test_db.add(BranchVote(branch_id=fork.id, voter_id=user.id, vote=True))
    test_db.commit()

    args = argparse.Namespace(fork_id=fork.id, voter=user.username, vote="no")
    vote_fork(args)

    out = capsys.readouterr().out
    assert "Vote already recorded" in out
    assert test_db.query(BranchVote).filter_by(branch_id=fork.id).count() == 1


def test_vote_fork_missing_entities(capsys, test_db):
    args = argparse.Namespace(fork_id="bad", voter="unknown", vote="yes")
    vote_fork(args)
    assert "Fork or voter not found" in capsys.readouterr().out
