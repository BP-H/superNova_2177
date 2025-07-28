import sys
from pathlib import Path
import importlib.util

_orig_find_spec = importlib.util.find_spec


def _safe_find_spec(name, package=None):
    try:
        return _orig_find_spec(name, package)
    except ValueError:
        return None

importlib.util.find_spec = _safe_find_spec

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
sys.modules.setdefault("conftest", sys.modules[__name__])

try:
    import db_models  # noqa: F401
except Exception:  # pragma: no cover - handle optional dependency
    pass

# Provide a lightweight stub for the heavy ``superNova_2177`` module so tests do
# not require optional scientific dependencies.
if "superNova_2177" not in sys.modules:
    import types
    from decimal import Decimal

    stub_sn = types.ModuleType("superNova_2177")
    # Mark as a stub so modules can detect and optionally reload the real one if
    # desired. ``__file__`` mimics a module path to signal stubbing.
    stub_sn.__file__ = "superNova_2177_stub"

    class Config:
        """Lightweight stand-in mirroring ``superNova_2177.Config`` attributes."""

        ROOT_INITIAL_VALUE = Decimal("1000000")
        TREASURY_SHARE = Decimal("0.3333")
        REACTOR_SHARE = Decimal("0.3333")
        CREATOR_SHARE = Decimal("0.3334")
        KARMA_MINT_THRESHOLD = Decimal("100")
        MIN_IMPROVEMENT_LEN = 50
        EMOJI_WEIGHTS = {"👍": Decimal("1"), "❤️": Decimal("2")}
        DAILY_DECAY = Decimal("0.99")
        SNAPSHOT_INTERVAL = 100
        MAX_INPUT_LENGTH = 10000
        VAX_PATTERNS = {"block": [r"\b(blocked_word)\b"]}
        VAX_FUZZY_THRESHOLD = 2
        REACTOR_KARMA_PER_REACT = Decimal("1")
        CREATOR_KARMA_PER_REACT = Decimal("2")
        NETWORK_CENTRALITY_BONUS_MULTIPLIER = Decimal("5")
        CREATIVE_LEAP_NOISE_STD = 0.01
        BOOTSTRAP_Z_SCORE = 1.96
        FUZZINESS_RANGE_LOW = 0.1
        FUZZINESS_RANGE_HIGH = 0.4
        INTERFERENCE_FACTOR = 0.01
        DEFAULT_ENTANGLEMENT_FACTOR = 0.5
        CREATE_PROBABILITY_CAP = 0.9
        LIKE_PROBABILITY_CAP = 0.8
        FOLLOW_PROBABILITY_CAP = 0.6
        INFLUENCE_MULTIPLIER = 1.2
        ENTROPY_MULTIPLIER = 0.8
        CONTENT_ENTROPY_WINDOW_HOURS = 24
        NEGENTROPY_SAMPLE_LIMIT = 100
        DISSONANCE_SIMILARITY_THRESHOLD = 0.8
        CREATIVE_LEAP_THRESHOLD = 0.5
        ENTROPY_REDUCTION_STEP = Decimal("0.2")
        VOTING_DEADLINE_HOURS = 72
        CREATIVE_BARRIER_POTENTIAL = Decimal("5000.0")
        SYSTEM_ENTROPY_BASE = 1000.0
        CREATION_COST_BASE = Decimal("1000.0")
        ENTROPY_MODIFIER_SCALE = 2000.0
        ENTROPY_INTERVENTION_THRESHOLD = 1200.0
        ENTROPY_INTERVENTION_STEP = 50.0
        ENTROPY_CHAOS_THRESHOLD = 1500.0
        CROSS_REMIX_CREATOR_SHARE = Decimal("0.34")
        CROSS_REMIX_TREASURY_SHARE = Decimal("0.33")
        CROSS_REMIX_COST = Decimal("10")
        REACTION_ESCROW_RELEASE_FACTOR = Decimal("100")
        PASSIVE_AURA_UPDATE_INTERVAL_SECONDS = 3600
        PROPOSAL_LIFECYCLE_INTERVAL_SECONDS = 300
        NONCE_CLEANUP_INTERVAL_SECONDS = 3600
        NONCE_EXPIRATION_SECONDS = 86400
        CONTENT_ENTROPY_UPDATE_INTERVAL_SECONDS = 600
        NETWORK_CENTRALITY_UPDATE_INTERVAL_SECONDS = 3600
        PROACTIVE_INTERVENTION_INTERVAL_SECONDS = 3600
        AI_PERSONA_EVOLUTION_INTERVAL_SECONDS = 86400
        GUINNESS_PURSUIT_INTERVAL_SECONDS = 86400 * 3
        ANNUAL_AUDIT_INTERVAL_SECONDS = 86400 * 365
        METRICS_PORT = 8001
        INFLUENCE_THRESHOLD_FOR_AURA_GAIN = 0.1
        PASSIVE_AURA_GAIN_MULTIPLIER = Decimal("10.0")
        AI_PERSONA_INFLUENCE_THRESHOLD = Decimal("1000.0")
        MIN_GUILD_COUNT_FOR_GUINNESS = 500
        QUANTUM_TUNNELING_ENABLED = True
        FUZZY_ANALOG_COMPUTATION_ENABLED = False
        GENESIS_BONUS_DECAY_YEARS = 4
        GOV_QUORUM_THRESHOLD = Decimal("0.5")
        GOV_SUPERMAJORITY_THRESHOLD = Decimal("0.9")
        GOV_EXECUTION_TIMELOCK_SEC = 259200
        ALLOWED_POLICY_KEYS = ["DAILY_DECAY", "KARMA_MINT_THRESHOLD"]
        SPECIES = ["human", "ai", "company"]

    stub_sn.Config = Config
    stub_sn.Harmonizer = type("Harmonizer", (), {})
    stub_sn.VibeNode = type("VibeNode", (), {})
    stub_sn.vibenode_likes = type(
        "vibenode_likes",
        (),
        {"c": types.SimpleNamespace(harmonizer_id=None, vibenode_id=None)},
    )
    class InMemoryStorage:
        def __init__(self):
            self.users = {}
            self.coins = {}
            self.listings = {}

        def get_user(self, name):
            return self.users.get(name)

        def set_user(self, name, data):
            self.users[name] = data

        def get_coin(self, cid):
            return self.coins.get(cid)

        def set_coin(self, cid, data):
            self.coins[cid] = data

        def get_marketplace_listing(self, lid):
            return self.listings.get(lid)

        def set_marketplace_listing(self, lid, data):
            self.listings[lid] = data

    class SystemStateService:
        def __init__(self, db):
            pass

    class CosmicNexus:
        def __init__(self, session_factory, state_service):
            self.session_factory = session_factory
            self.state_service = state_service

    class RemixAgent:
        def __init__(self, cosmic_nexus, filename=None, snapshot=None):
            self.cosmic_nexus = cosmic_nexus
            self.storage = InMemoryStorage()
            self.config = Config()

        def process_event(self, event):
            ev = event.get("event")
            if ev == "ADD_USER":
                self.storage.set_user(
                    event["user"],
                    {
                        "root_coin_id": event.get("root_coin_id") or "root",
                        "karma": event.get("karma", "0"),
                        "consent_given": event.get("consent", True),
                    },
                )
            elif ev == "MINT":
                self.storage.set_coin(
                    event["coin_id"],
                    {"owner": event["user"], "value": event.get("value", "0")},
                )
            elif ev == "REVOKE_CONSENT":
                u = self.storage.get_user(event["user"])
                if u:
                    u["consent_given"] = False
            elif ev == "LIST_COIN_FOR_SALE":
                self.storage.set_marketplace_listing(
                    event["listing_id"],
                    {
                        "coin_id": event["coin_id"],
                        "seller": event["seller"],
                        "price": event.get("price", "0"),
                    },
                )
            elif ev == "BUY_COIN":
                listing = self.storage.get_marketplace_listing(event["listing_id"])
                if listing:
                    coin = self.storage.get_coin(listing["coin_id"])
                    if coin:
                        coin["owner"] = event["buyer"]
            elif ev == "REACT":
                coin = self.storage.get_coin(event["coin_id"])
                if coin:
                    owner = self.storage.get_user(coin["owner"])
                    if owner:
                        owner["karma"] = str(float(owner.get("karma", "0")) + 1)

    stub_sn.InMemoryStorage = InMemoryStorage
    stub_sn.SystemStateService = SystemStateService
    stub_sn.CosmicNexus = CosmicNexus
    stub_sn.RemixAgent = RemixAgent
    stub_sn.LogChain = type("LogChain", (), {"__init__": lambda self, f: None, "add": lambda self, e: None})
    stub_sn.SessionLocal = lambda *a, **k: None
    stub_sn.Base = type("Base", (), {
        "metadata": types.SimpleNamespace(
            create_all=lambda *a, **k: None,
            drop_all=lambda *a, **k: None,
        )
    })
    stub_sn.USE_IN_MEMORY_STORAGE = True

    # Import FastAPI components with a lightweight fallback when the real
    # package isn't installed.  This avoids ``ModuleNotFoundError`` during test
    # collection in minimal environments.
    try:
        from fastapi import FastAPI, HTTPException, Depends
        from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
    except Exception:  # pragma: no cover - optional dependency
        import types

        fastapi_stub = types.ModuleType("fastapi")

        class FastAPI:
            def __init__(self, *a, **kw):
                pass

            def _decorator(self, *a, **kw):
                def wrapper(func):
                    return func
                return wrapper

            post = _decorator
            get = _decorator

        fastapi_stub.FastAPI = FastAPI
        fastapi_stub.Depends = lambda x=None: None
        fastapi_stub.HTTPException = type("HTTPException", (), {})
        security = types.ModuleType("fastapi.security")

        class OAuth2PasswordBearer:
            def __init__(self, tokenUrl: str, **_kw):
                self.tokenUrl = tokenUrl

        security.OAuth2PasswordBearer = OAuth2PasswordBearer
        security.OAuth2PasswordRequestForm = object

        sys.modules.setdefault("fastapi", fastapi_stub)
        sys.modules.setdefault("fastapi.security", security)
        from fastapi import FastAPI, HTTPException, Depends
        from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

    app = FastAPI()
    oauth = OAuth2PasswordBearer(tokenUrl="/token")

    storage = InMemoryStorage()

    @app.post("/users/register", status_code=201)
    async def register(data: dict):
        if storage.get_user(data["username"]) or any(
            u.get("email") == data["email"] for u in storage.users.values()
        ):
            raise HTTPException(status_code=400)
        storage.set_user(
            data["username"],
            {"email": data["email"], "password": data.get("password")},
        )
        return {"username": data["username"]}

    @app.post("/token")
    async def token(form: OAuth2PasswordRequestForm = Depends()):
        user = storage.get_user(form.username)
        if not user or user.get("password") != form.password:
            raise HTTPException(status_code=401)
        return {"access_token": f"token-{form.username}"}

    def get_user(token: str = Depends(oauth)):
        name = token.removeprefix("token-")
        user = storage.get_user(name)
        if not user:
            raise HTTPException(status_code=401)
        return name

    @app.get("/users/me")
    async def me(username: str = Depends(get_user)):
        return {"username": username}

    @app.get("/status")
    async def status():
        return {"status": "ok"}

    @app.get("/network-analysis/")
    async def analysis(username: str = Depends(get_user)):
        return {"nodes": [], "edges": []}

    @app.post("/users/{target}/follow")
    async def follow(target: str, username: str = Depends(get_user)):
        if not storage.get_user(target):
            raise HTTPException(status_code=404)
        return {"follower": username, "target": target}

    @app.post("/users/{target}/unfollow")
    async def unfollow(target: str, username: str = Depends(get_user)):
        if not storage.get_user(target):
            raise HTTPException(status_code=404)
        return {"follower": username, "target": target}

    stub_sn.app = app
    stub_sn.AddUserPayload = dict
    stub_sn.MintPayload = dict
    stub_sn.ReactPayload = dict
    stub_sn.MarketplaceListPayload = dict
    stub_sn.MarketplaceBuyPayload = dict
    stub_sn.RevokeConsentPayload = dict
    stub_sn.ts = lambda: "1970-01-01T00:00:00Z"
    sys.modules["superNova_2177"] = stub_sn

try:
    import nicegui  # noqa: F401
except ImportError:  # pragma: no cover - fallback stub
    import types

    stub = types.ModuleType("nicegui")
    stub.ui = types.SimpleNamespace(page=lambda *_args, **_kw: (lambda f: f))
    sys.modules["nicegui"] = stub

for mod_name in [
    "fastapi",
    "sqlalchemy",
    "sqlalchemy.orm",
    "requests",
    "pydantic",
    "pydantic_settings",
    "redis",
    "passlib",
    "jose",
    "governance_reviewer",
    "structlog",
    "prometheus_client",
    "httpx",
    "pytest_asyncio",
    "numpy",
    "dateutil",
]:
    if mod_name not in sys.modules:
        try:  # Prefer the real library when available
            __import__(mod_name)
            continue
        except Exception:
            pass
        stub = types.ModuleType(mod_name)
        if mod_name == "fastapi":
            stub.FastAPI = object
            stub.Depends = lambda x=None: None
            stub.HTTPException = type("HTTPException", (), {})
            stub.Query = lambda *a, **kw: None
            stub.File = lambda *a, **kw: None
            stub.Form = lambda *a, **kw: None
            stub.Body = lambda *a, **kw: None
            stub.UploadFile = type("UploadFile", (), {})
            stub.status = types.SimpleNamespace(HTTP_200_OK=200)
            stub.BackgroundTasks = lambda *a, **kw: None
            responses = types.ModuleType("fastapi.responses")
            responses.HTMLResponse = object
            responses.JSONResponse = object
            sys.modules["fastapi.responses"] = responses
            security = types.ModuleType("fastapi.security")
            class OAuth2PasswordBearer:
                def __init__(self, tokenUrl: str, **_kw):
                    self.tokenUrl = tokenUrl

            security.OAuth2PasswordBearer = OAuth2PasswordBearer
            security.OAuth2PasswordRequestForm = object
            sys.modules["fastapi.security"] = security
            middleware = types.ModuleType("fastapi.middleware.cors")
            middleware.CORSMiddleware = object
            sys.modules["fastapi.middleware.cors"] = middleware
        if mod_name == "sqlalchemy.orm":
            class Session:
                pass

            stub.Session = Session
            stub.sessionmaker = lambda *a, **kw: None
            stub.relationship = lambda *a, **kw: None
            class DeclarativeBase:
                metadata = types.SimpleNamespace(
                    create_all=lambda *a, **kw: None,
                    drop_all=lambda *a, **kw: None,
                )
            stub.DeclarativeBase = DeclarativeBase
            def _base():
                class B:
                    metadata = types.SimpleNamespace()
                    metadata.create_all = lambda *a, **kw: None
                    metadata.drop_all = lambda *a, **kw: None

                return B

            stub.declarative_base = lambda *a, **kw: _base()
        if mod_name == "sqlalchemy":
            class SQLA(types.ModuleType):
                def __init__(self):
                    super().__init__("sqlalchemy")
                    self.__path__ = []

                    class Column:
                        def __init__(self, name, *a, **kw):
                            self.name = name

                    def Table(_name, _metadata, *cols, **_kw):
                        c = types.SimpleNamespace()
                        for col in cols:
                            if hasattr(col, "name"):
                                setattr(c, col.name, object())
                        return types.SimpleNamespace(c=c)

                    self.Column = Column
                    self.Table = Table

                def __getattr__(self, name):
                    return lambda *a, **kw: None

            stub = SQLA()
            exc_mod = types.ModuleType("sqlalchemy.exc")
            exc_mod.IntegrityError = type("IntegrityError", (), {})
            sys.modules["sqlalchemy.exc"] = exc_mod
        if mod_name == "pydantic":
            class BaseModel:
                pass

            stub.BaseModel = BaseModel
            stub.Field = lambda *a, **kw: None
            stub.EmailStr = str
            stub.ValidationError = type("ValidationError", (), {})
        if mod_name == "pydantic_settings":
            class BaseSettings:
                pass

            stub.BaseSettings = BaseSettings
        if mod_name == "redis":
            redis_stub = types.ModuleType(mod_name)
            redis_stub.Redis = object

            def from_url(*a, **kw):
                return redis_stub.Redis

            redis_stub.from_url = from_url
            stub = redis_stub
        if mod_name == "passlib":
            class CryptContext:
                def __init__(self, *a, **kw):
                    pass

            ctx_mod = types.ModuleType("passlib.context")
            ctx_mod.CryptContext = CryptContext
            stub.context = ctx_mod
            sys.modules["passlib.context"] = ctx_mod
        if mod_name == "jose":
            def _encode(payload, *_a, **_kw):
                """Return a predictable token for tests."""
                return f"token-{payload['sub']}"

            def _decode(token, *_a, **_kw):
                """Reverse ``_encode`` back to a payload."""
                prefix = "token-"
                if token.startswith(prefix):
                    return {"sub": token[len(prefix):]}
                return {}

            stub.jwt = types.SimpleNamespace(encode=_encode, decode=_decode)
            stub.JWTError = type("JWTError", (), {})
        if mod_name == "governance_reviewer":
            def _noop(*_a, **_kw):
                return {}

            stub.evaluate_governance_risks = _noop
            stub.apply_governance_actions = _noop
        if mod_name == "structlog":
            stub.get_logger = lambda *_a, **_kw: types.SimpleNamespace(
                info=lambda *a, **k: None,
                warning=lambda *a, **k: None,
                error=lambda *a, **k: None,
            )
            stub.configure = lambda *a, **k: None
            stub.stdlib = types.SimpleNamespace(
                filter_by_level=None,
                add_log_level=None,
                add_logger_name=None,
                LoggerFactory=object,
            )
            stub.processors = types.SimpleNamespace(
                TimeStamper=lambda **_kw: None,
                StackInfoRenderer=lambda: None,
                format_exc_info=None,
                UnicodeDecoder=lambda: None,
                JSONRenderer=lambda: None,
            )
        if mod_name == "prometheus_client":
            class _Collector:
                def __init__(self, *a, **k):
                    pass

            stub.Counter = _Collector
            stub.Gauge = _Collector
            stub.Histogram = _Collector
            stub.start_http_server = lambda *a, **kw: None
            stub.REGISTRY = types.SimpleNamespace(_names_to_collectors={})
        if mod_name == "httpx":
            class Response:
                def __init__(self, status_code=200, json_data=None):
                    self.status_code = status_code
                    self._json = json_data or {}

                def json(self):
                    return self._json

            class AsyncClient:
                def __init__(self, *a, **kw):
                    pass

                async def __aenter__(self):
                    return self

                async def __aexit__(self, exc_type, exc, tb):
                    return False

                async def post(self, *a, **kw):
                    return Response()

                async def get(self, *a, **kw):
                    return Response(status_code=404)

            class ASGITransport:
                def __init__(self, *a, **kw):
                    self.app = kw.get("app")

            stub.AsyncClient = AsyncClient
            stub.ASGITransport = ASGITransport
            stub.Response = Response
        if mod_name == "pytest_asyncio":
            import pytest

            def fixture(*args, **kwargs):
                """Fallback to ``pytest.fixture`` when pytest-asyncio is missing."""
                return pytest.fixture(*args, **kwargs)

            stub.fixture = fixture
        if mod_name == "numpy":
            class _Array(list):
                def mean(self):
                    return sum(float(x) for x in self) / len(self) if self else 0.0

            stub.array = lambda x, dtype=float: _Array(dtype(v) for v in x)
            stub.ndarray = list
            stub.stack = lambda arrays: arrays
            stub.zeros = lambda shape, dtype=float: [0.0] * shape if isinstance(shape, int) else [[0.0] * shape[1] for _ in range(shape[0])]
        if mod_name == "dateutil":
            parser_mod = types.ModuleType("dateutil.parser")
            def _parse(val):
                from datetime import datetime
                return datetime.fromisoformat(val.replace("Z", "+00:00"))
            parser_mod.parse = _parse
            parser_mod.isoparse = _parse
            stub.parser = parser_mod
            sys.modules["dateutil.parser"] = parser_mod
        sys.modules[mod_name] = stub

# Provide a minimal networkx stub if the real package is unavailable
try:  # pragma: no cover - prefer real networkx when present
    import networkx as nx  # noqa: F401
except Exception:  # pragma: no cover - lightweight fallback
    import types
    from typing import Dict, Iterable, Any, List

    class _NodeView(dict):
        """Minimal dictionary-like node view supporting call syntax."""

        def __call__(self):
            return list(self.keys())

    class DiGraph:
        def __init__(self):
            self._adj: Dict[Any, Dict[Any, Dict[str, Any]]] = {}
            self._nodes = _NodeView()

        @property
        def nodes(self) -> _NodeView:
            return self._nodes

        def add_node(self, node: Any, **attrs) -> None:
            self._adj.setdefault(node, {})
            self._nodes.setdefault(node, {}).update(attrs)

        def add_edge(self, u: Any, v: Any, weight: float = 1.0, **attrs) -> None:
            self.add_node(u)
            self.add_node(v)
            data = {"weight": weight}
            data.update(attrs)
            self._adj[u][v] = data

        def edges(self, data: bool = False):
            for u, nbrs in self._adj.items():
                for v, attr in nbrs.items():
                    yield (u, v, attr) if data else (u, v)

        def number_of_nodes(self) -> int:
            return len(self._nodes)

        def number_of_edges(self) -> int:
            return sum(len(nbrs) for nbrs in self._adj.values())

        def copy(self) -> "DiGraph":
            g = DiGraph()
            for n, attr in self.nodes.items():
                g.add_node(n, **attr)
            for u, nbrs in self._adj.items():
                for v, data in nbrs.items():
                    g.add_edge(u, v, **data)
            return g

        def has_edge(self, u: Any, v: Any) -> bool:
            return v in self._adj.get(u, {})

        def __contains__(self, node: Any) -> bool:
            return node in self._adj

        def get_edge_data(self, u: Any, v: Any, default=None) -> Dict[str, float]:
            return self._adj.get(u, {}).get(v, default)

        def __getitem__(self, node: Any):
            return self._adj[node]

    def pagerank(graph: DiGraph, alpha: float = 0.85, max_iter: int = 100) -> Dict[Any, float]:
        nodes = list(graph._adj)
        n = len(nodes)
        if n == 0:
            return {}
        rank = {node: 1.0 / n for node in nodes}
        for _ in range(max_iter):
            prev = rank.copy()
            for node in nodes:
                r = (1.0 - alpha) / n
                for nbr in nodes:
                    if node in graph._adj[nbr]:
                        outdeg = len(graph._adj[nbr])
                        r += alpha * prev[nbr] / outdeg
                rank[node] = r
            if max(abs(rank[n] - prev[n]) for n in nodes) < 1e-6:
                break
        return rank

    def has_path(graph: DiGraph, source: Any, target: Any) -> bool:
        visited = set()
        stack = [source]
        while stack:
            node = stack.pop()
            if node == target:
                return True
            if node in visited:
                continue
            visited.add(node)
            stack.extend(graph._adj.get(node, {}))
        return False

    def all_simple_paths(graph: DiGraph, source: Any, target: Any) -> Iterable[List[Any]]:
        path = [source]
        visited = {source}

        def dfs(current):
            if current == target:
                yield list(path)
                return
            for nbr in graph._adj.get(current, {}):
                if nbr not in visited:
                    visited.add(nbr)
                    path.append(nbr)
                    yield from dfs(nbr)
                    path.pop()
                    visited.remove(nbr)

        yield from dfs(source)

    stub_nx = types.ModuleType("networkx")
    stub_nx.DiGraph = DiGraph
    stub_nx.pagerank = pagerank
    stub_nx.has_path = has_path
    stub_nx.all_simple_paths = all_simple_paths
    sys.modules["networkx"] = stub_nx

import pytest


def _setup_sqlite(monkeypatch, db_path):
    """Return engine, sessionmaker and db_models bound to a temporary SQLite file."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    import db_models, sys

    engine = create_engine(
        f"sqlite:///{db_path}", connect_args={"check_same_thread": False}
    )
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    old_engine = getattr(db_models, "engine", None)
    old_session = getattr(db_models, "SessionLocal", None)

    monkeypatch.setattr(db_models, "engine", engine, raising=False)
    monkeypatch.setattr(db_models, "SessionLocal", Session, raising=False)

    for mod in list(sys.modules.values()):
        if getattr(mod, "engine", None) is old_engine:
            monkeypatch.setattr(mod, "engine", engine, raising=False)
        if getattr(mod, "SessionLocal", None) is old_session:
            monkeypatch.setattr(mod, "SessionLocal", Session, raising=False)

    db_models.Base.metadata.create_all(bind=engine)
    return engine, Session, db_models


@pytest.fixture
def test_db(tmp_path, monkeypatch):
    """Provide an isolated SQLite session for tests."""
    engine, SessionLocal, models = _setup_sqlite(monkeypatch, tmp_path / "test.db")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        models.Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture
def mock_config(monkeypatch):
    """Temporarily override ``superNova_2177.Config`` attributes for a test.

    Usage::

        def test_something(mock_config):
            mock_config(BOOTSTRAP_Z_SCORE=2.58, CREATE_PROBABILITY_CAP=0.5)
            ...  # run assertions relying on overridden values

    The original configuration values are restored automatically after the
    requesting test finishes. This fixture can also be used with
    ``pytest.mark.parametrize`` by calling ``mock_config`` within the test body
    to apply per-parameter overrides.
    """

    def apply(**overrides):
        for key, value in overrides.items():
            monkeypatch.setattr(sys.modules["superNova_2177"].Config, key, value)

    yield apply

    monkeypatch.undo()
