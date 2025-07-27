import argparse
import datetime

import federation_cli as cli

class _Fork:
    id = "f1"
    creator_id = None
    karma_at_fork = 0.0
    config = {"bad": {1}}
    timestamp = datetime.datetime.utcnow()
    status = "active"
    entropy_divergence = 0.0
    consensus = 0.0

class _Query:
    def all(self):
        return [_Fork]

    def filter_by(self, **_kw):
        return self

    def first(self):
        return _Fork

class _Session:
    def query(self, *_a, **_kw):
        return _Query()

    def close(self):
        pass

def _factory():
    return _Session()

def test_serialization_fallback(monkeypatch, capsys):
    monkeypatch.setattr(cli, "SessionLocal", _factory)
    cli.list_forks(argparse.Namespace())
    out = capsys.readouterr().out
    assert "Warning: failed to serialize config" in out
    assert "{1}" in out

    cli.fork_info(argparse.Namespace(fork_id="f1"))
    out = capsys.readouterr().out
    assert "Warning: failed to serialize info" in out
    assert "{1}" in out
