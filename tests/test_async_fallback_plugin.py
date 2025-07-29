# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
import asyncio
import sys
import importlib

# Simulate ``pytest_asyncio`` being unavailable before the test runs so the
# fallback plugin activates during collection.  This must happen at module load
# time to ensure the plugin's hook is registered prior to executing any async
# tests.
sys.modules.pop("pytest_asyncio", None)

# Import and reload the fallback plugin after removing ``pytest_asyncio`` so the
# plugin sees it is missing and registers the appropriate hooks.
import tests.async_fallback as fallback
importlib.reload(fallback)

async def test_async_fallback_plugin(tmp_path, monkeypatch):
    """Async test should run even when pytest_asyncio is absent."""
    # The fallback plugin has already been loaded at module import time with
    # ``pytest_asyncio`` removed.  The test simply exercises async behavior to
    # confirm the plugin runs the coroutine under ``asyncio``.

    file = tmp_path / "example.txt"
    file.write_text("hello")
    await asyncio.sleep(0)
    assert file.read_text() == "hello"
