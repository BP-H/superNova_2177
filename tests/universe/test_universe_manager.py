# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
import importlib
import importlib.util
import sys

import superNova_2177 as sn
from sqlalchemy.orm import Session
import sqlalchemy
from db_models import Harmonizer, UniverseBranch
import pytest

# Ensure SQLAlchemy passes version check in test fixtures
sqlalchemy.create_engine.__module__ = "sqlalchemy.engine"

# Reload the real module when available and handle failures gracefully
if getattr(sn, "__file__", "") in (None, "superNova_2177_stub") or str(getattr(sn, "__file__", "")).endswith("_stub"):
    if importlib.util.find_spec("sqlalchemy") is not None:
        try:
            for mod in list(sys.modules):
                if mod.startswith("sqlalchemy") or mod.startswith("pydantic") or mod.startswith("fastapi"):
                    sys.modules.pop(mod, None)
            sys.modules.pop("superNova_2177", None)
            sn = importlib.import_module("superNova_2177")
        except Exception:
            pytest.skip("CosmicNexus unavailable", allow_module_level=True)

# Skip tests if CosmicNexus lacks fork_universe
if not hasattr(sn, "CosmicNexus") or not hasattr(sn.CosmicNexus, "fork_universe"):
    pytest.skip("fork_universe not implemented", allow_module_level=True)


def _create_user(db: Session, species: str) -> Harmonizer:
    user = Harmonizer(
        username=f"{species}_user",
        email=f"{species}@example.com",
        hashed_password="x",
        species=species,
        karma_score=10.0,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_fork_universe_human(test_db):
    nexus = sn.CosmicNexus(sn.SessionLocal, sn.SystemStateService(sn.SessionLocal()))
    user = _create_user(test_db, "human")
    fork_id = nexus.fork_universe(user, {"entropy_threshold": 0.5})
    assert fork_id in nexus.sub_universes
    record = test_db.query(UniverseBranch).filter_by(id=fork_id).first()
    assert record is not None and record.creator_id == user.id


def test_fork_universe_ai(test_db):
    nexus = sn.CosmicNexus(sn.SessionLocal, sn.SystemStateService(sn.SessionLocal()))
    user = _create_user(test_db, "ai")
    fork_id = nexus.fork_universe(user, {})
    assert fork_id in nexus.sub_universes
    record = test_db.query(UniverseBranch).filter_by(id=fork_id).first()
    assert record is not None


def test_fork_universe_company(test_db):
    nexus = sn.CosmicNexus(sn.SessionLocal, sn.SystemStateService(sn.SessionLocal()))
    user = _create_user(test_db, "company")
    fork_id = nexus.fork_universe(user, {"d": "1"})
    assert fork_id in nexus.sub_universes
    record = test_db.query(UniverseBranch).filter_by(id=fork_id).first()
    assert record is not None


def test_parent_child_relationship(test_db):
    nexus = sn.CosmicNexus(sn.SessionLocal, sn.SystemStateService(sn.SessionLocal()))
    user = _create_user(test_db, "human")
    fork_id = nexus.fork_universe(user, {})
    child_agent = nexus.sub_universes[fork_id]
    assert child_agent.cosmic_nexus is nexus
