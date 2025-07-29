from utils.quantum_futures import generate_quantum_futures, QuantumFuture, EMOJI_GLOSSARY


def test_generate_quantum_futures_count():
    futures = generate_quantum_futures("test", n=2)
    assert len(futures) == 2
    assert all(isinstance(f, QuantumFuture) for f in futures)


def test_emoji_glossary_non_empty():
    assert isinstance(EMOJI_GLOSSARY, dict)
    assert EMOJI_GLOSSARY
