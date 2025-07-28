"""Test suite package configuration."""

# Automatically register the async fallback plugin so that async tests run
# even when ``pytest-asyncio`` is not installed.
# The plugin module lives inside this package, so use the fully qualified name.
pytest_plugins = ["tests.async_fallback"]

