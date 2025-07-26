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


def test_metadata_round_trip(test_db):
    hid = register_hypothesis("meta hypothesis", test_db, {"foo": "bar"})

    # load in a fresh session to ensure data persisted
    from db_models import SessionLocal
    new_db = SessionLocal()
    try:
        record = new_db.query(HypothesisRecord).filter_by(id=hid).first()
        assert record is not None
        assert record.metadata_json == {"foo": "bar"}
    finally:
        new_db.close()

