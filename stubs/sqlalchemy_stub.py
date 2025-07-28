import types


class Column:
    def __init__(self, *args, **kwargs):  # pragma: no cover - simplified
        self.name = args[0] if args and isinstance(args[0], str) else None

    def __set_name__(self, owner, name):  # pragma: no cover - simplified
        self.name = name
        self.model = owner

    def __hash__(self):  # pragma: no cover - simplified
        return hash((self.model, self.name))

    def __get__(self, instance, owner):  # pragma: no cover - simplified
        if instance is None:
            return self
        return instance.__dict__.get(self.name)

    def __set__(self, instance, value):  # pragma: no cover - simplified
        instance.__dict__[self.name] = value

    def __eq__(self, other):  # pragma: no cover - simplified
        return lambda obj: getattr(obj, self.name) == other

class Integer:
    def __init__(self, *args, **kwargs):  # pragma: no cover - trivial
        pass

class String:
    def __init__(self, *args, **kwargs):  # pragma: no cover - trivial
        pass

class Text:
    def __init__(self, *args, **kwargs):  # pragma: no cover - trivial
        pass

class Boolean:
    def __init__(self, *args, **kwargs):  # pragma: no cover - trivial
        pass

class DateTime:
    def __init__(self, *args, **kwargs):  # pragma: no cover - trivial
        pass

class ForeignKey:
    def __init__(self, *args, **kwargs):
        pass

class Table:
    def __init__(self, name, metadata, *columns, **_kw):  # pragma: no cover - simplified
        self.name = name
        c = types.SimpleNamespace()
        for col in columns:
            if hasattr(col, "name") and col.name is not None:
                setattr(c, col.name, object())
        self.c = c

class Float:
    def __init__(self, *args, **kwargs):  # pragma: no cover - trivial
        pass

class JSON:
    def __init__(self, *args, **kwargs):  # pragma: no cover - trivial
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
        real_model = getattr(model, "model", model)
        data = self.engine.storage.get(real_model, [])
        data += [o for o in self._pending if isinstance(o, real_model)]
        return Session._Query(data)

    # Simple execute/select emulation ----------------------------------------
    def execute(self, statement):
        if isinstance(statement, Select):
            data = self.engine.storage.get(statement.model, [])
            data += [o for o in self._pending if isinstance(o, statement.model)]
            for pred in statement.predicates:
                data = [o for o in data if pred(o)]
            return Result(data)
        return Result([])

    def close(self) -> None:  # pragma: no cover - trivial
        pass

class IntegrityError(Exception):
    pass


class Result:
    """Minimal result wrapper mimicking SQLAlchemy execution results."""

    def __init__(self, data):
        self._data = list(data)

    # Support ``scalars().first()`` pattern used in the code
    def scalars(self):  # pragma: no cover - trivial
        return self

    def first(self):  # pragma: no cover - trivial
        return self._data[0] if self._data else None

    def scalar_one_or_none(self):
        """Return the first element or ``None`` if the result set is empty."""
        return self._data[0] if self._data else None

    def all(self):  # pragma: no cover - trivial
        return list(self._data)


class Select:
    """Very small subset of :func:`sqlalchemy.select`."""

    def __init__(self, model):
        self.model = model
        self.predicates = []

    def filter(self, predicate):
        if predicate is not None:
            self.predicates.append(predicate)
        return self

    def filter_by(self, **kw):
        def pred(obj):
            return all(getattr(obj, k, None) == v for k, v in kw.items())

        return self.filter(pred)

    def where(self, *predicates):
        for predicate in predicates:
            self.filter(predicate)
        return self

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

        def __init__(self, **kw):  # pragma: no cover - simplified
            for k, v in kw.items():
                setattr(self, k, v)

    return Base

class func:
    pass


def select(model):  # pragma: no cover - simplified
    return Select(model)
