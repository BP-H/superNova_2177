# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
import importlib
import json
import sys
import types


def load_ui(monkeypatch):
    stub = types.ModuleType("streamlit")

    def __getattr__(name):
        if name == "secrets":
            raise RuntimeError("no secrets")
        return lambda *a, **k: None

    stub.__getattr__ = __getattr__
    monkeypatch.setitem(sys.modules, "streamlit", stub)

    mpl = types.ModuleType("matplotlib")
    plt = types.ModuleType("matplotlib.pyplot")
    mpl.pyplot = plt
    monkeypatch.setitem(sys.modules, "matplotlib", mpl)
    monkeypatch.setitem(sys.modules, "matplotlib.pyplot", plt)

    return importlib.reload(importlib.import_module("ui"))


def test_clear_memory_resets_state(monkeypatch):
    ui = load_ui(monkeypatch)
    state = {
        "analysis_diary": [1],
        "run_count": 5,
        "last_result": {"a": 1},
        "last_run": "ts",
    }
    ui.clear_memory(state)
    assert state["analysis_diary"] == []
    assert state["run_count"] == 0
    assert state["last_result"] is None
    assert state["last_run"] is None


def test_export_latest_result(monkeypatch):
    ui = load_ui(monkeypatch)
    state = {"last_result": {"foo": "bar"}}
    blob = ui.export_latest_result(state)
    data = json.loads(blob)
    assert data == {"foo": "bar"}


def test_diff_results(monkeypatch):
    ui = load_ui(monkeypatch)
    old = {"a": 1}
    new = {"a": 2}
    diff = ui.diff_results(old, new)
    assert "-  \"a\": 1" in diff
    assert "+  \"a\": 2" in diff
