import uuid
from decimal import Decimal

import pytest
import pytest_asyncio
import httpx
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import importlib
import importlib.util
import sys

import superNova_2177 as sn

# Reload the real module if a lightweight stub was installed by conftest
if (
    getattr(sn, "__file__", "") in (None, "superNova_2177_stub")
    or str(getattr(sn, "__file__", "")).endswith("_stub")
) and importlib.util.find_spec("fastapi") is not None:
    for mod in list(sys.modules):
        if mod.startswith("fastapi") or mod.startswith("pydantic") or mod.startswith("sqlalchemy"):
            sys.modules.pop(mod, None)
    sys.modules.pop("superNova_2177", None)
    sn = importlib.import_module("superNova_2177")


@pytest.fixture
def test_db(tmp_path, monkeypatch):
    test_url = f"sqlite:///{tmp_path}/test.db"
    engine = create_engine(test_url, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    if TestingSessionLocal is None:
        pytest.skip("SQLAlchemy not available")
    sn.Base.metadata.create_all(bind=engine)
    monkeypatch.setattr(sn, "SessionLocal", TestingSessionLocal)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
    engine.dispose()


@pytest_asyncio.fixture
async def client(test_db):
    transport = httpx.ASGITransport(app=sn.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture
def memory_agent(monkeypatch):
    monkeypatch.setattr(sn, "USE_IN_MEMORY_STORAGE", True)
    agent = sn.RemixAgent(
        cosmic_nexus=sn.CosmicNexus(sn.SessionLocal, sn.SystemStateService(sn.SessionLocal()))
    )
    return agent


async def register(client, username, email, password="password123"):
    return await client.post(
        "/users/register",
        json={"username": username, "email": email, "password": password},
    )


async def login(client, username, password="password123"):
    return await client.post(
        "/token", data={"username": username, "password": password}
    )


async def register_and_get_token(client, username, email=None, password="password123"):
    """Register ``username`` and return an access token for authenticated calls."""
    if email is None:
        email = f"{username}@example.com"
    await register(client, username, email, password=password)
    r = await login(client, username, password)
    return r.json()["access_token"]


@pytest.mark.asyncio
async def test_register_success(client):
    r = await register(client, "user1", "u1@example.com")
    assert r.status_code == 201


@pytest.mark.asyncio
async def test_register_duplicate_username(client):
    await register(client, "dup", "d1@example.com")
    r = await register(client, "dup", "d2@example.com")
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    await register(client, "dupemail1", "dup@example.com")
    r = await register(client, "dupemail2", "dup@example.com")
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_login_success(client):
    await register(client, "loginuser", "l@example.com")
    r = await login(client, "loginuser")
    assert r.status_code == 200
    assert "access_token" in r.json()


@pytest.mark.asyncio
async def test_login_bad_password(client):
    await register(client, "badpass", "bp@example.com")
    r = await login(client, "badpass", "wrong")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent(client):
    r = await login(client, "ghost")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_get_me_requires_auth(client):
    r = await client.get("/users/me")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_get_me_success(client):
    token = await register_and_get_token(client, "meuser", "me@example.com")
    r = await client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["username"] == "meuser"


@pytest.mark.asyncio
async def test_status_endpoint(client):
    r = await client.get("/status")
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_network_analysis_requires_auth(client):
    r = await client.get("/network-analysis/")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_network_analysis_success(client):
    token = await register_and_get_token(client, "netuser", "net@example.com")
    r = await client.get(
        "/network-analysis/", headers={"Authorization": f"Bearer {token}"}
    )
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_follow_unfollow(client):
    token = await register_and_get_token(client, "follower", "fol@example.com")
    await register(client, "target", "tar@example.com")
    r = await client.post(
        "/users/target/follow", headers={"Authorization": f"Bearer {token}"}
    )
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_follow_counts(client):
    token = await register_and_get_token(client, "countfollower", "cf@example.com")
    await register(client, "counttarget", "ct@example.com")
    await client.post(
        "/users/counttarget/follow", headers={"Authorization": f"Bearer {token}"}
    )
    r1 = await client.get("/users/counttarget/followers")
    assert r1.status_code == 200
    assert r1.json()["followers"] == 1
    r2 = await client.get("/users/countfollower/following")
    assert r2.status_code == 200
    assert r2.json()["following"] == 1


@pytest.mark.asyncio
async def test_unknown_endpoint(client):
    r = await client.get("/does-not-exist")
    assert r.status_code == 404


def test_mint_success(memory_agent):
    add = sn.AddUserPayload(
        event="ADD_USER",
        user="gen",
        is_genesis=True,
        species="human",
        karma="0",
        join_time=sn.ts(),
        last_active=sn.ts(),
        root_coin_id="",
        coins_owned=[],
        initial_root_value=str(memory_agent.config.ROOT_INITIAL_VALUE),
        consent=True,
        root_coin_value=str(memory_agent.config.ROOT_INITIAL_VALUE),
        genesis_bonus_applied=True,
        nonce=uuid.uuid4().hex,
    )
    memory_agent.process_event(add)
    user = memory_agent.storage.get_user("gen")
    root_coin_id = user["root_coin_id"]
    memory_agent.storage.set_coin(
        root_coin_id,
        {"owner": "gen", "value": str(memory_agent.config.ROOT_INITIAL_VALUE)},
    )
    mint = sn.MintPayload(
        event="MINT",
        user="gen",
        coin_id=uuid.uuid4().hex,
        value="100",
        root_coin_id=root_coin_id,
        references=[],
        improvement="",
        fractional_pct="0.0001",
        ancestors=[],
        timestamp=sn.ts(),
        is_remix=False,
        content="data",
        genesis_creator=None,
        karma_spent="0",
        nonce=uuid.uuid4().hex,
    )
    memory_agent.process_event(mint)
    assert memory_agent.storage.get_coin(mint["coin_id"]) is not None


def test_mint_fails_for_low_karma(memory_agent):
    add = sn.AddUserPayload(
        event="ADD_USER",
        user="nong",
        is_genesis=False,
        species="human",
        karma="0",
        join_time=sn.ts(),
        last_active=sn.ts(),
        root_coin_id="",
        coins_owned=[],
        initial_root_value=str(memory_agent.config.ROOT_INITIAL_VALUE),
        consent=True,
        root_coin_value=str(memory_agent.config.ROOT_INITIAL_VALUE),
        genesis_bonus_applied=False,
        nonce=uuid.uuid4().hex,
    )
    memory_agent.process_event(add)
    user = memory_agent.storage.get_user("nong")
    root_coin_id = user["root_coin_id"]
    mint = sn.MintPayload(
        event="MINT",
        user="nong",
        coin_id=uuid.uuid4().hex,
        value="50",
        root_coin_id=root_coin_id,
        references=[],
        improvement="",
        fractional_pct="0.0001",
        ancestors=[],
        timestamp=sn.ts(),
        is_remix=False,
        content="data",
        genesis_creator=None,
        karma_spent="0",
        nonce=uuid.uuid4().hex,
    )
    memory_agent.process_event(mint)
    assert memory_agent.storage.get_coin(mint["coin_id"]) is None


def test_revoke_consent(memory_agent):
    add = sn.AddUserPayload(
        event="ADD_USER",
        user="rev",
        is_genesis=False,
        species="human",
        karma="0",
        join_time=sn.ts(),
        last_active=sn.ts(),
        root_coin_id="",
        coins_owned=[],
        initial_root_value=str(memory_agent.config.ROOT_INITIAL_VALUE),
        consent=True,
        root_coin_value=str(memory_agent.config.ROOT_INITIAL_VALUE),
        genesis_bonus_applied=False,
        nonce=uuid.uuid4().hex,
    )
    memory_agent.process_event(add)
    revoke = sn.RevokeConsentPayload(
        event="REVOKE_CONSENT", user="rev", nonce=uuid.uuid4().hex
    )
    memory_agent.process_event(revoke)
    user = memory_agent.storage.get_user("rev")
    assert user["consent_given"] is False


def test_buy_coin_success(memory_agent):
    seller = sn.AddUserPayload(
        event="ADD_USER",
        user="sell",
        is_genesis=True,
        species="human",
        karma="0",
        join_time=sn.ts(),
        last_active=sn.ts(),
        root_coin_id="",
        coins_owned=[],
        initial_root_value=str(memory_agent.config.ROOT_INITIAL_VALUE),
        consent=True,
        root_coin_value=str(memory_agent.config.ROOT_INITIAL_VALUE),
        genesis_bonus_applied=True,
        nonce=uuid.uuid4().hex,
    )
    buyer = sn.AddUserPayload(
        event="ADD_USER",
        user="buy",
        is_genesis=False,
        species="human",
        karma="0",
        join_time=sn.ts(),
        last_active=sn.ts(),
        root_coin_id="",
        coins_owned=[],
        initial_root_value=str(memory_agent.config.ROOT_INITIAL_VALUE),
        consent=True,
        root_coin_value=str(memory_agent.config.ROOT_INITIAL_VALUE),
        genesis_bonus_applied=False,
        nonce=uuid.uuid4().hex,
    )
    memory_agent.process_event(seller)
    memory_agent.process_event(buyer)
    seller_data = memory_agent.storage.get_user("sell")
    root_coin_id = seller_data["root_coin_id"]
    mint = sn.MintPayload(
        event="MINT",
        user="sell",
        coin_id=uuid.uuid4().hex,
        value="10",
        root_coin_id=root_coin_id,
        references=[],
        improvement="",
        fractional_pct="0.0001",
        ancestors=[],
        timestamp=sn.ts(),
        is_remix=False,
        content="data",
        genesis_creator=None,
        karma_spent="0",
        nonce=uuid.uuid4().hex,
    )
    memory_agent.process_event(mint)
    list_event = sn.MarketplaceListPayload(
        event="LIST_COIN_FOR_SALE",
        listing_id="l1",
        coin_id=mint["coin_id"],
        seller="sell",
        price="5",
        timestamp=sn.ts(),
        nonce=uuid.uuid4().hex,
    )
    memory_agent.process_event(list_event)
    buy_event = sn.MarketplaceBuyPayload(
        event="BUY_COIN",
        listing_id="l1",
        buyer="buy",
        total_cost="5",
        nonce=uuid.uuid4().hex,
    )
    memory_agent.process_event(buy_event)
    coin = memory_agent.storage.get_coin(mint["coin_id"])
    assert coin["owner"] == "buy"


def test_creator_karma_gain_on_react(memory_agent):
    creator = sn.AddUserPayload(
        event="ADD_USER",
        user="cre",
        is_genesis=False,
        species="human",
        karma="0",
        join_time=sn.ts(),
        last_active=sn.ts(),
        root_coin_id="",
        coins_owned=[],
        initial_root_value=str(memory_agent.config.ROOT_INITIAL_VALUE),
        consent=True,
        root_coin_value=str(memory_agent.config.ROOT_INITIAL_VALUE),
        genesis_bonus_applied=False,
        nonce=uuid.uuid4().hex,
    )
    reactor = sn.AddUserPayload(
        event="ADD_USER",
        user="rct",
        is_genesis=False,
        species="human",
        karma="0",
        join_time=sn.ts(),
        last_active=sn.ts(),
        root_coin_id="",
        coins_owned=[],
        initial_root_value=str(memory_agent.config.ROOT_INITIAL_VALUE),
        consent=True,
        root_coin_value=str(memory_agent.config.ROOT_INITIAL_VALUE),
        genesis_bonus_applied=False,
        nonce=uuid.uuid4().hex,
    )
    memory_agent.process_event(creator)
    memory_agent.process_event(reactor)
    creator_data = memory_agent.storage.get_user("cre")
    root_coin_id = creator_data["root_coin_id"]
    mint = sn.MintPayload(
        event="MINT",
        user="cre",
        coin_id=uuid.uuid4().hex,
        value="10",
        root_coin_id=root_coin_id,
        references=[],
        improvement="",
        fractional_pct="0.0001",
        ancestors=[],
        timestamp=sn.ts(),
        is_remix=False,
        content="data",
        genesis_creator=None,
        karma_spent="0",
        nonce=uuid.uuid4().hex,
    )
    memory_agent.process_event(mint)
    react = sn.ReactPayload(
        event="REACT",
        reactor="rct",
        coin_id=mint["coin_id"],
        emoji="👍",
        message="",
        timestamp=sn.ts(),
        nonce=uuid.uuid4().hex,
    )
    memory_agent.process_event(react)
    updated_creator = memory_agent.storage.get_user("cre")
    assert Decimal(updated_creator["karma"]) > Decimal("0")


@pytest.mark.asyncio
async def test_add_user_atomicity_and_rollback(test_db, monkeypatch):
    def fail_coin(*args, **kwargs):
        raise Exception("fail")

    monkeypatch.setattr(sn.SQLAlchemyStorage, "set_coin", fail_coin)
    event = sn.AddUserPayload(user="rollback_user", is_genesis=False, species="human")
    with pytest.raises(sn.UserCreationError):
        sn.agent._apply_ADD_USER(event)
    assert test_db.query(sn.Harmonizer).filter_by(username="rollback_user").first() is None


def test_entropy_calc(test_db):
    entropy = sn.calculate_content_entropy(test_db)
    assert entropy >= 0.0
