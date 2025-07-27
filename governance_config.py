from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.orm import Session

import numpy as np
import logging

try:  # optional quantum consensus engine
    from qutip import basis, tensor, sigmaz, expect, qeye, bell_state
except Exception:  # pragma: no cover - qutip may be missing in minimal env
    basis = tensor = sigmaz = expect = qeye = bell_state = None

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


def calculate_entropy_divergence(config: dict, base: object | None = None) -> float:
    """Return mean absolute deviation from base Config values."""
    if base is None:
        try:
            from superNova_2177 import Config as base
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
                logging.warning("Ignoring non-numeric configuration for key %s", k)
                continue
            diffs.append(abs(v_val - base_v))
    if not diffs:
        return 0.0
    arr = np.array(diffs, dtype=float)
    return float(arr.mean())


def quantum_consensus(
    votes: list[bool], entanglement: float | list[list[float]] | None = None
) -> float:
    """Compute consensus level with optional entanglement modeling.

    Parameters
    ----------
    votes:
        List of boolean votes.
    entanglement:
        Either a global correlation factor ``0 <= f <= 1`` or an ``NxN`` matrix
        describing pairwise entanglement strengths.
    """

    if not votes:
        return 0.0

    if basis is None:
        return sum(votes) / len(votes)

    states = [basis(2, 1 if v else 0) for v in votes]
    joint = tensor(states)

    if entanglement is None:
        obs = tensor([sigmaz()] * len(votes))
        expectation = expect(obs, joint)
        return float((expectation + 1) / 2)

    if not isinstance(entanglement, (int, float)):
        arr = np.array(entanglement, dtype=float)
        if arr.shape != (len(votes), len(votes)):
            raise ValueError("entanglement matrix must match vote count")
        corr = float(np.clip(arr.mean(), 0.0, 1.0))
    else:
        corr = float(entanglement)
        if not 0.0 <= corr <= 1.0:
            raise ValueError("correlation factor must be between 0 and 1")

    pairs: list = []
    i = 0
    while i < len(votes) - 1:
        if votes[i] == votes[i + 1]:
            pair = bell_state("00")
        else:
            pair = bell_state("10")
        pairs.append(pair)
        i += 2

    if len(votes) % 2 == 1:
        pairs.append(basis(2, 1 if votes[-1] else 0))

    ent_state = tensor(pairs)
    joint = (1 - corr) * joint + corr * ent_state

    expectations = []
    for idx in range(len(votes)):
        obs = tensor(
            [sigmaz() if i == idx else qeye(2) for i in range(len(votes))]
        )
        expectations.append(expect(obs, joint))
    mean_exp = sum(expectations) / len(votes)
    return float((mean_exp + 1) / 2)
