import types
from utils import styles

def test_set_theme_switches(monkeypatch):
    dummy = types.SimpleNamespace(add_head_html=lambda *_: None)
    monkeypatch.setattr(styles, "ui", dummy)
    styles.set_theme("light")
    assert styles.get_theme() is styles.THEMES["light"]
    styles.set_theme("dark")
    assert styles.get_theme() is styles.THEMES["dark"]


def test_apply_global_styles_injects_css(monkeypatch):
    captured = {}
    def add_head_html(html):
        captured["html"] = html
    dummy = types.SimpleNamespace(add_head_html=add_head_html)
    monkeypatch.setattr(styles, "ui", dummy)
    styles.apply_global_styles()
    assert "global-theme" in captured["html"]
