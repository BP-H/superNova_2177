"""Proxy module to load shared fixtures from ``tests/conftest.py``.

The import is performed via file location to avoid ``ImportPathMismatchError``
when other ``tests`` packages (e.g. the frontend) are also present.
"""

import sys
from importlib import util
from pathlib import Path

ROOT_TESTS_CONFTST = Path(__file__).resolve().parent / "tests" / "conftest.py"
spec = util.spec_from_file_location("root_tests_conftest", ROOT_TESTS_CONFTST)
_module = util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = _module
spec.loader.exec_module(_module)

globals().update(
    {name: getattr(_module, name) for name in dir(_module) if not name.startswith("_")}
)
