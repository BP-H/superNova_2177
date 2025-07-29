# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
import importlib
import sys
import types


def load_utils(monkeypatch):
    """Reload ui_utils with a stubbed streamlit.cache_data."""
    stub = types.ModuleType("streamlit")

    def cache_data(func=None, **kwargs):
        def decorator(fn):
            cache = {}

            def wrapper(*args, **kw):
                key = (tuple(args), tuple(sorted(kw.items())))
                if key not in cache:
                    wrapper.call_count += 1
                    cache[key] = fn(*args, **kw)
                return cache[key]

            wrapper.call_count = 0
            return wrapper

        if func is not None:
            return decorator(func)
        return decorator

    stub.cache_data = cache_data
    monkeypatch.setitem(sys.modules, "streamlit", stub)

    if "ui_utils" in sys.modules:
        del sys.modules["ui_utils"]
    return importlib.import_module("ui_utils")


def test_load_rfc_entries_caching(monkeypatch, tmp_path):
    ui_utils = load_utils(monkeypatch)
    rfc_dir = tmp_path / "rfcs"
    rfc_dir.mkdir()
    rfc_file = rfc_dir / "rfc-1.md"
    rfc_file.write_text("# RFC 1\n\n## Summary\nInitial")

    first = ui_utils.load_rfc_entries(rfc_dir)
    second = ui_utils.load_rfc_entries(rfc_dir)
    assert first == second  # nosec B101
    assert ui_utils.load_rfc_entries.call_count == 1  # nosec B101

    # modify file to invalidate cache
    rfc_file.write_text("# RFC 1\n\n## Summary\nChanged")
    third = ui_utils.load_rfc_entries(rfc_dir)
    assert third[0][0]["summary"] != first[0][0]["summary"]  # nosec B101
    assert ui_utils.load_rfc_entries.call_count == 2  # nosec B101
