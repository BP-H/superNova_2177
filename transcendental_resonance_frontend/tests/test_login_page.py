# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
import inspect
from pages.login_page import login_page

def test_login_page_is_async():
    assert inspect.iscoroutinefunction(login_page)
