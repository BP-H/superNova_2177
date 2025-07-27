# RFC_V5_1_INIT
"""Helper utilities for SystemState management."""

import json
import datetime
from typing import Any, Dict

from sqlalchemy.orm import Session
from db_models import SystemState


def log_event(db: Session, category: str, payload: Dict[str, Any]) -> None:
    """Append an event record to SystemState under ``log:<category>``."""
    key = f"log:{category}"
    state = db.query(SystemState).filter(SystemState.key == key).first()
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
