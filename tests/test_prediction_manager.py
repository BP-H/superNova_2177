import datetime
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


def test_annual_audit_scheduler(monkeypatch):
    init_db()
    manager = PredictionManager(session_factory=SessionLocal)

    called = {}

    class DummyQC:
        def quantum_prediction_engine(self, _ids):
            called["ok"] = True
            return {"overall_quantum_coherence": 0.5}

    monkeypatch.setattr(
        "prediction_manager.QuantumContext", lambda: DummyQC()
    )

    start = datetime.datetime(2020, 1, 1)

    pid1 = manager.schedule_annual_audit_proposal(current_time=start)
    assert pid1 is not None
    assert called.get("ok")

    # within same year -> None
    assert (
        manager.schedule_annual_audit_proposal(
            current_time=start + datetime.timedelta(days=100)
        )
        is None
    )

    pid2 = manager.schedule_annual_audit_proposal(
        current_time=start + datetime.timedelta(days=366)
    )
    assert pid2 is not None and pid2 != pid1
    Base.metadata.drop_all(bind=engine)
