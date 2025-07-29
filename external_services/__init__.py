# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
"""Plug-and-play modules for external AI services."""

from .llm_client import LLMClient, get_speculative_futures
from .video_client import VideoClient, generate_video_preview
from .vision_client import VisionClient, analyze_timeline

__all__ = [
    "LLMClient",
    "VideoClient",
    "VisionClient",
    "get_speculative_futures",
    "generate_video_preview",
    "analyze_timeline",
]
