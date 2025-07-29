import pytest
from transcendental_resonance_frontend.src.quantum_futures import (
    generate_speculative_futures,
    generate_speculative_payload,
    DISCLAIMER,
)


@pytest.mark.asyncio
async def test_quantum_futures_offline(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.delenv("VIDEO_API_KEY", raising=False)
    monkeypatch.delenv("VISION_API_KEY", raising=False)

    futures = await generate_speculative_futures({"description": "warp"}, num_variants=1)
    assert futures and "Offline Mode" in futures[0]["text"]

    payload = await generate_speculative_payload("warp")
    assert payload and payload[0]["video_url"].endswith("placeholder.mp4")
    assert payload[0]["disclaimer"] == DISCLAIMER
