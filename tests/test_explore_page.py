import pytest

from contextlib import contextmanager


class Dummy:
    def __call__(self, *a, **k):
        return self

    def classes(self, *a, **k):
        return self

    def style(self, *a, **k):
        return self

    def on(self, *a, **k):
        return self

    def delete(self):
        pass

    def clear(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        pass


@pytest.mark.asyncio
async def test_explore_page_failure(monkeypatch):
    xp = pytest.importorskip(
        'transcendental_resonance_frontend.src.pages.explore_page'
    )

    monkeypatch.setattr(xp, 'TOKEN', 'tok')
    monkeypatch.setattr(xp, 'login_page', lambda: None)
    monkeypatch.setattr(xp, 'navigation_bar', lambda: None)
    monkeypatch.setattr(xp, 'render_media_block', lambda *a, **k: None)
    monkeypatch.setattr(xp, 'get_theme', lambda: {'accent': '', 'background': ''})

    @contextmanager
    def fake_page_container(theme=None):
        yield Dummy()

    monkeypatch.setattr(xp, 'page_container', fake_page_container)
    monkeypatch.setattr(xp.ui, 'label', lambda *a, **k: Dummy())
    monkeypatch.setattr(xp.ui, 'column', lambda *a, **k: Dummy())
    monkeypatch.setattr(xp.ui, 'card', lambda *a, **k: Dummy())
    monkeypatch.setattr(xp, 'skeleton_loader', lambda *a, **k: Dummy())
    monkeypatch.setattr(xp.ui, 'run_javascript', lambda *a, **k: False)
    monkeypatch.setattr(xp.ui, 'timer', lambda *a, **k: None)
    monkeypatch.setattr(xp.ui, 'open', lambda *a, **k: None)
    monkeypatch.setattr(xp.ui, 'run_async', lambda coro: None)

    notified = {}

    def fake_notify(msg, color=None):
        notified['msg'] = msg
        notified['color'] = color

    monkeypatch.setattr(xp.ui, 'notify', fake_notify)

    async def fake_api(*a, **k):
        raise RuntimeError('boom')

    monkeypatch.setattr(xp, 'api_call', fake_api)

    await xp.explore_page()

    assert notified == {'msg': 'Failed to load posts', 'color': 'negative'}
