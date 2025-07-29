# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
import types
from utils import styles

def dummy_ui(captured):
    return types.SimpleNamespace(
        add_head_html=lambda html: captured.setdefault("html", html),
        run_javascript=lambda *_args, **_kwargs: None,
    )


def test_set_theme_switches(monkeypatch):
    dummy = dummy_ui({})
    monkeypatch.setattr(styles, "ui", dummy)
    styles.set_theme("light")
    assert styles.get_theme_name() == "light"
    styles.set_theme("dark")
    assert styles.get_theme_name() == "dark"


def test_apply_global_styles_injects_css(monkeypatch):
    captured = {}
    dummy = dummy_ui(captured)
    monkeypatch.setattr(styles, "ui", dummy)
    styles.apply_global_styles()
    assert "global-theme" in captured["html"]


def test_set_accent_overrides_default(monkeypatch):
    captured = {}
    dummy = dummy_ui(captured)
    monkeypatch.setattr(styles, "ui", dummy)
    styles.set_theme("dark")
    styles.set_accent("#123456")
    assert styles.get_theme()["accent"] == "#123456"
