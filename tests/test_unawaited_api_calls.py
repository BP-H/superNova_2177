from pathlib import Path

from tests.unawaited_helper import find_unawaited_api_calls

PAGES = [
    "transcendental_resonance_frontend/src/pages/feed_page.py",
    "transcendental_resonance_frontend/src/pages/messages_page.py",
    "transcendental_resonance_frontend/src/pages/profile_page.py",
]


def test_no_unawaited_api_calls():
    for page in PAGES:
        source = Path(page).read_text()
        lines = find_unawaited_api_calls(source)
        assert not lines, f"Unawaited api_call on lines {lines} in {page}"
