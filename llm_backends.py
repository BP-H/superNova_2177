from typing import Callable, Dict, Optional


def dummy_backend(prompt: str) -> str:
    """Return a canned response for testing."""
    return "[dummy]" + prompt


BACKENDS: Dict[str, Callable[[str], str]] = {
    "dummy": dummy_backend,
}


def get_backend(name: str) -> Optional[Callable[[str], str]]:
    """Retrieve the backend callable by name."""
    return BACKENDS.get(name)
