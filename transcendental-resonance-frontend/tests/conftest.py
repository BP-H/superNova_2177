import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / 'src'
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import types
import pytest


class DummyUI:
    """Lightweight NiceGUI stub used for tests."""

    def __init__(self) -> None:
        self.buttons = []
        self.inputs = []
        self.notifications = []
        self.opened = []
        self.head_html = ""

    # decorator -------------------------------------------------------------
    def page(self, path: str):
        def decorator(func):
            setattr(func, "__nicegui_path__", path)
            return func
        return decorator

    # element stubs --------------------------------------------------------
    context = types.SimpleNamespace(client=types.SimpleNamespace(request=types.SimpleNamespace(headers={"user-agent": "test"})))

    def column(self):
        return self

    def label(self, *args, **kwargs):
        return self

    def input(self, *args, **kwargs):
        obj = types.SimpleNamespace(value="", classes=lambda *_: obj)
        self.inputs.append(obj)
        return obj

    textarea = input
    select = input

    def button(self, *args, on_click=None, **kwargs):
        if on_click:
            self.buttons.append(on_click)
        obj = types.SimpleNamespace(classes=lambda *_: obj, style=lambda *_: obj)
        return obj

    def on_click(self, *_, **__):
        return self

    def classes(self, *_):
        return self

    def style(self, *_):
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        pass

    def open(self, target):
        self.opened.append(target)

    def notify(self, message, color=None):
        self.notifications.append((message, color))

    def timer(self, *_, **__):
        pass

    def html(self, *_, **__):
        pass

    def add_head_html(self, html: str) -> None:
        self.head_html += html


@pytest.fixture(autouse=True)
def stub_nicegui(monkeypatch):
    """Provide a minimal ``nicegui.ui`` stub for page tests."""

    ui_stub = DummyUI()
    nicegui_stub = types.SimpleNamespace(ui=ui_stub)
    monkeypatch.setitem(sys.modules, "nicegui", nicegui_stub)
    # ensure utilities use the stubbed ui
    if "utils.styles" in sys.modules:
        monkeypatch.setattr(sys.modules["utils.styles"], "ui", ui_stub)
    if "utils.api" in sys.modules:
        monkeypatch.setattr(sys.modules["utils.api"], "ui", ui_stub)
    yield ui_stub

