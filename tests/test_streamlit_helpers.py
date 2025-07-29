import importlib
import sys
import types

# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards


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


def test_apply_theme_minimalist(monkeypatch):
    stub = types.ModuleType("streamlit")

    injected = []

    def markdown(text, **kwargs):
        injected.append(text)

    stub.markdown = markdown

    monkeypatch.setitem(sys.modules, "streamlit", stub)
    helpers = importlib.reload(importlib.import_module("streamlit_helpers"))
    helpers.apply_theme("minimalist_dark")
    assert "app-theme" in injected[0]
