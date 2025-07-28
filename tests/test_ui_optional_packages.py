import importlib
import sys
import types


def load_ui(monkeypatch, missing=None):
    stub = types.ModuleType("streamlit")

    def __getattr__(name):
        if name == "secrets":
            raise RuntimeError("no secrets")
        if name == "spinner":
            class Dummy:
                def __enter__(self):
                    return self
                def __exit__(self, exc_type, exc, tb):
                    pass
            return lambda *a, **k: Dummy()
        if name == "components":
            return types.SimpleNamespace(v1=types.SimpleNamespace(html=lambda *a, **k: None))
        return lambda *a, **k: None

    stub.__getattr__ = __getattr__
    monkeypatch.setitem(sys.modules, "streamlit", stub)

    mpl = types.ModuleType("matplotlib")
    plt = types.ModuleType("matplotlib.pyplot")
    mpl.pyplot = plt
    monkeypatch.setitem(sys.modules, "matplotlib", mpl)
    monkeypatch.setitem(sys.modules, "matplotlib.pyplot", plt)

    for mod in missing or []:
        monkeypatch.delitem(sys.modules, mod, raising=False)

    import streamlit_helpers
    importlib.reload(streamlit_helpers)
    ui = importlib.reload(importlib.import_module("ui"))
    return ui


def test_run_analysis_without_optional_graph_libs(monkeypatch):
    ui = load_ui(monkeypatch, missing=["plotly", "plotly.graph_objects", "pyvis", "pyvis.network"])
    result = ui.run_analysis([
        {"validator_id": "A", "hypothesis_id": "H", "score": 0.5}
    ])
    assert isinstance(result, dict)
    assert "integrity_analysis" in result

