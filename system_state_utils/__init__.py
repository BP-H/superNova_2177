# RFC_V5_1_INIT
"""Helper utilities for SystemState management."""

import json
import datetime
from typing import Any, Dict

from sqlalchemy import select
from sqlalchemy.orm import Session
from db_models import SystemState

__all__ = ["log_event"]


def log_event(db: Session, category: str, payload: Dict[str, Any]) -> None:
    """Append an event record to SystemState under ``log:<category>``."""
    key = f"log:{category}"
    stmt = select(SystemState).where(SystemState.key == key)
    state = db.execute(stmt).scalar_one_or_none()
    events = []
    if state:
        try:
            events = json.loads(state.value)
        except Exception:
            events = []
    entry = {"timestamp": datetime.datetime.utcnow().isoformat(), **payload}
    events.append(entry)
    if state:
        state.value = json.dumps(events)
    else:
        db.add(SystemState(key=key, value=json.dumps(events)))
    db.commit()
