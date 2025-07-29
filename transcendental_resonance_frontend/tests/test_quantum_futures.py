import inspect
from quantum_futures import (
    generate_speculative_futures,
    generate_speculative_payload,
    DISCLAIMER,
)


def test_generate_speculative_futures_length():
    futures = generate_speculative_futures({'description': 'test'}, num_variants=2)
    assert isinstance(futures, list)
    assert len(futures) == 2


def test_disclaimer_constant():
    assert isinstance(DISCLAIMER, str)
    assert 'satirical simulation' in DISCLAIMER


def test_generate_speculative_payload_includes_disclaimer():
    payload = generate_speculative_payload({'description': 'demo'}, num_variants=1)
    assert payload[0]['disclaimer'] == DISCLAIMER
