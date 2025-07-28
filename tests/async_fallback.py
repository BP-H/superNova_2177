import asyncio
import inspect
import importlib.util
import pytest


_has_pytest_asyncio = importlib.util.find_spec("pytest_asyncio") is not None

if not _has_pytest_asyncio:
    @pytest.hookimpl(tryfirst=True)
    def pytest_pyfunc_call(pyfuncitem):
        testfunc = pyfuncitem.obj
        if inspect.iscoroutinefunction(testfunc):
            asyncio.run(testfunc(**pyfuncitem.funcargs))
            return True
