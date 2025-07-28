import pytest

from frontend_bridge import dispatch_route
from audit import explainer_ui_hook


@pytest.mark.asyncio
async def test_explain_audit_via_router():
    events = []

    async def listener(data):
        events.append(data)

    explainer_ui_hook.ui_hook_manager.register_hook("audit_explained", listener)

    payload = {"trace": {"path_nodes": ["A", "B"], "highlights": ["B"]}}

    result = await dispatch_route("explain_audit", payload)

    expected = "This trace follows the causal chain: A \u2192 B. Notable nodes: B."
    assert result == expected
    assert events == [expected]
