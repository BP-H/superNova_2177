# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
"""Offline mode behavior for utils.api"""

import importlib

import pytest


@pytest.mark.asyncio
async def test_api_call_offline(monkeypatch):
    monkeypatch.setenv("OFFLINE_MODE", "1")
    import utils.api as api

    importlib.reload(api)
    result = await api.api_call("GET", "/status")
    assert result is None  # nosec B101


@pytest.mark.asyncio
async def test_websocket_offline(monkeypatch):
    monkeypatch.setenv("OFFLINE_MODE", "1")
    import utils.api as api

    importlib.reload(api)

    called = []

    async def handler(event):
        called.append(event)

    ws = await api.connect_ws()
    assert ws is None  # nosec B101

    await api.listen_ws(handler, reconnect=False)
    assert called == []  # nosec B101
