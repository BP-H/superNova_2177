# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
import inspect
from pages.music_page import music_page


def test_music_page_is_async():
    assert inspect.iscoroutinefunction(music_page)
