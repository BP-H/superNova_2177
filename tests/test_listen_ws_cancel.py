import asyncio
import pytest

import utils.api as api
import transcendental_resonance_frontend.src.utils.api as tr_api

class DummyWS:
    def __init__(self):
        self.closed = False
    def __aiter__(self):
        return self
    async def __anext__(self):
        await asyncio.sleep(0)
        return '{}'
    async def close(self):
        self.closed = True

@pytest.mark.asyncio
async def test_listen_ws_stops_on_cancel(monkeypatch):
    ws = DummyWS()
    async def fake_connect_ws(*_a, **_kw):
        return ws
    monkeypatch.setattr(tr_api, 'connect_ws', fake_connect_ws)
    api.WS_CONNECTION = None
    tr_api.WS_CONNECTION = None
    events = []

    async def handle(event):
        events.append(event)

    task = api.listen_ws(handle, reconnect=False)
    await asyncio.sleep(0.01)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert ws.closed
