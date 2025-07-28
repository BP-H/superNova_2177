"""
Governance Reviewer (v3.9+)
Evaluates a HypothesisRecord for compliance with scientific, logical, and procedural rules.
Returns structured issues, enforcement decisions, and integrates with downstream audit tools.
"""

from db_models import HypothesisRecord
from sqlalchemy.orm import Session
from typing import Dict, List, Union, Optional
from causal_graph import InfluenceGraph
import logging
import networkx as nx  # Required for cycle detection

logger = logging.getLogger("superNova_2177.governance")
logger.propagate = False

# Configurable thresholds and rule toggles
class Config:
    ENTROPY_THRESHOLD = 0.15
    REQUIRE_VALIDATION_LOGS = True
    ENFORCE_CREATOR_METADATA = True
    ENABLE_CYCLE_DETECTION = True

def evaluate_governance_risks(
    hypothesis: HypothesisRecord, db: Session, graph: Optional[InfluenceGraph] = None
) -> Dict[str, Union[float, List[str], Dict[str, List[str]], bool]]:
    """
    Evaluate the hypothesis for policy compliance, risk, and governance enforcement.
    Returns a structured compliance bundle.

    Args:
        hypothesis: The hypothesis to evaluate.
        db: Database session.
        graph: Optional InfluenceGraph for loop detection.

    Returns:
        Dict containing compliance_score, actions, severity-tiered issues, and flags.
    """
    issues = {
        "critical_issues": [],
        "warning_issues": [],
        "info_issues": [],
    }
    auto_actions_taken = []
    requires_human_review = False
    score_penalty = 0.0

    metadata = hypothesis.metadata_json or {}
    text = (hypothesis.text or "").lower()

    # --- Metadata checks ---
    if Config.ENFORCE_CREATOR_METADATA and "creator" not in metadata:
        issues["critical_issues"].append("Missing creator metadata.")
        score_penalty += 0.1
    if "timestamp" not in metadata:
        issues["warning_issues"].append("Missing creation timestamp.")
        score_penalty += 0.05

    # --- Logic contradiction checks ---
    if "always true" in text and "cannot be proven" in text:
        issues["critical_issues"].append("Contradictory hypothesis phrasing.")
        score_penalty += 0.2
        requires_human_review = True

    # --- Validation logs ---
    validations = metadata.get("validations", [])
    if Config.REQUIRE_VALIDATION_LOGS and not validations:
        issues["warning_issues"].append("No validations attached.")
        score_penalty += 0.15

    # --- Audit entropy check ---
    last_audit = metadata.get("last_audit", {})
    deviation = last_audit.get("deviation", None)
    if deviation is not None and deviation > Config.ENTROPY_THRESHOLD:
        issues["critical_issues"].append(f"Deviation {deviation:.3f} exceeds threshold.")
        score_penalty += 0.2
        auto_actions_taken.append("flag_for_retraining")

    # --- Causal graph cycle check ---
    if Config.ENABLE_CYCLE_DETECTION and graph is not None:
        try:
            node_ids = metadata.get("causal_node_ids", [])
            subgraph = graph.graph.subgraph(node_ids)
            if not subgraph:
                issues["warning_issues"].append("Subgraph could not be formed from causal_node_ids.")
            elif not nx.is_directed_acyclic_graph(subgraph):
                issues["critical_issues"].append("Causal loop detected in hypothesis dependencies.")
                score_penalty += 0.25
                auto_actions_taken.append("quarantine_hypothesis")
                requires_human_review = True
        except Exception as e:
            logger.error(f"Causal graph check failed: {e}", exc_info=True)
            issues["warning_issues"].append("Causal graph analysis failed.")

    # --- Final score + escalations ---
    compliance_score = max(0.0, 1.0 - score_penalty)
    if compliance_score < 0.6:
        auto_actions_taken.append("auto_quarantine")
        requires_human_review = True

    logger.info(f"Governance review for {hypothesis.id} yielded score={compliance_score:.2f}, actions={auto_actions_taken}")

    return {
        "overall_compliance_score": round(compliance_score, 2),
        "auto_actions_taken": auto_actions_taken,
        "requires_human_review": requires_human_review,
        "issues": {k: v for k, v in issues.items() if v}
    }

def apply_governance_actions(hypothesis: HypothesisRecord, actions: List[str], db: Session) -> None:
    """
    Execute auto_actions_taken by updating the hypothesis or triggering escalations.

    Args:
        hypothesis: The record to act upon.
        actions: List of action codes.
        db: Active SQLAlchemy session.
    """
    for action in actions:
        if action in ("quarantine_hypothesis", "auto_quarantine"):
            hypothesis.status = "quarantined"  # Ensure 'quarantined' is a valid status in your model
            logger.warning(f"Hypothesis {hypothesis.id} quarantined due to governance violations.")
        elif action == "flag_for_retraining":
            hypothesis.metadata_json["retraining_required"] = True
            logger.info(f"Hypothesis {hypothesis.id} flagged for retraining.")
        elif action == "rollback_requested":
            hypothesis.metadata_json["rollback_flag"] = True
            logger.warning(f"Rollback flag set for hypothesis {hypothesis.id}.")
        else:
            logger.info(f"Action '{action}' logged for hypothesis {hypothesis.id} (no-op).")

    db.merge(hypothesis)
    db.commit()
