from proposals.engine import generate_proposals, list_proposals, DEFAULT_PROPOSALS


def test_low_karma_filtered():
    user = {"karma": 10, "is_certified": True}
    universe_state = {"entropy": 0.5, "popularity": 0.8}

    proposals = generate_proposals(user, universe_state, min_karma=50)

    assert proposals == []


def test_high_karma_receives_proposals():
    user = {"karma": 100, "is_certified": True}
    universe_state = {"entropy": 1.2, "popularity": 0.9}

    proposals = generate_proposals(
        user,
        universe_state,
        min_karma=50,
        requires_certification=True,
        universe_metadata={"id": "u1"},
    )

    assert len(proposals) == len(DEFAULT_PROPOSALS)
    for p in proposals:
        assert p["urgency"] in {"high", "low"}
        assert "popularity" in p and "entropy" in p
        assert p.get("universe") == {"id": "u1"}


def test_list_low_karma_filtered():
    user = {"karma": 5}
    state = {"entropy": 0.2, "popularity": 0.3}

    assert list_proposals(user, state, min_karma=50) == []


def test_list_high_karma_receives_proposals():
    user = {"karma": 80}
    state = {"entropy": 1.5, "popularity": 0.7}

    proposals = list_proposals(
        user,
        state,
        min_karma=50,
        universe_metadata={"id": "u2"},
    )

    assert len(proposals) == len(DEFAULT_PROPOSALS)
    for p in proposals:
        assert p["urgency"] in {"high", "low"}
        assert "popularity" in p and "entropy" in p
        assert p.get("universe") == {"id": "u2"}
