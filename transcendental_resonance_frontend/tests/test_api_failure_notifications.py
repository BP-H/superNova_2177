import types
import pytest

import pages.network_analysis_page as network_page
import pages.system_insights_page as system_insights_page
import pages.events_page as events_page
from utils import layout

class DummyElement:
    def __init__(self):
        self.text = ''
        self.value = ''
    def classes(self, *a):
        return self
    def style(self, *a):
        return self
    def on(self, *a, **k):
        return self
    def on_change(self, *a, **k):
        return self
    def clear(self):
        pass
    def set_content(self, _):
        pass

class DummyUI(types.SimpleNamespace):
    def __init__(self):
        super().__init__()
        self.notifications = []
    def notify(self, msg, color=None):
        self.notifications.append((msg, color))
    def label(self, *a, **k):
        return DummyElement()
    def input(self, *a, **k):
        return DummyElement()
    def button(self, *a, **k):
        return DummyElement()
    def html(self, *a, **k):
        return DummyElement()
    def column(self, *a, **k):
        class C(DummyElement):
            def __enter__(self_inner):
                return self_inner
            def __exit__(self_inner, *exc):
                pass
        return C()
    def card(self, *a, **k):
        class C(DummyElement):
            def __enter__(self_inner):
                return self_inner
            def __exit__(self_inner, *exc):
                pass
        return C()
    def select(self, *a, **k):
        return DummyElement()
    def row(self, *a, **k):
        class C(DummyElement):
            def __enter__(self_inner):
                return self_inner
            def __exit__(self_inner, *exc):
                pass
        return C()
    def switch(self, *a, **k):
        return DummyElement()
    def textarea(self, *a, **k):
        return DummyElement()
    def date(self, *a, **k):
        return DummyElement()
    def slider(self, *a, **k):
        return DummyElement()
    def timer(self, *a, **k):
        return DummyElement()
    def open(self, *a, **k):
        pass
    def run_javascript(self, *a, **k):
        pass
    def dialog(self, *a, **k):
        class C(DummyElement):
            def __enter__(self_inner):
                return self_inner
            def __exit__(self_inner, *exc):
                pass
        return C()

def _setup(monkeypatch, module):
    ui = DummyUI()
    monkeypatch.setattr(module, "ui", ui)
    monkeypatch.setattr(layout, "ui", ui)
    monkeypatch.setattr(module, "TOKEN", "x", raising=False)
    async def fake(*args, **kwargs):
        return None
    monkeypatch.setattr(module, "api_call", fake)
    return ui

@pytest.mark.asyncio
async def test_refresh_network_notifies(monkeypatch):
    ui = _setup(monkeypatch, network_page)
    await network_page.network_page()
    assert ("Failed to load data", "negative") in ui.notifications

@pytest.mark.asyncio
async def test_refresh_metrics_notifies(monkeypatch):
    ui = _setup(monkeypatch, system_insights_page)
    await system_insights_page.system_insights_page()
    assert ("Failed to load data", "negative") in ui.notifications

@pytest.mark.asyncio
async def test_refresh_events_notifies(monkeypatch):
    ui = _setup(monkeypatch, events_page)
    await events_page.events_page()
    assert ("Failed to load data", "negative") in ui.notifications
