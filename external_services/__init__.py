# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
"""Plug-and-play modules for external AI services."""

from .llm_client import get_speculative_futures
from .vision_client import analyze_image
from .video_client import generate_video_preview
__all__ = ["get_speculative_futures", "generate_video_preview", "analyze_image"]
