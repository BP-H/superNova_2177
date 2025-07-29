# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
import inspect
from pages.network_analysis_page import network_page

def test_network_page_is_async():
    assert inspect.iscoroutinefunction(network_page)
