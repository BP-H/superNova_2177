# auditor_report_formatter.py — Report & Export Formatter for Audit Narratives (v3.9)
"""
This module transforms introspective outputs from `audit_explainer.py`
into structured report formats for external consumption. It acts as the
presentation/export layer for scientific audits, converting the system’s
internal reasoning into formats suitable for logs, markdown summaries,
or future PDF/export integration.

v3.9 constraint: no external rendering libraries, no LLM use, no file I/O.
All output is returned as strings or dictionaries, ready for logging,
display, or structured export.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime # Added datetime import for timestamping


def render_plain_text_report(explainer_output: Dict[str, Any]) -> str:
    """
    Converts a hypothesis audit explanation into a plain-text string.

    Args:
        explainer_output (Dict[str, Any]): Output from explain_validation_reasoning().

    Returns:
        str: A multi-line plain-text report.
    """
    summary = explainer_output.get("summary", "No summary available.")
    reasoning = explainer_output.get("reasoning", [])
    nodes = explainer_output.get("supporting_nodes", [])
    flags = explainer_output.get("risk_flags", [])

    text = []
    text.append("=== Hypothesis Audit Report ===")
    text.append("")
    text.append(f"Summary: {summary}")
    text.append("")
    if reasoning:
        text.append("Reasoning:")
        for r in reasoning:
            text.append(f"- {r}")
        text.append("") # Add a blank line after reasoning if present
    if nodes:
        text.append("Supporting Nodes:")
        text.append(f"  {', '.join(nodes)}")
        text.append("") # Add a blank line after nodes if present
    if flags:
        text.append("Risk Flags:")
        text.append(f"  {', '.join(flags)}")
        text.append("") # Add a blank line after flags if present

    return "\n".join(text).strip() # .strip() to remove trailing newlines if lists are empty


def render_markdown_report(
    explainer_output: Dict[str, Any],
    hypothesis_id: str,
    hypothesis_text_preview: str,
    validation_id: Optional[int] = None,
    bias_summary_text: Optional[str] = None, # Added for inclusion
) -> str:
    """
    Converts a hypothesis audit explanation into a Markdown report.

    Args:
        explainer_output (Dict[str, Any]): Output from explain_validation_reasoning().
        hypothesis_id (str): The ID of the hypothesis being explained.
        hypothesis_text_preview (str): A preview of the hypothesis's original text.
        validation_id (Optional[int]): The specific validation event ID, if any.
        bias_summary_text (Optional[str]): A summary of biases impacting the hypothesis.

    Returns:
        str: Markdown-formatted audit report.
    """
    summary = explainer_output.get("summary", "No summary available.")
    reasoning = explainer_output.get("reasoning", [])
    nodes = explainer_output.get("supporting_nodes", [])
    flags = explainer_output.get("risk_flags", [])

    title_suffix = f" (Validation Log #{validation_id})" if validation_id else ""
    title = f"# Hypothesis Audit Report: `{hypothesis_id}`{title_suffix}"

    md = []
    md.append(title)
    md.append("")
    md.append(f"**Hypothesis:** `{hypothesis_text_preview}`")
    md.append("")
    md.append(f"**Summary:** {summary}")
    md.append("")
    
    if reasoning:
        md.append("## Reasoning")
        md.append("---") # Consistent header separator
        for r in reasoning:
            md.append(f"- {r}")
        md.append("") # Add a blank line after reasoning if present
    
    if nodes:
        md.append("## Supporting Nodes")
        md.append("---") # Consistent header separator
        md.append(", ".join(nodes))
        md.append("") # Add a blank line after nodes if present
    
    if flags:
        md.append("## Risk Flags")
        md.append("---") # Consistent header separator
        md.append(", ".join(flags))
        md.append("") # Add a blank line after flags if present

    if bias_summary_text and bias_summary_text != "No bias summary available.": # Only include if meaningful
        md.append("## Bias Impact Summary")
        md.append("---") # Consistent header separator
        md.append(bias_summary_text)
        md.append("") # Add a blank line after bias summary if present

    return "\n".join(md).strip()


def format_bias_summary(bias_data: Dict[str, Any]) -> str:
    """
    Formats the bias analysis output into a compact summary string.

    Args:
        bias_data (Dict[str, Any]): Output from summarize_bias_impact_on().

    Returns:
        str: Formatted bias summary.
    """
    return bias_data.get("summary", "No bias summary available.")


def generate_structured_audit_bundle(
    explainer_output: Dict[str, Any],
    bias_data: Dict[str, Any],
    causal_chain_data: Optional[List[Dict[str, Any]]],
    hypothesis_id: str,
    hypothesis_text_preview: str,
    validation_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Bundles formatted artifacts into a structured dictionary.

    Args:
        explainer_output (Dict[str, Any]): Output from explain_validation_reasoning().
        bias_data (Dict[str, Any]): Output from summarize_bias_impact_on().
        causal_chain_data (Optional[List[Dict[str, Any]]]): Output from trace_causal_chain().
        hypothesis_id (str): The ID of the hypothesis.
        hypothesis_text_preview (str): A preview of the hypothesis's original text.
        validation_id (Optional[int]): ID of the validation log, if any.

    Returns:
        Dict[str, Any]: A bundled artifact dictionary for logging or export.
    """
    bias_summary_text = format_bias_summary(bias_data) # Generate bias summary once

    return {
        "hypothesis_id": hypothesis_id,
        "validation_id": validation_id,
        "summary": explainer_output.get("summary", "N/A"), # Added default value
        "markdown_report": render_markdown_report(
            explainer_output,
            hypothesis_id,
            hypothesis_text_preview,
            validation_id,
            bias_summary_text,
        ),
        "plain_text_report": render_plain_text_report(explainer_output),
        "risk_flags": explainer_output.get("risk_flags", []),
        "bias_summary": bias_summary_text,
        "causal_trace": causal_chain_data or [],
        "timestamp": datetime.utcnow().isoformat(), # Add timestamp to bundle
    }
