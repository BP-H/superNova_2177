import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

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
]:
    if mod_name not in sys.modules:
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
            stub.jwt = types.SimpleNamespace(encode=lambda *a, **kw: "", decode=lambda *a, **kw: {})
            stub.JWTError = type("JWTError", (), {})
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


@pytest.fixture
def test_db(tmp_path):
    """Provide an in-memory SQLite session for tests."""
    from db_models import Base, SessionLocal, engine, init_db

    init_db()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


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
