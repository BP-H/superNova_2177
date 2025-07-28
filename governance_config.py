from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.orm import Session

import numpy as np
import logging

try:  # optional quantum consensus engine
    from qutip import basis, tensor, sigmaz, expect
except Exception:  # pragma: no cover - qutip may be missing in minimal env
    basis = tensor = sigmaz = expect = None

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
    """Return karma score cutoff for given percentile.

    Attempts to compute the percentile directly in SQL using
    ``func.percentile_cont``. If the database or dialect does not support the
    percentile window function, falls back to loading all karma values into
    memory and sorting them.
    """
    close_session = False
    if db is None:
        db = SessionLocal()
        close_session = True
    try:
        if not 0 <= percentile <= 1:
            raise ValueError("percentile must be between 0 and 1")

        # Try native percentile support first.
        try:
            result = (
                db.query(
                    func.percentile_cont(1 - percentile).within_group(
                        Harmonizer.karma_score
                    )
                ).scalar()
            )
            if result is not None:
                return float(result)
        except Exception:
            # Dialect may not support percentile_cont; fall back to manual method.
            pass

        values = [h.karma_score for h in db.query(Harmonizer.karma_score).all()]
        if not values:
            return 0.0
        values.sort()
        # Clamp percentile-derived index so ``percentile`` values of exactly 0
        # or 1 map to list bounds, even when only a single value exists.
        index = round((1 - percentile) * (len(values) - 1))
        index = max(0, min(index, len(values) - 1))
        return values[int(index)]
    finally:
        if close_session:
            db.close()


def is_eligible_for_fork(user: Harmonizer, db: Session | None = None) -> bool:
    """Check if user meets karma percentile cutoff for forking."""
    percentile = get_forking_percentile(db)
    cutoff = karma_percentile_cutoff(percentile, db)
    return user.karma_score >= cutoff


def calculate_entropy_divergence(config: dict, base: object | None = None) -> float:
    """Return mean absolute deviation from base Config values."""
    if base is None:
        try:
            from config import Config as base
        except Exception as exc:  # pragma: no cover - optional dependency
            raise ImportError(
                "Cannot import superNova_2177.Config for entropy divergence calculation"
            ) from exc
    diffs: list[float] = []
    for k, v in config.items():
        if hasattr(base, k):
            try:
                base_v = float(getattr(base, k))
                v_val = float(v)
            except ValueError:
                logging.warning(
                    "Ignoring non-numeric configuration for key %s with value %r",
                    k,
                    v,
                )
                continue
            diffs.append(abs(v_val - base_v))
    if not diffs:
        return 0.0
    arr = np.array(diffs, dtype=float)
    return float(arr.mean())


# TODO: explore entanglement-based consensus metrics
# Implementing a more realistic quantum model would allow
# contributors to simulate entangled voter states. This is
# currently a simple toy calculation and should be replaced
# or extended with a full entanglement simulation.
def quantum_consensus(votes: list[bool]) -> float:
    """Compute consensus level using a simple quantum-inspired model."""
    if not votes:
        return 0.0
    if basis is None:
        return sum(votes) / len(votes)
    states = [basis(2, 1 if v else 0) for v in votes]
    joint = tensor(states)
    obs = tensor([sigmaz()] * len(votes))
    expectation = expect(obs, joint)
    return float((expectation + 1) / 2)
