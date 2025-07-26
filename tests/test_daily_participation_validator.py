import datetime
from validators.daily_participation_validator import evaluate_daily_participation


def test_inactive_users_flagged():
    now = datetime.datetime(2025, 1, 5, 12, 0, 0)
    logs = [
        {"user_id": "u1", "timestamp": (now - datetime.timedelta(days=1)).isoformat()},
        {"user_id": "u2", "timestamp": (now - datetime.timedelta(days=4)).isoformat()},
    ]

    result = evaluate_daily_participation(logs, inactivity_days=2, current_time=now)
    assert "u2" in result["inactive_users"]
    assert "u1" not in result["inactive_users"]


def test_no_inactive_users():
    now = datetime.datetime(2025, 1, 5, 12, 0, 0)
    logs = [
        {"user_id": "u1", "timestamp": (now - datetime.timedelta(days=0)).isoformat()},
        {"user_id": "u2", "timestamp": (now - datetime.timedelta(days=1)).isoformat()},
    ]

    result = evaluate_daily_participation(logs, inactivity_days=2, current_time=now)
    assert result["inactive_users"] == []
