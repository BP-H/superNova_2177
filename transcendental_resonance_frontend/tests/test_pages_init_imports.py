import inspect

from pages import register_page, network_page


def test_register_page_importable():
    assert inspect.iscoroutinefunction(register_page)


def test_network_page_importable():
    assert inspect.iscoroutinefunction(network_page)
