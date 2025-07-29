# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
from datetime import datetime, timezone

from validators.daily_participation_validator import detect_inactive_users


def test_detect_inactive_users_flags_inactivity():
    now = datetime(2024, 1, 10, tzinfo=timezone.utc)
    logs = [
        {"user_id": "active", "timestamp": "2024-01-09T23:59:00Z"},
        {"user_id": "inactive", "timestamp": "2023-12-15T00:00:00Z"},
    ]
    result = detect_inactive_users(logs, threshold_days=20, current_time=now)
    assert result == ["inactive"]


def test_detect_inactive_users_respects_threshold():
    now = datetime(2024, 1, 10, tzinfo=timezone.utc)
    logs = [{"user_id": "u1", "timestamp": "2024-01-08T12:00:00Z"}]

    flagged = detect_inactive_users(logs, threshold_days=0, current_time=now)
    assert flagged == ["u1"]

    flagged = detect_inactive_users(logs, threshold_days=2, current_time=now)
    assert flagged == []


def test_detect_inactive_users_ignores_bad_logs():
    now = datetime(2024, 1, 10, tzinfo=timezone.utc)
    logs = [
        {"user_id": "a", "timestamp": "not-a-date"},
        {"user_id": "a", "timestamp": "2024-01-01T00:00:00Z"},
    ]
    result = detect_inactive_users(logs, threshold_days=5, current_time=now)
    assert result == ["a"]
