# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
"""Import and UI tests for Transcendental Resonance pages."""

import pytest
import streamlit.testing.v1 as st_test


def _run_page(module_name: str) -> None:
    """Import and run a Streamlit page using AppTest."""
    script = f"import {module_name} as m\nm.main()"
    app = st_test.AppTest.from_string(script)
    app.run()
    assert not app.exception  # nosec B101


def test_import_ideas_page():
    _run_page("transcendental_resonance_frontend.pages.ideas")


def test_import_video_page():
    _run_page("transcendental_resonance_frontend.pages.video")


@pytest.mark.asyncio
async def test_video_client_offline(monkeypatch):
    monkeypatch.setenv("OFFLINE_MODE", "1")
    from external_services.video_client import VideoClient

    client = VideoClient()
    result = await client.generate_video_preview("test")
    assert "placeholder" in result["video_url"]  # nosec B101
