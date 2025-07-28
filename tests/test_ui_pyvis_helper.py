import importlib
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


def test_render_pyvis_to_html(monkeypatch):
    ui = load_ui(monkeypatch)

    class DummyNetwork:
        def __init__(self):
            self.called = False
        def generate_html(self, **kwargs):
            self.called = True
            return "<html><body>graph</body></html>"

    net = DummyNetwork()
    html = ui.render_pyvis_to_html(net)
    assert html.startswith("<html")
    assert net.called
