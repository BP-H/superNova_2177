import asyncio
from llm_client import get_speculative_futures
from quantum_futures import DISCLAIMER


async def run():
    return await get_speculative_futures({'description': 'x'}, num_variants=2, offline=True)


def test_get_speculative_futures_offline_deterministic():
    fut1 = asyncio.run(run())
    fut2 = asyncio.run(run())
    assert fut1 == fut2
    assert all(f['disclaimer'] == DISCLAIMER for f in fut1)
