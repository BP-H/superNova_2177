from proposals.engine import generate_proposals, DEFAULT_PROPOSALS


def test_low_karma_filtered():
    user = {"karma": 5, "is_certified": True}
    state = {"entropy": 0.2, "popularity": 0.3}
    assert generate_proposals(user, state, min_karma=50) == []


def test_high_karma_receives_proposals():
    user = {"karma": 200, "is_certified": True}
    state = {"entropy": 1.1, "popularity": 0.8}
    proposals = generate_proposals(user, state, min_karma=50, requires_certification=True)
    assert len(proposals) == len(DEFAULT_PROPOSALS)
    for p in proposals:
        assert p["urgency"] in {"high", "low"}
        assert "popularity" in p and "entropy" in p
