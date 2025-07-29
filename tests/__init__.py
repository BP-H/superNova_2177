# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
"""Test suite package configuration."""

import importlib.util

# Automatically register the async fallback plugin so that async tests run even
# when ``pytest-asyncio`` is not installed.  When the real plugin is available
# we avoid loading the fallback entirely to prevent any interference.
if importlib.util.find_spec("pytest_asyncio") is None:
    pytest_plugins = ["tests.async_fallback"]
else:  # pragma: no cover - nothing to load when pytest-asyncio is present
    pytest_plugins = []

