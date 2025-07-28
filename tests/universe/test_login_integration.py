import superNova_2177 as sn
import httpx
import pytest
import pytest_asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker



@pytest_asyncio.fixture
async def client(monkeypatch, tmp_path):
    db_url = f"sqlite:///{tmp_path}/login.db"
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    sn.Base.metadata.create_all(bind=engine)
    monkeypatch.setattr(sn, "SessionLocal", SessionLocal)

    # Inject universe_id into the stub app
    sn.UNIVERSE_ID = "test-universe"

    @sn.app.get("/universe/info")
    async def universe_info():
        return {"universe_id": sn.UNIVERSE_ID}

    transport = httpx.ASGITransport(app=sn.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


async def _register(client, username):
    await client.post(
        "/users/register",
        json={"username": username, "email": f"{username}@e.com", "password": "p"},
    )


async def _login(client, username):
    return await client.post("/token", data={"username": username, "password": "p"})


@pytest.mark.asyncio
async def test_login_universe_id_propagation(client):
    await _register(client, "u1")
    token_resp = await _login(client, "u1")
    assert token_resp.status_code == 200
    info = await client.get("/universe/info")
    assert info.status_code == 200
    assert info.json()["universe_id"] == "test-universe"
