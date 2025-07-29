# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
import inspect
from pages.status_page import status_page

def test_status_page_is_async():
    assert inspect.iscoroutinefunction(status_page)
