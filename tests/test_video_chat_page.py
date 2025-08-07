import importlib
import sys
import types

import pytest


class DummyCtx:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def classes(self, *args):
        return self

    def style(self, *args):
        return self


class DummyEl(DummyCtx):
    def __init__(self):
        self.value = None

    def on(self, *args, **kwargs):
        pass

    def props(self, *args):
        return self

    def on_click(self, *args, **kwargs):
        pass

    def disable(self):
        pass


class StubUI:
    def __init__(self):
        self.notify_calls = []
        self.button_callbacks = []
        self.last_coro = None

    def page(self, *args, **kwargs):
        def decorator(f):
            return f

        return decorator

    def camera(self):
        return DummyEl()

    def video(self):
        return DummyEl()

    def button(self, label, on_click=None, **kwargs):
        el = DummyEl()

        def _on_click(cb=None, **k):
            self.button_callbacks.append((label, cb))

        el.on_click = _on_click
        if on_click:
            el.on_click(on_click)
        return el

    def run_async(self, coro):
        self.last_coro = coro

    def label(self, *args, **kwargs):
        return DummyEl()

    def notify(self, msg, color=None):
        self.notify_calls.append((msg, color))

    def open(self, *args, **kwargs):
        pass

    def row(self):
        return DummyCtx()

    def column(self):
        return DummyCtx()


@pytest.mark.asyncio
async def test_join_call_notifies(monkeypatch):
    stub_ui = StubUI()
    nicegui_mod = types.ModuleType("nicegui")
    nicegui_mod.ui = stub_ui
    element_mod = types.ModuleType("nicegui.element")
    element_mod.Element = object
    monkeypatch.setitem(sys.modules, "nicegui", nicegui_mod)
    monkeypatch.setitem(sys.modules, "nicegui.element", element_mod)
    monkeypatch.setitem(sys.modules, "httpx", types.ModuleType("httpx"))
    monkeypatch.setitem(sys.modules, "websockets", types.ModuleType("websockets"))

    import importlib

    import transcendental_resonance_frontend.src.utils.layout as layout

    importlib.reload(layout)

    import transcendental_resonance_frontend.src.utils.api as api

    async def bad_listen_ws(handler):
        raise RuntimeError("fail")

    monkeypatch.setattr(api, "listen_ws", bad_listen_ws)
    monkeypatch.setattr(api, "TOKEN", "t", raising=False)

    page = importlib.reload(importlib.import_module("pages.video_chat_page"))

    class DummyErrorOverlay:
        def show(self, *a, **k):
            pass

    monkeypatch.setattr(page, "ErrorOverlay", DummyErrorOverlay)
    monkeypatch.setattr(page, "listen_ws", bad_listen_ws)
    monkeypatch.setattr(page, "TOKEN", "t", raising=False)

    await page.video_chat_page()
    join_cb = [cb for label, cb in stub_ui.button_callbacks if label == "Join Call"][0]
    join_cb()
    try:
        await stub_ui.last_coro
    except RuntimeError:
        pass

    assert ("Unable to join video chat", "negative") in stub_ui.notify_calls
