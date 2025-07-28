import sys
import types
from pathlib import Path

sys.modules.setdefault("streamlit", types.ModuleType("streamlit"))
sys.modules.setdefault("matplotlib", types.ModuleType("matplotlib"))
sys.modules.setdefault("matplotlib.pyplot", types.ModuleType("pyplot"))

from ui import parse_rfcs, summarize_text


def test_summarize_text_word_limit():
    text = " ".join(str(i) for i in range(10))
    assert summarize_text(text, word_limit=5) == "0 1 2 3 4..."
    assert summarize_text(text, word_limit=20) == text


def test_parse_rfcs_basic(tmp_path, monkeypatch):
    rfc_dir = tmp_path / "rfcs"
    rfc_dir.mkdir()
    content = (
        "# Example RFC\n"
        + " ".join([f"word{i}" for i in range(50)])
        + "\n\n## Section\nMore"
    )
    (rfc_dir / "rfc1.md").write_text(content)
    (rfc_dir / "TEMPLATE.md").write_text("# Template")
    monkeypatch.chdir(tmp_path)
    rfcs = parse_rfcs()
    assert len(rfcs) == 1
    item = rfcs[0]
    assert item["title"] == "Example RFC"
    assert item["path"].name == "rfc1.md"
    assert item["summary"].endswith("...")
    assert len(item["summary"].split()) <= 41
    assert item["entropy"] > 0
