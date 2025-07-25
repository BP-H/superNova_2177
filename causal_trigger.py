from typing import Optional
from sqlalchemy.orm import Session
import logging
import datetime
import json

from db_models import LogEntry, HypothesisRecord
from causal_graph import InfluenceGraph
from audit_explainer import trace_causal_chain
from governance_reviewer import evaluate_governance_risks, apply_governance_actions

logger = logging.getLogger("superNova_2177.trigger")


def safe_json_loads(json_str: str, default=None):
    try:
        return json.loads(json_str) if json_str else (default or {})
    except (json.JSONDecodeError, TypeError):
        logger.exception(f"JSON decode failed: {json_str}")
        return default or {}


def safe_db_query(db, model, id_field, fallback=None):
    try:
        result = db.query(model).filter_by(**{id_field[0]: id_field[1]}).first()
        return result if result else fallback
    except Exception:
        logger.exception(f"DB query failed for {model}")
        return fallback

def trigger_causal_audit(
    db: Session,
    log_id: Optional[int],
    graph: InfluenceGraph,
    hypothesis_id: Optional[str] = None,
    skip_commentary: bool = False,
    skip_validation: bool = False,
) -> dict:
    """
    Perform a causal audit on a given LogEntry and hypothesis (if provided),
    trace the causal chain using the graph, and return an audit summary.
    Includes governance enforcement if a hypothesis is linked.

    Args:
        db: Active SQLAlchemy session
        log_id: ID of the LogEntry to audit
        graph: InfluenceGraph object
        hypothesis_id: Optional hypothesis ID tied to the audit
        skip_commentary: If True, skip adding commentary
        skip_validation: If True, skip validation steps

    Returns:
        dict: audit summary report
    """
    audit_summary = {
        "log_id": log_id,
        "hypothesis_id": hypothesis_id,
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "causal_chain": [],
        "governance_review": {},
        "commentary": None,
    }

    if log_id is None:
        logger.warning("No log_id provided to trigger_causal_audit.")
        return {"error": "Missing log_id"}

    log_entry = safe_db_query(db, LogEntry, ("id", log_id))
    if not log_entry:
        logger.warning(f"LogEntry {log_id} not found.")
        return {"error": f"LogEntry {log_id} not found"}

    try:
        chain = trace_causal_chain(log_id, db, graph)
        audit_summary["causal_chain"] = chain
    except Exception as e:
        logger.exception("Causal chain tracing failed")
        audit_summary["causal_chain_error"] = str(e)

    hypothesis_record = None
    if hypothesis_id:
        hypothesis_record = safe_db_query(db, HypothesisRecord, ("id", hypothesis_id))
        if not hypothesis_record:
            logger.warning(f"Hypothesis {hypothesis_id} not found.")
            audit_summary["governance_review"] = {"error": f"Hypothesis {hypothesis_id} not found"}
        else:
            try:
                gov_result = evaluate_governance_risks(hypothesis_record, db, graph=graph)
                audit_summary["governance_review"] = gov_result

                score = gov_result.get("overall_compliance_score")
                if score is not None:
                    logger.info(f"Governance score for {hypothesis_id}: {score}")

                if gov_result["auto_actions_taken"]:
                    apply_governance_actions(hypothesis_record, gov_result["auto_actions_taken"], db)
                    logger.info(f"Governance actions applied: {gov_result['auto_actions_taken']}")
            except Exception as ge:
                logger.exception("Governance review failed")
                audit_summary["governance_review"] = {"error": str(ge)}

    return audit_summary
