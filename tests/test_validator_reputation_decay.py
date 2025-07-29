# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
import datetime
from validators.reputation_influence_tracker import compute_validator_reputations

def _build_validations(ts):
    return [
        {"validator_id": "a", "hypothesis_id": "h1", "score": 0.8, "timestamp": ts.isoformat()},
        {"validator_id": "a", "hypothesis_id": "h1", "score": 0.75, "timestamp": ts.isoformat()},
        {"validator_id": "a", "hypothesis_id": "h1", "score": 0.78, "timestamp": ts.isoformat()},
    ]


def test_reputation_decays_with_age():
    now = datetime.datetime.utcnow().replace(microsecond=0)
    old_ts = now - datetime.timedelta(days=60)

    recent_vals = _build_validations(now)
    old_vals = _build_validations(old_ts)

    consensus = {"h1": 0.8}

    recent = compute_validator_reputations(recent_vals, consensus, current_time=now, half_life_days=30)
    old = compute_validator_reputations(old_vals, consensus, current_time=now, half_life_days=30)

    rep_recent = recent["validator_reputations"].get("a")
    rep_old = old["validator_reputations"].get("a")

    assert rep_recent > rep_old


def test_half_life_zero_defaults_to_config():
    now = datetime.datetime.utcnow().replace(microsecond=0)
    vals = _build_validations(now)
    consensus = {"h1": 0.8}

    default_result = compute_validator_reputations(vals, consensus, current_time=now)
    zero_result = compute_validator_reputations(vals, consensus, current_time=now, half_life_days=0)

    assert zero_result["validator_reputations"] == default_result["validator_reputations"]
