from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.orm import Session

from db_models import Harmonizer, SessionLocal, SystemState


def get_forking_percentile(db: Session | None = None) -> float:
    """Retrieve current FORKING_KARMA_PERCENTILE from governance table."""
    close = False
    if db is None:
        db = SessionLocal()
        close = True
    try:
        record = db.query(SystemState).filter_by(key="FORKING_KARMA_PERCENTILE").first()
        if record:
            return float(record.value)
        return FORKING_KARMA_PERCENTILE
    finally:
        if close:
            db.close()


def set_forking_percentile(value: float, db: Session | None = None) -> None:
    close = False
    if db is None:
        db = SessionLocal()
        close = True
    try:
        record = db.query(SystemState).filter_by(key="FORKING_KARMA_PERCENTILE").first()
        if record:
            record.value = str(value)
        else:
            record = SystemState(key="FORKING_KARMA_PERCENTILE", value=str(value))
            db.add(record)
        db.commit()
    finally:
        if close:
            db.close()

# Forking governance configuration
FORKING_KARMA_PERCENTILE = 0.75  # Default value if no setting stored


def karma_percentile_cutoff(percentile: float, db: Session | None = None) -> float:
    """Return karma score cutoff for given percentile."""
    close_session = False
    if db is None:
        db = SessionLocal()
        close_session = True
    try:
        if not 0 <= percentile <= 1:
            raise ValueError("percentile must be between 0 and 1")
        values = [h.karma_score for h in db.query(Harmonizer.karma_score).all()]
        if not values:
            return 0.0
        values.sort()
        index = int((1 - percentile) * len(values))
        return values[index]
    finally:
        if close_session:
            db.close()


def is_eligible_for_fork(user: Harmonizer, db: Session | None = None) -> bool:
    """Check if user meets karma percentile cutoff for forking."""
    percentile = get_forking_percentile(db)
    cutoff = karma_percentile_cutoff(percentile, db)
    return user.karma_score >= cutoff
