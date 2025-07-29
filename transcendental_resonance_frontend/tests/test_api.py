import inspect
import importlib
import types
import utils.api as api_mod
import pytest

api_call = api_mod.api_call

def test_api_call_is_async():
    assert inspect.iscoroutinefunction(api_call)


@pytest.mark.asyncio
async def test_api_call_offline(monkeypatch):
    monkeypatch.setenv("OFFLINE_MODE", "1")
    api = importlib.reload(api_mod)
    monkeypatch.setattr(api, "ui", types.SimpleNamespace(notify=lambda *a, **kw: None))
    result = await api.api_call("GET", "/test")
    assert result is None
    monkeypatch.setenv("OFFLINE_MODE", "0")
    importlib.reload(api_mod)


@pytest.mark.asyncio
async def test_get_user_recommendations_offline(monkeypatch):
    monkeypatch.setenv("OFFLINE_MODE", "1")
    api = importlib.reload(api_mod)
    monkeypatch.setattr(api, "ui", types.SimpleNamespace(notify=lambda *a, **kw: None))
    result = await api.get_user_recommendations()
    assert result == []
    monkeypatch.setenv("OFFLINE_MODE", "0")
    importlib.reload(api_mod)
