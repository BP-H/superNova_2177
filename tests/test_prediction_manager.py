from prediction_manager import PredictionManager
from db_models import SessionLocal, init_db, Base, engine


def test_prediction_lifecycle(tmp_path):
    # ensure tables exist
    init_db()
    manager = PredictionManager(session_factory=SessionLocal)

    data = {"foo": 1, "status": "created"}
    pid = manager.store_prediction(data)
    record = manager.get_prediction(pid)

    assert record["prediction_id"] == pid
    assert record["data"]["foo"] == 1
    assert record["status"] == "created"

    manager.update_prediction_status(pid, "done", {"res": 2})
    updated = manager.get_prediction(pid)
    assert updated["status"] == "done"
    assert updated["actual_outcome"]["res"] == 2

    exp_id = manager.store_experiment_design({"name": "exp"})
    exp = manager.get_experiment_design(exp_id)
    assert exp["experiment_id"] == exp_id
    assert exp["data"]["name"] == "exp"

    # cleanup
    Base.metadata.drop_all(bind=engine)
