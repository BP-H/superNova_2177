# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
import types
import pytest

from frontend_bridge import dispatch_route
import scientific_metrics.ui_hook as sm_ui_hook


class DummyManager:
    def __init__(self):
        self.events = []

    async def trigger(self, name, payload):
        self.events.append((name, payload))


@pytest.mark.asyncio
async def test_predict_user_interactions_route(monkeypatch):
    dummy = DummyManager()
    monkeypatch.setattr(sm_ui_hook, "ui_hook_manager", dummy, raising=False)

    called = {}

    def fake_predict(uid, db, window):
        called["args"] = (uid, db, window)
        return {
            "predictions": {
                "will_create_content": {"probability": 0.1},
                "will_like_posts": {"probability": 0.2},
                "will_follow_users": {"probability": 0.3},
            }
        }

    monkeypatch.setattr(sm_ui_hook, "predict_user_interactions", fake_predict)

    result = await dispatch_route(
        "predict_user_interactions",
        {"user_id": 7, "prediction_window_hours": 12},
        db="dbsession",
    )

    expected = {
        "user_id": 7,
        "predictions": {
            "will_create_content": 0.1,
            "will_like_posts": 0.2,
            "will_follow_users": 0.3,
        },
    }
    assert result == expected
    assert called["args"] == (7, "dbsession", 12)
    assert dummy.events == [("user_interaction_prediction", expected)]


@pytest.mark.asyncio
async def test_calculate_influence_route(monkeypatch):
    dummy = DummyManager()
    monkeypatch.setattr(sm_ui_hook, "ui_hook_manager", dummy, raising=False)

    def fake_build(db):
        return types.SimpleNamespace(graph="g")

    def fake_calc(graph, uid, iterations=10):
        assert graph == "g"
        return {"value": 0.6}

    monkeypatch.setattr(sm_ui_hook, "build_causal_graph", fake_build)
    monkeypatch.setattr(sm_ui_hook, "calculate_influence_score", fake_calc)

    result = await dispatch_route("calculate_influence", {"user_id": 3}, db="db")

    expected = {"user_id": 3, "influence_score": 0.6}
    assert result == expected
    assert dummy.events == [("influence_score_computed", expected)]
