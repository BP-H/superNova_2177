class Column:
    def __init__(self, *args, **kwargs):
        pass

class Integer:
    pass

class String:
    pass

class Text:
    pass

class Boolean:
    pass

class DateTime:
    pass

class ForeignKey:
    def __init__(self, *args, **kwargs):
        pass

class Table:
    def __init__(self, *args, **kwargs):
        pass

class Float:
    pass

class JSON:
    pass

class Engine:
    """Lightweight stand-in for :class:`sqlalchemy.engine.Engine`."""

    def __init__(self, *args, **kwargs):
        self.storage = {}

    # Context manager helpers -------------------------------------------------
    def begin(self):  # pragma: no cover - trivial
        return self

    def __enter__(self):  # pragma: no cover - trivial
        return self

    def __exit__(self, exc_type, exc, tb):  # pragma: no cover - trivial
        return False

    def dispose(self):  # pragma: no cover - trivial
        pass


class Session:
    """Minimal in-memory session used by the tests."""

    def __init__(self, engine: Engine | None = None) -> None:
        self.engine = engine or Engine()
        self._pending = []

    # Basic persistence -------------------------------------------------------
    def add(self, obj) -> None:  # pragma: no cover - trivial
        self._pending.append(obj)

    def add_all(self, objs) -> None:  # pragma: no cover - trivial
        for obj in objs:
            self.add(obj)

    def commit(self) -> None:  # pragma: no cover - simplified
        for obj in self._pending:
            cls = obj.__class__
            self.engine.storage.setdefault(cls, []).append(obj)
        self._pending.clear()

    def rollback(self) -> None:  # pragma: no cover - trivial
        self._pending.clear()

    # Query API ---------------------------------------------------------------
    class _Query:
        def __init__(self, data):
            self._data = list(data)

        def filter_by(self, **kw):
            def match(obj):
                return all(getattr(obj, k, None) == v for k, v in kw.items())

            return Session._Query([o for o in self._data if match(o)])

        def filter(self, func):  # pragma: no cover - simplified
            return Session._Query([o for o in self._data if func(o)])

        def first(self):  # pragma: no cover - trivial
            return self._data[0] if self._data else None

        def all(self):  # pragma: no cover - trivial
            return list(self._data)

        def count(self):  # pragma: no cover - trivial
            return len(self._data)

    def query(self, model):  # pragma: no cover - simplified
        data = self.engine.storage.get(model, [])
        data += [o for o in self._pending if isinstance(o, model)]
        return Session._Query(data)

    def close(self) -> None:  # pragma: no cover - trivial
        pass

class IntegrityError(Exception):
    pass

def create_engine(*args, **kwargs):
    return Engine(*args, **kwargs)

def sessionmaker(*args, **kwargs):
    bind = kwargs.get("bind")

    def maker(*margs, **mkwargs):
        return Session(engine=bind)
    return maker

def relationship(*args, **kwargs):
    return None

def declarative_base():
    class Meta:
        def create_all(self, *a, **k):  # pragma: no cover - trivial
            pass

        def drop_all(self, *a, **k):  # pragma: no cover - trivial
            pass

    class Base:
        metadata = Meta()

    return Base

class func:
    pass
