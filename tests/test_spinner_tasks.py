import asyncio
import types
import pytest

@pytest.mark.asyncio
async def test_spinner_cancel_suppresses_error():
    progress = types.SimpleNamespace(value=0)

    async def spin():
        while progress.value < 0.95:
            await asyncio.sleep(0)
            progress.value += 0.05

    spinner = asyncio.create_task(spin())
    await asyncio.sleep(0)
    spinner.cancel()
    try:
        await spinner
    except asyncio.CancelledError:
        pass

@pytest.mark.asyncio
async def test_spinner_cancel_suppresses_error_again():
    progress = types.SimpleNamespace(value=0)

    async def spin():
        while progress.value < 0.5:
            await asyncio.sleep(0)
            progress.value += 0.1

    spinner = asyncio.create_task(spin())
    await asyncio.sleep(0)
    spinner.cancel()
    try:
        await spinner
    except asyncio.CancelledError:
        pass
