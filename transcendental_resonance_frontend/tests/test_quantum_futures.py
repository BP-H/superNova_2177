import inspect
import pytest
from quantum_futures import generate_speculative_futures, DISCLAIMER


@pytest.mark.asyncio
async def test_generate_speculative_futures_length():
    futures = await generate_speculative_futures({'description': 'test'}, num_variants=2)
    assert isinstance(futures, list)
    assert len(futures) == 2


def test_disclaimer_constant():
    assert isinstance(DISCLAIMER, str)
    assert 'satirical simulation' in DISCLAIMER
