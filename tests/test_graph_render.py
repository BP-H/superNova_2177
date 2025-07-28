import importlib
import sys
import types


def make_stub_streamlit():
    stub = types.ModuleType("streamlit")

    class Dummy:
        def __enter__(self):
            return None

        def __exit__(self, *exc):
            pass

    def spinner(*a, **k):
        return Dummy()

    stub.spinner = spinner
    stub.warning = lambda *a, **k: None
    stub.metric = lambda *a, **k: None
    stub.markdown = lambda *a, **k: None
    stub.subheader = lambda *a, **k: None
    stub.json = lambda *a, **k: None
    stub.plotly_chart = lambda *a, **k: None
    components = types.SimpleNamespace(
        v1=types.SimpleNamespace(html=lambda *a, **k: None)
    )
    stub.components = components
    return stub


def test_run_analysis_graph(monkeypatch):
    stub = make_stub_streamlit()
    monkeypatch.setitem(sys.modules, "streamlit", stub)
    ui = importlib.import_module("ui")
    importlib.reload(ui)

    monkeypatch.setattr(ui, "analyze_validation_integrity", lambda v: {})
    monkeypatch.setattr(
        ui,
        "build_validation_graph",
        lambda v: {
            "edges": [("A", "B", 0.5)],
            "nodes": {"A", "B"},
        },
    )

    ui.run_analysis(
        [
            {"validator_id": "A", "hypothesis_id": "H1", "score": 0.7},
            {"validator_id": "B", "hypothesis_id": "H1", "score": 0.6},
        ]
    )
