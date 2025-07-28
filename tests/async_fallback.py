import asyncio
import inspect
import pytest

@pytest.hookimpl(tryfirst=True)
def pytest_pyfunc_call(pyfuncitem):
    testfunc = pyfuncitem.obj
    if inspect.iscoroutinefunction(testfunc):
        asyncio.run(testfunc(**pyfuncitem.funcargs))
        return True
