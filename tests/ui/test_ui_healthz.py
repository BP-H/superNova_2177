from pathlib import Path

import streamlit.testing.v1 as st_test


def test_ui_healthz_endpoint():
    """ui.py should respond to ?healthz=1 with plain 'ok'."""
    app = st_test.AppTest.from_file(str(Path("ui.py").resolve()))
    app.query_params["healthz"] = "1"
    app.run()
    assert not app.exception  # nosec B101
    assert app.markdown[0].body.strip().lower() == "ok"  # nosec B101
