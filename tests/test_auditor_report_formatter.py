# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
import re
from auditor_report_formatter import generate_structured_audit_bundle


def test_generate_structured_audit_bundle_basic():
    explainer = {
        "summary": "All good",
        "reasoning": ["step1"],
        "supporting_nodes": ["n1"],
        "risk_flags": ["f1"]
    }
    bias = {"summary": "no major bias"}
    causal = [{"id": 1}]

    bundle = generate_structured_audit_bundle(
        explainer_output=explainer,
        bias_data=bias,
        causal_chain_data=causal,
        hypothesis_id="H1",
        hypothesis_text_preview="Example text",
        validation_id=7,
    )

    assert bundle["hypothesis_id"] == "H1"
    assert bundle["validation_id"] == 7
    assert bundle["summary"] == "All good"
    assert bundle["risk_flags"] == ["f1"]
    assert bundle["bias_summary"] == "no major bias"
    assert bundle["causal_trace"] == causal

    md = bundle["markdown_report"]
    assert "# Hypothesis Audit Report: `H1`" in md
    assert "## Bias Impact Summary" in md
    assert "no major bias" in md

    plain = bundle["plain_text_report"]
    assert "Summary: All good" in plain
    assert "Risk Flags:" in plain

    # timestamp should be ISO formatted
    assert re.match(r"\d{4}-\d{2}-\d{2}T", bundle["timestamp"])
