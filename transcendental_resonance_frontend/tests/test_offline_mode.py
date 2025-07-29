import inspect
from utils import api
from pages.debug_panel_page import debug_panel_page


def test_offline_mode_constant_exists():
    assert isinstance(api.OFFLINE_MODE, bool)


def test_debug_panel_mentions_offline():
    source = inspect.getsource(debug_panel_page)
    assert "Offline Mode" in source
