import asyncio
import inspect
import types
import sys
import importlib

import pytest

# Dummy NiceGUI components for testing
class DummyElement:
    def __init__(self):
        self.value = ""
        self.open = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        pass

    def __getattr__(self, name):
        def method(*_a, **_kw):
            return self
        return method

class DummyUI:
    def __init__(self):
        self.notifications = []
        self.callbacks = []
        self.inputs = []
        self.textareas = []

    def page(self, _path):
        def decorator(func):
            return func
        return decorator

    def column(self, *a, **k):
        return DummyElement()

    def row(self, *a, **k):
        return DummyElement()

    def card(self, *a, **k):
        return DummyElement()

    def dialog(self, *a, **k):
        return DummyElement()

    def label(self, *a, **k):
        return DummyElement()

    def input(self, *a, **k):
        elem = DummyElement()
        self.inputs.append(elem)
        return elem

    def textarea(self, *a, **k):
        elem = DummyElement()
        self.textareas.append(elem)
        return elem

    def select(self, *a, **k):
        return DummyElement()

    def switch(self, *a, **k):
        return DummyElement()

    def button(self, *args, on_click=None, **kwargs):
        label = args[0] if args else kwargs.get("icon")
        self.callbacks.append((label, on_click))
        return DummyElement()

    def expansion(self, *a, **k):
        return DummyElement()

    def markdown(self, *a, **k):
        return DummyElement()

    def link(self, *a, **k):
        return DummyElement()

    def timer(self, *a, **k):
        return DummyElement()

    def html(self, *a, **k):
        return DummyElement()

    def image(self, *a, **k):
        return DummyElement()

    def video(self, *a, **k):
        return DummyElement()

    def audio(self, *a, **k):
        return DummyElement()

    def skeleton(self, *a, **k):
        return DummyElement()

    def notify(self, message, **kwargs):
        self.notifications.append(message)

    def open(self, *a, **k):
        pass

    def run_async(self, coro):
        if inspect.iscoroutine(coro):
            asyncio.create_task(coro)


def setup_dummy_ui(monkeypatch):
    dummy_ui = DummyUI()
    module = types.ModuleType("nicegui")
    module.ui = dummy_ui
    element_module = types.ModuleType("nicegui.element")
    element_module.Element = DummyElement
    monkeypatch.setitem(sys.modules, "nicegui", module)
    monkeypatch.setitem(sys.modules, "nicegui.element", element_module)
    # Reload modules that may have imported NiceGUI before patching
    for mod_name in ("utils.layout", "utils.features"):
        if mod_name in sys.modules:
            importlib.reload(sys.modules[mod_name])
    return dummy_ui


@pytest.mark.asyncio
async def test_offline_client(monkeypatch):
    monkeypatch.setenv("OFFLINE_MODE", "1")
    from external_services.llm_client import LLMClient
    client = LLMClient(api_url="http://x", api_key="y")
    assert client.offline


@pytest.mark.asyncio
async def test_login_failed_notification(monkeypatch):
    dummy = setup_dummy_ui(monkeypatch)
    import pages.login_page as lp
    importlib.reload(lp)

    async def fake_call(*_a, **_kw):
        return None

    monkeypatch.setattr(lp, "api_call", fake_call)
    monkeypatch.setattr(lp, "set_token", lambda *_: None)

    await lp.login_page()
    # first button is the login button
    handle_login = dummy.callbacks[0][1]
    dummy.inputs[0].value = "user"
    dummy.inputs[1].value = "pass"
    await handle_login()
    assert any("login failed" in n.lower() for n in dummy.notifications)


@pytest.mark.asyncio
async def test_feed_post_failure_notification(monkeypatch):
    dummy = setup_dummy_ui(monkeypatch)
    import pages.feed_page as fp
    importlib.reload(fp)

    async def fake_call(method, endpoint, *_a, **_kw):
        if method == "POST":
            return None
        return []

    monkeypatch.setattr(fp, "api_call", fake_call)
    monkeypatch.setattr(fp, "generate_speculative_futures", lambda *_a, **_kw: [])
    monkeypatch.setattr(fp, "TOKEN", "token")

    await fp.feed_page()
    callback = None
    for label, cb in dummy.callbacks:
        if label == "Post" and cb is not None:
            callback = cb
    assert callback is not None
    dummy.textareas[0].value = "hi"
    await callback()
    assert any("failed to post" in n.lower() for n in dummy.notifications)
