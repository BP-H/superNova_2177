import frontend_bridge  # noqa: F401 - ensure routes are loaded
from tank_registry import registry


def test_no_duplicate_routes():
    routes = registry.list_routes()
    assert len(routes) == len(set(routes))


def test_routes_callable():
    for name in registry.list_routes():
        handler = registry.routes[name]
        assert callable(handler)
