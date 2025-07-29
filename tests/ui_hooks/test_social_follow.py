# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
import pytest

from frontend_bridge import dispatch_route
import social.follow_ui_hook as follow_hook


class DummyUser:
    pass


class DummyDB:
    pass


@pytest.mark.asyncio
async def test_follow_user_route(monkeypatch):
    called = {}

    def fake_follow(username, db, current_user):
        called['args'] = (username, db, current_user)
        return {'message': 'Followed'}

    monkeypatch.setattr(follow_hook, 'follow_unfollow_user', fake_follow)

    db = DummyDB()
    user = DummyUser()
    payload = {'username': 'alice'}
    result = await dispatch_route('follow_user', payload, db=db, current_user=user)

    assert result == {'message': 'Followed'}
    assert called['args'] == ('alice', db, user)
