import inspect
from pages.predictions_page import predictions_page

def test_predictions_page_is_async():
    assert inspect.iscoroutinefunction(predictions_page)
