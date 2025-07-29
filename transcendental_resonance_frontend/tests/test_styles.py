import types
from utils import styles


def dummy_ui(captured):
    return types.SimpleNamespace(
        add_head_html=lambda html: captured.setdefault("html", html),
        run_javascript=lambda *_args, **_kwargs: None,
    )


def dummy_ui_dom(captured):
    def add_head_html(html: str) -> None:
        captured.setdefault("htmls", []).append(html)

    def run_javascript(script: str, *args, **kwargs) -> None:
        if "global-theme" in script:
            captured["htmls"] = [
                h for h in captured.get("htmls", []) if "id=\"global-theme\"" not in h
            ]

    return types.SimpleNamespace(add_head_html=add_head_html, run_javascript=run_javascript)


def test_set_theme_switches(monkeypatch):
    dummy = dummy_ui({})
    monkeypatch.setattr(styles, "ui", dummy)
    styles.set_theme("light")
    assert styles.get_theme_name() == "light"
    styles.set_theme("dark")
    assert styles.get_theme_name() == "dark"


def test_minimalist_dark_theme(monkeypatch):
    dummy = dummy_ui({})
    monkeypatch.setattr(styles, "ui", dummy)
    styles.set_theme("minimalist_dark")
    assert styles.get_theme_name() == "minimalist_dark"
    assert styles.get_theme()["text"] == "#F0F0F0"


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

def test_toggle_high_contrast(monkeypatch):
    dummy = dummy_ui({})
    monkeypatch.setattr(styles, "ui", dummy)
    styles.set_theme("dark")
    styles.toggle_high_contrast(True)
    assert styles.get_theme_name() == "high_contrast"
    styles.toggle_high_contrast(False)
    assert styles.get_theme_name() == "dark"


def test_glow_card_css(monkeypatch):
    captured = {}
    dummy = dummy_ui(captured)
    monkeypatch.setattr(styles, "ui", dummy)
    styles.apply_global_styles()
    assert ".glow-card" in captured["html"]


def test_apply_global_styles_removes_old(monkeypatch):
    captured = {}
    dummy = dummy_ui_dom(captured)
    monkeypatch.setattr(styles, "ui", dummy)
    styles.apply_global_styles()
    styles.apply_global_styles()
    style_tags = [h for h in captured.get("htmls", []) if "id=\"global-theme\"" in h]
    assert len(style_tags) == 1


def test_minimalist_dark_theme(monkeypatch):
    captured = {}
    dummy = dummy_ui(captured)
    monkeypatch.setattr(styles, "ui", dummy)
    styles.set_theme("minimalist_dark")
    assert styles.get_theme_name() == "minimalist_dark"
    assert "Iosevka" in captured["html"]
    assert "#181818" in captured["html"]
