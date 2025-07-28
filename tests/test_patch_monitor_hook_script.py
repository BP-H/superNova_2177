import subprocess

import pytest

from scripts import patch_monitor_hook


def test_main_git_missing(monkeypatch, capsys):
    monkeypatch.setattr(patch_monitor_hook, "which", lambda cmd: None)
    assert patch_monitor_hook.main() == 1
    out = capsys.readouterr().out.strip()
    assert "git executable not found; install git with `apt install git`" in out


def test_main_git_error(monkeypatch, capsys):
    monkeypatch.setattr(patch_monitor_hook, "which", lambda cmd: "/git")

    def fake_check_output(cmd, text=True):
        raise subprocess.CalledProcessError(1, cmd)

    monkeypatch.setattr(patch_monitor_hook, "which", lambda cmd: "/git")
    monkeypatch.setattr(
        patch_monitor_hook.subprocess, "check_output", fake_check_output
    )
    assert patch_monitor_hook.main() == 1
    out = capsys.readouterr().out.strip()
    assert "Failed to generate diff" in out


def test_main_success(monkeypatch):
    monkeypatch.setattr(patch_monitor_hook, "which", lambda cmd: "/git")
    monkeypatch.setattr(
        patch_monitor_hook.subprocess, "check_output", lambda *a, **k: "diff"
    )
    monkeypatch.setattr(patch_monitor_hook, "check_patch_compliance", lambda diff: [])
    assert patch_monitor_hook.main() == 0
