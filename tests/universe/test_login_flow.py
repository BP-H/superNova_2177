# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
from types import SimpleNamespace
import sys
import types

fastapi_mod = sys.modules.get("fastapi")
if not fastapi_mod:
    fastapi_mod = types.ModuleType("fastapi")
    sys.modules["fastapi"] = fastapi_mod
if not hasattr(fastapi_mod, "APIRouter"):
    fastapi_mod.APIRouter = type(
        "APIRouter",
        (),
        {"post": lambda *a, **kw: (lambda f: f)},
    )
if not hasattr(fastapi_mod, "Depends"):
    fastapi_mod.Depends = lambda x=None: None
if not hasattr(fastapi_mod, "HTTPException"):
    fastapi_mod.HTTPException = type("HTTPException", (), {})
if not hasattr(fastapi_mod, "status"):
    fastapi_mod.status = types.SimpleNamespace(HTTP_401_UNAUTHORIZED=401)

sec = sys.modules.get("fastapi.security")
if not sec:
    sec = types.ModuleType("fastapi.security")
    sys.modules["fastapi.security"] = sec
if not hasattr(sec, "OAuth2PasswordRequestForm"):
    sec.OAuth2PasswordRequestForm = object

import db_models

sn = sys.modules.get("superNova_2177")
if sn is None:
    sn = types.ModuleType("superNova_2177")
    sys.modules["superNova_2177"] = sn

sn.Harmonizer = db_models.Harmonizer
sn.verify_password = lambda p, h: p == h
sn.create_access_token = lambda data: "tok"
sn.get_db = lambda: None
sn.InvalidConsentError = type("InvalidConsentError", (), {})
sn.Token = dict
sn.get_password_hash = lambda p: p

import login_router
from superNova_2177 import get_password_hash


class DummyUser:
    def __init__(self, username="user", password="pass"):
        self.id = 1
        self.username = username
        self.hashed_password = get_password_hash(password)
        self.email = "u@example.com"
        self.species = "human"
        self.is_active = True
        self.consent_given = True
        self.engagement_streaks = {}


class DummyQuery:
    def __init__(self, user):
        self.user = user

    def filter(self, *_args, **_kw):
        return self

    def first(self):
        return self.user


class DummySession:
    def __init__(self, user):
        self.user = user
        self.committed = False

    def query(self, _model):
        return DummyQuery(self.user)

    def commit(self):
        self.committed = True


def test_login_returns_universe_id(monkeypatch):
    user = DummyUser()
    db = DummySession(user)

    monkeypatch.setattr(login_router.UniverseManager, "initialize_for_entity", lambda *_: "U1")

    captured = {}

    def fake_token(data):
        captured["data"] = data
        return "tok"

    monkeypatch.setattr(login_router, "create_access_token", fake_token)

    form = SimpleNamespace(username="user", password="pass")
    result = login_router.login_for_access_token(form, db)

    assert result["universe_id"] == "U1"
    assert result["access_token"] == "tok"
    assert captured["data"]["universe_id"] == "U1"
