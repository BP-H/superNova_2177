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


def test_apply_theme_injects_unique_css(monkeypatch):
    stub = types.ModuleType("streamlit")
    captured = []

    def markdown(text, **_kwargs):
        captured.append(text)

    stub.markdown = markdown
    stub.text_util = types.ModuleType("streamlit.text_util")

    monkeypatch.setitem(sys.modules, "streamlit", stub)
    monkeypatch.setitem(sys.modules, "streamlit.text_util", stub.text_util)

    helpers = importlib.reload(importlib.import_module("streamlit_helpers"))

    themes = ["light", "dark", "modern", "minimalist_dark"]
    css_blocks = {}
    for theme in themes:
        captured.clear()
        helpers.apply_theme(theme)
        assert captured, f"No CSS injected for {theme}"
        css_blocks[theme] = captured[0]

    assert len(set(css_blocks.values())) == len(themes)
