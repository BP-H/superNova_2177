import importlib.util
from pathlib import Path
import pytest
import sys
import types

# Provide minimal stubs for heavy optional modules required during import
sys.modules.setdefault("immutable_tri_species_adjust", types.ModuleType("immutable_tri_species_adjust"))
sys.modules.setdefault("optimization_engine", types.ModuleType("optimization_engine"))
sys.modules.setdefault("dotenv", types.ModuleType("dotenv"))
sys.modules["dotenv"].load_dotenv = lambda *a, **k: None
sys.modules.setdefault("structlog", types.ModuleType("structlog"))
_structlog = sys.modules["structlog"]

class _DummyLogger:
    def bind(self, *a, **k):
        return self

    def info(self, *a, **k):
        pass

    def warning(self, *a, **k):
        pass

    def error(self, *a, **k):
        pass

    def debug(self, *a, **k):
        pass


_structlog.get_logger = lambda *a, **k: _DummyLogger()
_structlog.configure = lambda *a, **k: None
_structlog.stdlib = types.SimpleNamespace(
    LoggerFactory=lambda *a, **k: object(),
    BoundLogger=_DummyLogger,
    filter_by_level=lambda *a, **k: None,
    add_log_level=lambda *a, **k: None,
    add_logger_name=lambda *a, **k: None,
)
_structlog.processors = types.SimpleNamespace(
    TimeStamper=lambda *a, **k: None,
    StackInfoRenderer=lambda *a, **k: None,
    format_exc_info=lambda *a, **k: None,
    UnicodeDecoder=lambda *a, **k: None,
    JSONRenderer=lambda *a, **k: None,
)

sys.modules.setdefault("prometheus_client", types.ModuleType("prometheus_client"))
sys.modules["prometheus_client"].Counter = lambda *a, **k: None
sys.modules["prometheus_client"].Gauge = lambda *a, **k: None
sys.modules["prometheus_client"].Summary = lambda *a, **k: None
sys.modules["prometheus_client"].start_http_server = lambda *a, **k: None
sys.modules.setdefault("numpy", types.ModuleType("numpy"))
sys.modules.setdefault("qutip", types.ModuleType("qutip"))

import logging
if not hasattr(logging, "getRoot"):
    logging.getRoot = logging.getLogger

# Provide a Config stub so early module initialization succeeds

# Dynamically load only the ``InMemoryStorage`` class from the source file
source = Path(__file__).resolve().parents[1] / "superNova_2177.py"
text = source.read_text()
start = text.index("class AbstractStorage")
end = text.index("# --- MODULE: tasks.py ---", start)
namespace: dict = {}
exec(
    text[start:end],
    {
        "copy": __import__("copy"),
        "contextmanager": __import__("contextlib").contextmanager,
        "logging": logging,
        "Optional": __import__("typing").Optional,
        "Dict": __import__("typing").Dict,
        "Any": __import__("typing").Any,
        "List": __import__("typing").List,
        "Callable": __import__("typing").Callable,
        "Session": object,
    },
    namespace,
)
InMemoryStorage = namespace["InMemoryStorage"]


def test_transaction_rolls_back_existing_entries():
    storage = InMemoryStorage()
    storage.set_user("u", {"karma": 1})
    storage.set_coin("c", {"amount": 1})
    storage.set_proposal("p", {"value": 1})
    storage.set_marketplace_listing("l", {"price": 1})

    with pytest.raises(RuntimeError):
        with storage.transaction():
            storage.set_user("u", {"karma": 2})
            storage.set_coin("c", {"amount": 2})
            storage.set_proposal("p", {"value": 2})
            storage.set_marketplace_listing("l", {"price": 2})
            raise RuntimeError("boom")

    assert storage.get_user("u") == {"karma": 1}
    assert storage.get_coin("c") == {"amount": 1}
    assert storage.get_proposal("p") == {"value": 1}
    assert storage.get_marketplace_listing("l") == {"price": 1}


def test_transaction_removes_new_entries_on_rollback():
    storage = InMemoryStorage()
    with pytest.raises(ValueError):
        with storage.transaction():
            storage.set_proposal("new", {})
            storage.set_marketplace_listing("new", {})
            raise ValueError()

    assert storage.get_proposal("new") is None
    assert storage.get_marketplace_listing("new") is None
