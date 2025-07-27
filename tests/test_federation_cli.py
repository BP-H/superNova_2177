import argparse
from federation_cli import create_fork
from db_models import Harmonizer


def test_create_fork_numeric_validation(monkeypatch, capsys, test_db):
    user = Harmonizer(
        username="alice",
        email="a@example.com",
        hashed_password="pw",
        karma_score=100.0,
    )
    test_db.add(user)
    test_db.commit()
    monkeypatch.setattr("federation_cli.SessionLocal", lambda: test_db)

    args = argparse.Namespace(creator="alice", config=["entropy_threshold=-1"])
    create_fork(args)
    out = capsys.readouterr().out
    assert "Parameters must be > 0" in out
