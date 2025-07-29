import asyncio
import importlib
import sys
import types


def load_app(monkeypatch):
    """Reload ``ui`` with a stubbed ``streamlit`` module."""
    stub = types.ModuleType("streamlit")
    # provide minimal attributes used in ``ui``
    monkeypatch.setitem(sys.modules, "streamlit", stub)
    if "ui" in sys.modules:
        del sys.modules["ui"]
    return importlib.import_module("ui")


async def sample():
    return "done"


def test_run_async_without_running_loop(monkeypatch):
    app = load_app(monkeypatch)
    calls = {}

    def fake_run(coro):
        calls["coro"] = coro
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    monkeypatch.setattr(
        app.asyncio, "get_running_loop", lambda: (_ for _ in ()).throw(RuntimeError())
    )
    monkeypatch.setattr(app.asyncio, "run", fake_run)

    result = app._run_async(sample())
    assert result == "done"
    assert calls["coro"].__class__.__name__ == "coroutine"


def test_run_async_with_running_loop(monkeypatch):
    app = load_app(monkeypatch)

    class DummyLoop:
        def __init__(self):
            self.coro = None

        def is_running(self):
            return True

        def run_until_complete(self, coro):
            self.coro = coro
            loop = asyncio.new_event_loop()
            try:
                return loop.run_until_complete(coro)
            finally:
                loop.close()

    loop = DummyLoop()
    fut_obj = types.SimpleNamespace()

    def fake_run_coroutine_threadsafe(coro, loop_obj):
        assert loop_obj is loop
        loop.coro = coro
        fut_obj.result = lambda: loop.run_until_complete(coro)
        return fut_obj

    monkeypatch.setattr(app.asyncio, "get_running_loop", lambda: loop)
    monkeypatch.setattr(
        app.asyncio, "run_coroutine_threadsafe", fake_run_coroutine_threadsafe
    )

    result = app._run_async(sample())
    assert result == "done"
    assert loop.coro.__class__.__name__ == "coroutine"
