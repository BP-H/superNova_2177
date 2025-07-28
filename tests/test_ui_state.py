import importlib
import sys
import types

import json


def make_stub():
    stub = types.ModuleType("streamlit")
    stub.session_state = {}
    stub.secrets = {}
    def no_op(*a, **k):
        return None
    stub.experimental_rerun = no_op
    return stub


def stub_dependencies(monkeypatch):
    mpl = types.ModuleType("matplotlib")
    plt = types.ModuleType("matplotlib.pyplot")
    mpl.pyplot = plt
    monkeypatch.setitem(sys.modules, "matplotlib", mpl)
    monkeypatch.setitem(sys.modules, "matplotlib.pyplot", plt)
    monkeypatch.setitem(sys.modules, "networkx", types.ModuleType("networkx"))


def test_clear_memory_resets_state(monkeypatch):
    stub = make_stub()
    stub_dependencies(monkeypatch)
    stub.session_state.update({
        "analysis_diary": [1],
        "run_count": 3,
        "last_run": "time",
        "last_result": {"foo": "bar"},
        "show_explanation": True,
    })
    monkeypatch.setitem(sys.modules, "streamlit", stub)
    import ui
    importlib.reload(ui)
    ui.clear_memory()
    assert stub.session_state["analysis_diary"] == []
    assert stub.session_state["run_count"] == 0
    assert stub.session_state["last_result"] is None
    assert not stub.session_state["show_explanation"]


def test_export_latest_result(monkeypatch):
    stub = make_stub()
    stub_dependencies(monkeypatch)
    stub.session_state["last_result"] = {"a": 1}
    monkeypatch.setitem(sys.modules, "streamlit", stub)
    import ui
    importlib.reload(ui)
    data = ui.export_latest_result()
    assert json.loads(data) == {"a": 1}
