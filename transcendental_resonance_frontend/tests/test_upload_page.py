# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
import inspect
from pages.upload_page import upload_page

def test_upload_page_is_async():
    assert inspect.iscoroutinefunction(upload_page)
