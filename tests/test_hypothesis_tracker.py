import re

from hypothesis_tracker import register_hypothesis
from db_models import HypothesisRecord


def test_register_hypothesis_generates_unique_id(test_db):
    hid = register_hypothesis("test hypothesis", test_db)

    assert hid.startswith("HYP_")
    assert re.match(r"^HYP_\d+_[0-9a-f]{8}$", hid)

    record = test_db.query(HypothesisRecord).filter_by(id=hid).first()
    assert record is not None

    hid2 = register_hypothesis("another hypothesis", test_db)
    assert hid != hid2


def test_metadata_json_persistence_new_session(test_db):
    metadata = {"creator": "tester", "timestamp": "2025-01-01T00:00:00"}
    hid = register_hypothesis("metadata test", test_db, metadata)

    test_db.close()
    from db_models import SessionLocal

    new_session = SessionLocal()
    try:
        record = new_session.query(HypothesisRecord).filter_by(id=hid).first()
        assert record is not None
        assert record.metadata_json == metadata
    finally:
        new_session.close()

