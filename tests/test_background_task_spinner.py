import asyncio
import contextlib
import pytest

# nicegui may be a stub without background_tasks in tests
import nicegui

class DummyBG:
    def create(self, coro, name=None):
        return asyncio.create_task(coro)

@pytest.mark.asyncio
async def test_spinner_task_completes_without_warning(recwarn):
    nicegui.background_tasks = DummyBG()
    progress = 0.0

    async def spin():
        nonlocal progress
        while progress < 0.2:
            await asyncio.sleep(0)
            progress += 0.1

    task = nicegui.background_tasks.create(spin(), name='test')
    try:
        await asyncio.sleep(0.01)
    finally:
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task
    assert not recwarn.list
