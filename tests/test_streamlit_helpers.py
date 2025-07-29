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


def test_apply_codex_theme_injects_css(monkeypatch):
    stub = types.ModuleType("streamlit")
    captured = []

    def markdown(text, **kwargs):
        captured.append(text)

    stub.markdown = markdown
    monkeypatch.setitem(sys.modules, "streamlit", stub)

    helpers = importlib.reload(importlib.import_module("streamlit_helpers"))
    helpers.apply_theme("codex")
    assert any("Iosevka" in css for css in captured)
    assert any("294e80" in css for css in captured)


def test_theme_selector_lists_codex(monkeypatch):
    stub = types.ModuleType("streamlit")
    captured_options = {}

    def radio(label, options, **kwargs):
        captured_options["options"] = options
        return "Codex"

    stub.radio = radio
    stub.markdown = lambda *a, **k: None
    stub.session_state = {}

    monkeypatch.setitem(sys.modules, "streamlit", stub)

    helpers = importlib.reload(importlib.import_module("streamlit_helpers"))
    theme = helpers.theme_selector("Theme")
    assert "Codex" in captured_options["options"]
    assert theme == "codex"
