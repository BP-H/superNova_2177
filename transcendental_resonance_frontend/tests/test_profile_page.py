import inspect
from pages.profile_page import profile_page

def test_profile_page_is_async():
    assert inspect.iscoroutinefunction(profile_page)


def test_profile_page_calls_influence_score_api():
    source = inspect.getsource(profile_page)
    assert "/users/me/influence-score" in source
