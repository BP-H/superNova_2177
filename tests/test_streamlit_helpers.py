import importlib
import sys
import types


def test_alert_handles_missing_escape(monkeypatch):
    stub = types.ModuleType("streamlit")

    calls = []

    def markdown(text, **kwargs):
        calls.append(text)

    stub.markdown = markdown
    stub.text_util = types.ModuleType("streamlit.text_util")
    # no escape_markdown attribute provided on stub or text_util

    monkeypatch.setitem(sys.modules, "streamlit", stub)
    monkeypatch.setitem(sys.modules, "streamlit.text_util", stub.text_util)

    helpers = importlib.reload(importlib.import_module("streamlit_helpers"))
    helpers.alert("hello")
    assert calls


def test_graph_to_graphml_buffer(monkeypatch):
    helpers = importlib.reload(importlib.import_module("streamlit_helpers"))
    import networkx as nx

    g = nx.DiGraph()
    g.add_edge("a", "b", weight=1.0)

    buf = helpers.graph_to_graphml_buffer(g)
    assert b"<graphml" in buf.getvalue()


def test_figure_to_png_buffer():
    helpers = importlib.reload(importlib.import_module("streamlit_helpers"))

    class DummyFig:
        def write_image(self, fh, format="png"):
            fh.write(b"img")

    buf = helpers.figure_to_png_buffer(DummyFig())
    assert buf.getvalue() == b"img"
