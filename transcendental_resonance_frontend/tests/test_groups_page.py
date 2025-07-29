# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
import inspect
from pages.groups_page import groups_page

def test_groups_page_is_async():
    assert inspect.iscoroutinefunction(groups_page)

def test_groups_page_has_search_widgets():
    src = inspect.getsource(groups_page)
    assert "ui.input('Search'" in src
    assert "ui.select(['name', 'date']" in src
