import importlib
import types
from types import ModuleType

class _MissingModule(ModuleType):
    """Stub module for missing optional dependencies."""

    def __init__(self, name: str, message: str) -> None:
        super().__init__(name)
        self._message = message

    def __getattr__(self, attr: str) -> ModuleType:
        raise ImportError(self._message)

    def __bool__(self) -> bool:  # pragma: no cover - bool check convenience
        return False

    @property
    def _optional_missing(self) -> bool:  # marker for detection
        return True


def optional_import(module: str, attr: str | None = None):
    """Return imported module or attribute, or a stub raising ImportError."""
    try:
        mod = importlib.import_module(module)
        return getattr(mod, attr) if attr else mod
    except Exception:
        msg = f"Optional dependency '{module}' is required for this feature"

        def _missing(*_a, **_k):
            raise ImportError(msg)

        _missing._optional_missing = True  # type: ignore[attr-defined]

        return _missing if attr else _MissingModule(module, msg)
