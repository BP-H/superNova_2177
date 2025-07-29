# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
import inspect
from pages.proposals_page import proposals_page

def test_proposals_page_is_async():
    assert inspect.iscoroutinefunction(proposals_page)
