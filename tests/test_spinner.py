import asyncio
import contextlib
import pytest

@pytest.mark.asyncio
async def test_cancelled_spinner_suppressed():
    async def spin():
        while True:
            await asyncio.sleep(0.01)

    spinner = asyncio.create_task(spin())
    spinner.cancel()
    with pytest.raises(asyncio.CancelledError):
        await spinner

    spinner = asyncio.create_task(spin())
    spinner.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await spinner
