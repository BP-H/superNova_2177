import json
import pytest

from frontend_bridge import dispatch_route
import virtual_diary.ui_hook as diary_ui_hook


class DummyHookManager:
    def __init__(self):
        self.events = []

    async def trigger(self, name, *args, **kwargs):
        self.events.append((name, args, kwargs))


@pytest.mark.asyncio
async def test_fetch_entries_via_router(monkeypatch, tmp_path):
    dummy = DummyHookManager()
    monkeypatch.setattr("virtual_diary.ui_hook.ui_hook_manager", dummy, raising=False)

    path = tmp_path / "vd.json"
    entries = [{"note": "a"}, {"note": "b"}, {"note": "c"}]
    path.write_text(json.dumps(entries))
    monkeypatch.setenv("VIRTUAL_DIARY_FILE", str(path))

    result = await dispatch_route("fetch_diary_entries", {"limit": 2})

    assert result == {"entries": entries[-2:]}
    assert dummy.events == [("diary_entries_fetched", (entries[-2:],), {})]


@pytest.mark.asyncio
async def test_add_entry_via_router(monkeypatch, tmp_path):
    dummy = DummyHookManager()
    monkeypatch.setattr("virtual_diary.ui_hook.ui_hook_manager", dummy, raising=False)

    path = tmp_path / "vd.json"
    path.write_text("[]")
    monkeypatch.setenv("VIRTUAL_DIARY_FILE", str(path))

    entry = {"note": "hello"}
    result = await dispatch_route("add_diary_entry", {"entry": entry})

    assert result == {"status": "added"}
    data = json.loads(path.read_text())
    assert data == [entry]
    assert dummy.events == [("diary_entry_added", (entry,), {})]
