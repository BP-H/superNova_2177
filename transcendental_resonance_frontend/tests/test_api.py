import inspect
from utils.api import api_call

def test_api_call_is_async():
    assert inspect.iscoroutinefunction(api_call)
