import json
import os
import pytest

from frontend_bridge import dispatch_route
import diary.ui_hook as diary_hook


@pytest.mark.asyncio
async def test_get_diary_entries_dispatch(monkeypatch, tmp_path):
    path = tmp_path / "virtual_diary.json"
    with open(path, "w") as f:
        json.dump([{"note": "a"}, {"note": "b"}], f)

    monkeypatch.setenv("VIRTUAL_DIARY_FILE", str(path))

    result = await dispatch_route("get_diary_entries", {"limit": 1})

    assert result == {"entries": [{"note": "b"}]}


@pytest.mark.asyncio
async def test_get_diary_entries_missing_file(monkeypatch, tmp_path):
    path = tmp_path / "missing.json"
    monkeypatch.setenv("VIRTUAL_DIARY_FILE", str(path))

    result = await dispatch_route("get_diary_entries", {})

    assert result == {"entries": []}
