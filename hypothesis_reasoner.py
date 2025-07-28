# hypothesis_reasoner.py — Scientific Judgment Layer (superNova_2177 v3.8)
"""
This module serves as the "analytical cortex" of the superNova_2177 system,
implementing functions to rank, compare, and synthesize hypotheses. It simulates
aspects of scientific judgment by reasoning over stored hypotheses based on
evidence strength, conflicting predictions, and entropy deltas.
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
import math
import itertools # For combinations in conflict detection
import textwrap # Added for text summarization
import logging

logger = logging.getLogger(__name__)
logger.propagate = False
from sqlalchemy.orm import Session
from sqlalchemy import func, select

# Assuming these modules are available in the same directory or Python path
from db_models import SystemState # For accessing hypothesis records
import hypothesis_tracker as ht # For retrieving and updating hypothesis records

# --- Configuration Placeholder ---
# In a real scenario, this would come from a central Config object (e.g., superNova_2177.Config)
# For scaffolding, we define it here for clarity.
class TempConfig:
    HYPOTHESIS_STALENESS_THRESHOLD_DAYS = 30
    TEXT_SIMILARITY_THRESHOLD = 0.7 # For detecting conflicting hypotheses (Levenshtein/keyword)

# Try to import actual Config if available, otherwise use TempConfig
try:
    from config import Config as SystemConfig
    CONFIG = SystemConfig
except ImportError:
    CONFIG = TempConfig


def _get_all_hypotheses(db: Session) -> List[Dict[str, Any]]:
    """Helper to retrieve all hypothesis records from SystemState."""
    stmt = select(SystemState).where(
        SystemState.key.like("hypothesis_HYP_%")  # Assuming prefix from hypothesis_tracker
    )
    rows = db.execute(stmt).scalars().all()
    parsed_hypotheses = []
    for entry in rows:
        try:
            parsed_hypotheses.append(json.loads(entry.value))
        except json.JSONDecodeError:
            # Log error for malformed entry, but continue
            logger.warning(
                "Warning: Malformed hypothesis record found for key: %s",
                entry.key,
            )
            continue
    return parsed_hypotheses


def _calculate_hypothesis_trend(history: List[Dict[str, Any]]) -> str:
    """Determine the trend of a hypothesis score based on its history."""
    if len(history) < 2:
        return "stable"
    
    # Sort history by timestamp to ensure correct order
    sorted_history = sorted(history, key=lambda x: x.get("t", ""))
    
    initial_score = sorted_history[0].get("score", 0.0)
    final_score = sorted_history[-1].get("score", 0.0)

    if final_score > initial_score:
        return "increasing"
    elif final_score < initial_score:
        return "declining"
    else:
        return "stable"


def _get_confidence_band(score: float) -> str:
    """Categorize score into high/medium/low confidence band."""
    if score >= 0.8:
        return "high"
    elif score >= 0.5:
        return "medium"
    else:
        return "low"


def _levenshtein_distance_normalized(s1: str, s2: str) -> float:
    """Calculate normalized Levenshtein distance (0.0 to 1.0, 1.0 being identical)."""
    if not s1 and not s2: return 1.0
    if not s1 or not s2: return 0.0
    
    # Basic normalization: lowercase and remove non-alphanumeric (except spaces)
    s1_norm = "".join(filter(str.isalnum, s1.lower()))
    s2_norm = "".join(filter(str.isalnum, s2.lower()))
    
    if not s1_norm and not s2_norm: return 1.0 # Both empty after norm
    if not s1_norm or not s2_norm: return 0.0 # One empty after norm

    rows = len(s1_norm) + 1
    cols = len(s2_norm) + 1
    
    dist = [[0 for x in range(cols)] for x in range(rows)]
    for i in range(1, rows):
        dist[i][0] = i
    for i in range(1, cols):
        dist[0][i] = i

    for col in range(1, cols):
        for row in range(1, rows):
            cost = 0 if s1_norm[row-1] == s2_norm[col-1] else 1
            dist[row][col] = min(dist[row-1][col] + 1,      # Deletion
                                 dist[row][col-1] + 1,      # Insertion
                                 dist[row-1][col-1] + cost) # Substitution
    
    max_len = max(len(s1_norm), len(s2_norm))
    return 1.0 - (dist[rows-1][cols-1] / max_len) if max_len > 0 else 1.0


def rank_hypotheses_by_confidence(db: Session, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Ranks all registered hypotheses based on their scientific confidence.
    Prioritizes status, then score, then trend.
    """
    all_hypotheses = _get_all_hypotheses(db)

    status_priority = {"validated": 4, "open": 3, "inconclusive": 2, "falsified": 1, "merged": 0} # Added 'merged' status
    trend_priority = {"increasing": 3, "stable": 2, "declining": 1, "unknown": 0}

    ranked_hypotheses = []
    for hyp in all_hypotheses:
        current_status = hyp.get("status", "open")
        current_score = hyp.get("score", 0.0)
        current_trend = _calculate_hypothesis_trend(hyp.get("history", []))

        # Create a sortable key
        sort_key = (
            status_priority.get(current_status, 0), # Primary sort: status
            current_score,                          # Secondary sort: score (descending implicitly by multiplying -1 if needed, but here simple > means higher score is better)
            trend_priority.get(current_trend, 0)    # Tertiary sort: trend
        )
        
        ranked_hypotheses.append({
            "hypothesis": hyp,
            "sort_key": sort_key,
            "metadata": {
                "hypothesis_id": hyp.get("hypothesis_id"),
                "text_preview": hyp.get("text", "")[:100],
                "score": current_score,
                "status": current_status,
                "trend": current_trend,
                "confidence_band": _get_confidence_band(current_score),
            }
        })

    # Sort in descending order of confidence
    ranked_hypotheses.sort(key=lambda x: x["sort_key"], reverse=True)

    return [h["metadata"] for h in ranked_hypotheses[:top_k]]


def detect_conflicting_hypotheses(db: Session) -> List[Tuple[str, str]]:
    """
    Compares texts and nodes of all open hypotheses to flag conflicting pairs.
    Conflict is flagged when:
    - Textual similarity exceeds a threshold (initially: normalized Levenshtein distance)
    - But scores or evidence (supporting_nodes, validation_log_ids) differ significantly.
    """
    all_hypotheses = _get_all_hypotheses(db)
    conflicting_pairs = []

    open_hypotheses = [h for h in all_hypotheses if h.get("status") == "open"]

    # Iterate through all unique pairs of open hypotheses
    for hyp1, hyp2 in itertools.combinations(open_hypotheses, 2):
        text1 = hyp1.get("text", "")
        text2 = hyp2.get("text", "")

        # Check textual similarity
        similarity = _levenshtein_distance_normalized(text1, text2)
        
        if similarity >= CONFIG.TEXT_SIMILARITY_THRESHOLD:
            # Check for diverging evidence/scores for similar texts
            score1 = hyp1.get("score", 0.0)
            score2 = hyp2.get("score", 0.0)
            
            # Simple check for significant score difference (e.g., > 0.3 on a 0-1 scale)
            if abs(score1 - score2) > 0.3:
                conflicting_pairs.append((hyp1["hypothesis_id"], hyp2["hypothesis_id"]))
                continue
            
            # Check for diverging supporting evidence (nodes)
            nodes1 = set(hyp1.get("supporting_nodes", []))
            nodes2 = set(hyp2.get("supporting_nodes", []))
            
            # If texts are similar but supporting nodes are largely disjoint
            # Use a slightly lower threshold for nodes if text is very similar
            if similarity > 0.8 and len(nodes1.intersection(nodes2)) / max(len(nodes1), len(nodes2), 1) < 0.2:
                 conflicting_pairs.append((hyp1["hypothesis_id"], hyp2["hypothesis_id"]))
                 continue
            
            # Further checks on validation_log_ids or prediction differences can be added here
            # For v3.8, keep it focused on score and nodes.

    return conflicting_pairs


def synthesize_consensus_hypothesis(hypothesis_ids: List[str], db: Session) -> str:
    """
    Fuses 2+ validated hypotheses into a new "consensus hypothesis."
    Generates a new HYP_ record with a summary note indicating inheritance.
    """
    source_hypotheses = []
    for hyp_id in hypothesis_ids:
        hyp = ht._get_hypothesis_record(db, hyp_id)
        if not hyp:
            raise ValueError(f"Source hypothesis {hyp_id} not found.")
        source_hypotheses.append(hyp)

    if not source_hypotheses:
        raise ValueError("No valid source hypotheses provided for synthesis.")

    # Fusion Logic:
    fused_text_parts = []
    fused_supporting_nodes = set()
    fused_validation_log_ids = set()
    fused_audit_sources = set()
    total_score = 0.0
    all_validated = True

    for hyp in source_hypotheses:
        fused_text_parts.append(hyp.get("text", ""))
        fused_supporting_nodes.update(hyp.get("supporting_nodes", []))
        fused_validation_log_ids.update(hyp.get("validation_log_ids", []))
        fused_audit_sources.update(hyp.get("audit_sources", []))
        total_score += hyp.get("score", 0.0)
        if hyp.get("status") != "validated":
            all_validated = False

    # Heuristic summarization for text using textwrap.shorten
    source_texts = [textwrap.shorten(h.get("text", ""), width=100, placeholder="...") for h in source_hypotheses]
    fused_text_base = f"Consensus derived from: {'; '.join(source_texts)}"
    fused_text = textwrap.shorten(fused_text_base, width=500, placeholder="...")


    new_score = total_score / len(source_hypotheses)
    new_status = "validated" if all_validated else "inconclusive"

    # Create new hypothesis record using hypothesis_tracker's register function
    new_hypothesis_id = ht.register_hypothesis(fused_text, db)
    new_hypothesis_record = ht._get_hypothesis_record(db, new_hypothesis_id) # Retrieve the fresh record

    new_hypothesis_record["supporting_nodes"] = list(fused_supporting_nodes)
    new_hypothesis_record["validation_log_ids"] = list(fused_validation_log_ids)
    new_hypothesis_record["audit_sources"] = list(fused_audit_sources)
    new_hypothesis_record["score"] = new_score
    new_hypothesis_record["status"] = new_status
    new_hypothesis_record["notes"].append(
        f"Synthesized from hypotheses: {', '.join(hypothesis_ids)} with fusion logic: text concatenation/averaging."
    )
    # Add explicit merged_from field for traceability
    new_hypothesis_record["merged_from"] = hypothesis_ids 
    
    # Update history for this new record
    new_hypothesis_record["history"].append({
        "t": datetime.utcnow().isoformat(),
        "score": new_score,
        "status": new_status,
        "reason": "Synthesis"
    })

    if not ht._save_hypothesis_record(db, new_hypothesis_record):
        raise RuntimeError("Failed to save synthesized hypothesis.")

    # Optionally, mark original hypotheses as 'merged'
    for hyp_id in hypothesis_ids:
        original_hyp = ht._get_hypothesis_record(db, hyp_id)
        if original_hyp and original_hyp.get("status") in ["open", "validated"]: # Only update if not already falsified/inconclusive
            original_hyp["status"] = "merged"
            original_hyp["notes"].append(f"Merged into consensus hypothesis: {new_hypothesis_id}")
            ht._save_hypothesis_record(db, original_hyp)

    return new_hypothesis_id


def auto_flag_stale_or_redundant(db: Session) -> List[str]:
    """
    Identifies open hypotheses that:
    - Have not changed score or status in Config.HYPOTHESIS_STALENESS_THRESHOLD_DAYS
    - OR are semantically identical to a validated one.
    Flags them as "inconclusive" with a note.
    Returns list of affected hypothesis_ids.
    """
    all_hypotheses = _get_all_hypotheses(db)
    affected_hypothesis_ids = []
    
    now = datetime.utcnow()
    staleness_threshold_date = now - timedelta(days=CONFIG.HYPOTHESIS_STALENESS_THRESHOLD_DAYS)

    validated_hypotheses = [h for h in all_hypotheses if h.get("status") == "validated"]

    for hyp in all_hypotheses:
        hyp_id = hyp.get("hypothesis_id")
        if not hyp_id or hyp.get("status") != "open":
            continue # Only process open hypotheses

        # Check for staleness
        last_history_entry = sorted(hyp.get("history", []), key=lambda x: x.get("t", ""))[-1] if hyp.get("history") else None
        last_update_str = last_history_entry.get("t") if last_history_entry else hyp.get("created_at")
        
        last_update_dt = None
        if last_update_str:
            try:
                last_update_dt = datetime.fromisoformat(last_update_str)
            except ValueError:
                logger.warning(
                    f"Invalid timestamp for hypothesis {hyp_id}: {last_update_str}"
                )

        if last_update_dt and last_update_dt < staleness_threshold_date:
            hyp["status"] = "inconclusive"
            hyp["notes"].append(f"[{now.isoformat()}] Flagged as stale: No update in {CONFIG.HYPOTHESIS_STALENESS_THRESHOLD_DAYS} days.")
            ht._save_hypothesis_record(db, hyp)
            affected_hypothesis_ids.append(hyp_id)
            continue # Move to next hypothesis after flagging as stale

        # Check for redundancy against validated hypotheses
        hyp_text = hyp.get("text", "")
        is_redundant = False
        for validated_hyp in validated_hypotheses:
            validated_text = validated_hyp.get("text", "")
            similarity = _levenshtein_distance_normalized(hyp_text, validated_text)
            if similarity >= CONFIG.TEXT_SIMILARITY_THRESHOLD: # Using same threshold for conflict and redundancy
                is_redundant = True
                break
        
        if is_redundant:
            hyp["status"] = "redundant" # New status: "redundant"
            hyp["notes"].append(f"[{now.isoformat()}] Flagged as redundant: Semantically similar to an already validated hypothesis.")
            ht._save_hypothesis_record(db, hyp)
            affected_hypothesis_ids.append(hyp_id)
            continue
            
    return affected_hypothesis_ids
