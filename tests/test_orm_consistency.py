import importlib
import importlib.util
import sys

import superNova_2177 as sn
from sqlalchemy import create_engine

# Reload the real module if a lightweight stub is installed
if (
    getattr(sn, "__file__", "") in (None, "superNova_2177_stub")
    or str(getattr(sn, "__file__", "")).endswith("_stub")
) and importlib.util.find_spec("fastapi") is not None:
    for mod in list(sys.modules):
        if mod.startswith("fastapi") or mod.startswith("pydantic") or mod.startswith("sqlalchemy"):
            sys.modules.pop(mod, None)
    sys.modules.pop("superNova_2177", None)
    sn = importlib.import_module("superNova_2177")


def test_orm_consistency():
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )
    sn.Base.metadata.create_all(engine)
    session = sn.SessionLocal(bind=engine)
    try:
        session.query(sn.Harmonizer).all()
    finally:
        session.close()
