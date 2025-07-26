import importlib
import pytest

from utils import api
from pages import login_page as login_mod


def reload_login():
    """Reload the login module so patched ``ui`` is applied."""
    importlib.reload(login_mod)

def get_button(ui_stub):
    assert ui_stub.buttons, "no button captured"
    return ui_stub.buttons.pop()


@pytest.mark.asyncio
async def test_login_success(monkeypatch, stub_nicegui):
    monkeypatch.setattr(api, "api_call", lambda *a, **k: {"access_token": "tok"})
    token = {}
    monkeypatch.setattr(api, "set_token", lambda t: token.setdefault("value", t))

    reload_login()
    await login_mod.login_page()
    stub_nicegui.inputs[0].value = "u"
    stub_nicegui.inputs[1].value = "p"
    await get_button(stub_nicegui)()

    assert token.get("value") == "tok"
    assert ("Login successful!", "positive") in stub_nicegui.notifications
    assert stub_nicegui.opened


@pytest.mark.asyncio
async def test_login_error(monkeypatch, stub_nicegui):
    monkeypatch.setattr(api, "api_call", lambda *a, **k: None)
    reload_login()
    await login_mod.login_page()
    stub_nicegui.inputs[0].value = "u"
    stub_nicegui.inputs[1].value = "p"
    await get_button(stub_nicegui)()

    assert ("Login failed", "negative") in stub_nicegui.notifications


@pytest.mark.asyncio
async def test_register_success(monkeypatch, stub_nicegui):
    monkeypatch.setattr(api, "api_call", lambda *a, **k: True)
    reload_login()
    await login_mod.register_page()
    stub_nicegui.inputs[0].value = "u"
    stub_nicegui.inputs[1].value = "e@x"
    stub_nicegui.inputs[2].value = "pass"
    await get_button(stub_nicegui)()

    assert ("Registration successful! Please login.", "positive") in stub_nicegui.notifications


@pytest.mark.asyncio
async def test_register_error(monkeypatch, stub_nicegui):
    monkeypatch.setattr(api, "api_call", lambda *a, **k: None)
    reload_login()
    await login_mod.register_page()
    stub_nicegui.inputs[0].value = "u"
    stub_nicegui.inputs[1].value = "e@x"
    stub_nicegui.inputs[2].value = "pass"
    await get_button(stub_nicegui)()

    assert ("Registration failed", "negative") in stub_nicegui.notifications


