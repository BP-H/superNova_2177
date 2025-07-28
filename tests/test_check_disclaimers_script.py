import subprocess

import pytest

from scripts import check_disclaimers


def test_main_git_missing(monkeypatch, capsys):
    monkeypatch.setattr(check_disclaimers, "which", lambda cmd: None)
    assert check_disclaimers.main() == 1
    out = capsys.readouterr().out.strip()
    assert "install git" in out


def test_main_git_error(monkeypatch, capsys):
    monkeypatch.setattr(check_disclaimers, "which", lambda cmd: "/git")

    def fake_check_output(cmd, text=True):
        raise subprocess.CalledProcessError(1, cmd)

    monkeypatch.setattr(check_disclaimers.subprocess, "check_output", fake_check_output)
    assert check_disclaimers.main() == 1
    out = capsys.readouterr().out.strip()
    assert "Failed to generate diff" in out


def test_main_success(monkeypatch):
    monkeypatch.setattr(check_disclaimers, "which", lambda cmd: "/git")
    monkeypatch.setattr(check_disclaimers.subprocess, "check_output", lambda *a, **k: "diff")
    monkeypatch.setattr(check_disclaimers, "check_patch_compliance", lambda diff: [])
    assert check_disclaimers.main() == 0
