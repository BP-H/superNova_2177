import asyncio
import logging
import pytest

from hook_manager import HookManager


@pytest.mark.asyncio
async def test_hook_manager_basic_async_and_sync():
    hm = HookManager()
    results = []

    def sync_hook(x):
        results.append(x + 1)
        return x + 1

    async def async_hook(x):
        await asyncio.sleep(0)
        results.append(x + 2)
        return x + 2

    hm.register_hook("event", sync_hook)
    hm.register_hook("event", async_hook)

    out = await hm.trigger("event", 1)
    assert results == [2, 3]
    assert out == [2, 3]


def test_dump_hooks():
    hm = HookManager()
    hm.register_hook("alpha", lambda: None)
    dump = hm.dump_hooks()
    assert "alpha" in dump
    assert dump["alpha"]
