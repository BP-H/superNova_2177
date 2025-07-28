import asyncio
import inspect
import importlib.util
import pytest


class _AsyncioFallback:
    """Minimal async runner used when ``pytest_asyncio`` isn't installed."""

    @pytest.hookimpl(tryfirst=True)
    def pytest_pyfunc_call(self, pyfuncitem):
        testfunc = pyfuncitem.obj
        if inspect.iscoroutinefunction(testfunc):
            sig = inspect.signature(testfunc)
            kwargs = {name: pyfuncitem.funcargs[name] for name in sig.parameters}
            asyncio.run(testfunc(**kwargs))
            return True


def pytest_configure(config):
    """Register async fallback if ``pytest_asyncio`` isn't available."""

    if importlib.util.find_spec("pytest_asyncio") is not None or config.pluginmanager.hasplugin(
        "pytest_asyncio"
    ):
        return

    config.pluginmanager.register(_AsyncioFallback(), name="asyncio-fallback")
