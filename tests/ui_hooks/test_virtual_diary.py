# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
import pytest

from frontend_bridge import dispatch_route
import virtual_diary.ui_hook as diary_hook


class DummyManager:
    def __init__(self):
        self.events = []

    async def trigger(self, name, *args, **kwargs):
        self.events.append((name, args, kwargs))


@pytest.mark.asyncio
async def test_load_diary_entries_route(monkeypatch):
    dummy = DummyManager()
    monkeypatch.setattr(diary_hook, "ui_hook_manager", dummy, raising=False)
    monkeypatch.setattr(diary_hook, "load_entries", lambda limit=20: [
        {"note": "hello"}
    ])

    result = await dispatch_route("load_diary_entries", {"limit": 5})

    assert result == {"entries": [{"note": "hello"}]}
    assert dummy.events == [("diary_entries_loaded", ([{"note": "hello"}],), {})]
