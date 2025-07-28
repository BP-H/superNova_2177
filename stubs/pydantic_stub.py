class ValidationError(Exception):
    """Simplified validation error."""
    pass

class BaseModel:
    """Very small subset of pydantic BaseModel used in tests."""
    def __init__(self, **data):
        for k, v in data.items():
            setattr(self, k, v)

    def dict(self, *args, **kwargs):  # pragma: no cover - trivial
        return self.__dict__.copy()

# ``Field`` simply returns the default or invokes a ``default_factory`` if
# provided.  Additional validation features are intentionally omitted.
def Field(default=None, *, default_factory=None, **_kw):  # noqa: D401
    """Return ``default`` without evaluation to mimic pydantic's API."""
    return default

# ``EmailStr`` is treated the same as ``str`` in the lightweight stub.
class EmailStr(str):
    pass
