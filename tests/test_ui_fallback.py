# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
import importlib
import sys
import types


def test_ui_defaults_to_dev_secrets(monkeypatch):
    """Importing ui without ``st.secrets`` should use dev configuration."""
    # Stub the streamlit module so accessing ``st.secrets`` raises an error
    stub = types.ModuleType("streamlit")

    def __getattr__(name):
        if name == "secrets":
            raise RuntimeError("no secrets")
        return lambda *a, **k: None

    stub.__getattr__ = __getattr__
    monkeypatch.setitem(sys.modules, "streamlit", stub)

    # Provide a minimal matplotlib stub for the import in ui
    mpl = types.ModuleType("matplotlib")
    plt = types.ModuleType("matplotlib.pyplot")
    mpl.pyplot = plt
    monkeypatch.setitem(sys.modules, "matplotlib", mpl)
    monkeypatch.setitem(sys.modules, "matplotlib.pyplot", plt)

    ui = importlib.import_module("ui")
    importlib.reload(ui)
    assert ui.st_secrets == {
        "SECRET_KEY": "dev",
        "DATABASE_URL": "sqlite:///:memory:",
    }

