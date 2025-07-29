import asyncio
from video_client import generate_video_preview
from quantum_futures import DISCLAIMER


async def run():
    return await generate_video_preview('hello world', offline=True)


def test_generate_video_preview_offline_deterministic():
    prev1 = asyncio.run(run())
    prev2 = asyncio.run(run())
    assert prev1 == prev2
    assert prev1['disclaimer'] == DISCLAIMER
