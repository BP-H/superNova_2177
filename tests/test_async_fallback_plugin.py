import asyncio
import sys
import importlib

async def test_async_fallback_plugin(tmp_path, monkeypatch):
    """Async test should run even when pytest_asyncio is absent."""
    # Simulate missing pytest_asyncio
    monkeypatch.delitem(sys.modules, "pytest_asyncio", raising=False)

    # Ensure fallback plugin is reloaded in case it relied on the module
    import tests.async_fallback as fallback
    importlib.reload(fallback)

    file = tmp_path / "example.txt"
    file.write_text("hello")
    await asyncio.sleep(0)
    assert file.read_text() == "hello"
