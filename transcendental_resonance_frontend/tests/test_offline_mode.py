import pytest

from utils.api import api_call, connect_ws, listen_ws
from quantum_futures import generate_speculative_payload
from nicegui import ui

@pytest.mark.asyncio
async def test_api_call_offline(monkeypatch):
    monkeypatch.setenv("OFFLINE_MODE", "1")
    monkeypatch.setattr(ui, "notify", lambda *a, **kw: None)
    result = await api_call("GET", "/status", return_error=True)
    assert result is not None
    assert "error" in result

@pytest.mark.asyncio
async def test_websocket_helpers_offline(monkeypatch):
    monkeypatch.setenv("OFFLINE_MODE", "1")
    ws = await connect_ws(timeout=0.1)
    assert ws is None

    received = []
    async def handler(msg):
        received.append(msg)
    await listen_ws(handler, reconnect=False)
    assert received == []

@pytest.mark.asyncio
async def test_generate_speculative_payload_offline(monkeypatch):
    monkeypatch.setenv("OFFLINE_MODE", "1")
    payload = await generate_speculative_payload("offline test")
    assert payload
    first = payload[0]
    assert "Offline Mode" in first["text"]
    assert "placeholder" in first["video_url"]
    assert first["vision_notes"] and "Offline" in first["vision_notes"][0]
