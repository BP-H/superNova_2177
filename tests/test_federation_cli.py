import argparse
import datetime
from decimal import Decimal
from types import SimpleNamespace

import federation_cli
from federation_cli import list_forks, fork_info


class DummyResult:
    def __init__(self, value):
        self.value = value

    def scalar_one_or_none(self):
        return self.value

    def scalars(self):
        class _Scalar:
            def __init__(self, val):
                self.val = val

            def all(self):
                return [self.val]

        return _Scalar(self.value)


class DummySession:
    def __init__(self, fork):
        self.fork = fork

    def execute(self, stmt):
        params = stmt.compile().params
        if params:
            val = next(iter(params.values()))
            value = self.fork if val == self.fork.id or val == self.fork.creator_id else None
        else:
            value = self.fork
        return DummyResult(value)

    def close(self):
        pass


def _patch_session(monkeypatch, fork):
    monkeypatch.setattr(federation_cli, "SessionLocal", lambda: DummySession(fork))


def _make_fork():
    return SimpleNamespace(
        id="fid",
        creator_id=1,
        karma_at_fork=0.0,
        config={"d": Decimal("1.5")},
        timestamp=datetime.datetime.utcnow(),
        status="active",
        entropy_divergence=0.0,
        consensus=0.0,
    )


def test_list_forks_serializes_decimal_config(monkeypatch, capsys):
    fork = _make_fork()
    _patch_session(monkeypatch, fork)
    list_forks(argparse.Namespace())
    out = capsys.readouterr().out
    assert '"d": "1.5"' in out


def test_fork_info_serializes_decimal_config(monkeypatch, capsys):
    fork = _make_fork()
    _patch_session(monkeypatch, fork)
    fork_info(argparse.Namespace(fork_id=fork.id))
    out = capsys.readouterr().out
    assert '"d": "1.5"' in out
