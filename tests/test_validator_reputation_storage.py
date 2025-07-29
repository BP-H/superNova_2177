# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
import pytest
import sys
from validator_reputation_tracker import save_reputations, load_reputations, DataAccessError
from db_models import ValidatorReputation


def test_save_and_load_reputations(test_db):
    reps = {"v1": 0.7, "v2": 0.3}
    save_reputations(reps, test_db)

    db_rows = {r.validator_id: r.reputation for r in test_db.query(ValidatorReputation).all()}
    assert db_rows == reps

    loaded = load_reputations(test_db)
    assert loaded == reps


def test_save_updates_existing(test_db):
    save_reputations({"v1": 0.4}, test_db)
    save_reputations({"v1": 0.9}, test_db)

    row = test_db.query(ValidatorReputation).filter_by(validator_id="v1").first()
    assert row.reputation == 0.9

def test_load_reputations_missing_models(monkeypatch, test_db):
    monkeypatch.setitem(sys.modules, 'db_models', None)
    from validator_reputation_tracker import load_reputations, DataAccessError
    with pytest.raises(DataAccessError):
        load_reputations(test_db)

