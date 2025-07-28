# hypothesis_meta_evaluator.py — Scientific Meta-Reasoning Layer (v3.9)
"""
This module establishes a meta-evaluation layer that reflects on the system’s own
hypothesis judgment behavior. It identifies validation trends, potential reasoning
biases, judgment quality issues, and proposes heuristic improvements. This module
simulates a "scientific conscience"—closing the feedback loop of automated reasoning.
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple, cast
import collections
import math
import dateutil.parser  # type: ignore[import]

from sqlalchemy.orm import Session
from sqlalchemy import func

# Local imports
import hypothesis_tracker as ht # For accessing hypothesis records and their schema
import audit_bridge # Potentially for getting full audit data if needed for entropy deltas
from db_models import SystemState # For storing meta-evaluation results

# --- Configuration Placeholder ---
# These would typically come from superNova_2177.Config
class TempConfig:
    # BIAS_THRESHOLD_PERCENT is split into more granular settings
    MIN_SAMPLES_FOR_BIAS_ANALYSIS = 5 # Minimum data points for meaningful bias analysis
    VALIDATION_RATE_DELTA_THRESHOLD = 0.10  # e.g., 10% proportional difference for bias
    LOW_ENTROPY_DELTA_THRESHOLD = 0.1 # Threshold for flagging low entropy deltas
    UNRESOLVED_HYPOTHESIS_THRESHOLD_DAYS = 60
    # Add other config relevant to bias detection or quality scoring if needed


try:
    from config import Config as SystemConfig
except ImportError:
    SystemConfig = TempConfig  # type: ignore[misc]

CONFIG: Any = SystemConfig


def _get_all_hypotheses_with_parsed_metadata(db: Session) -> List[Dict[str, Any]]:
    """Helper to retrieve all hypothesis records and ensure metadata is parsed."""
    all_hypotheses = []
    records = db.query(SystemState).filter(
        SystemState.key.like("hypothesis_HYP_%")
    ).all()
    for record in records:
        try:
            value_str = cast(str, record.value)
            hyp_data = json.loads(value_str)
            # Ensure metadata is a dict, not just assumed from schema
            if "metadata" not in hyp_data or not isinstance(hyp_data["metadata"], dict):
                hyp_data["metadata"] = {}
            all_hypotheses.append(hyp_data)
        except json.JSONDecodeError:
            print(f"Warning: Malformed hypothesis record found for key: {record.key}")
            continue
    return all_hypotheses


def _parse_datetime_safely(dt_str: str) -> Optional[datetime]:
    """Safely parse datetime string, returning None on error."""
    try:
        return dateutil.parser.parse(dt_str)
    except (ValueError, TypeError, AttributeError):
        return None


def analyze_validation_patterns(db: Session) -> Dict[str, Any]:
    """
    Returns statistical insights on hypothesis records:
    Common keywords in validated vs. falsified texts.
    Average time to validation/falsification.
    Frequent supporting node clusters or audit log references.
    Popularity of source modules or authors (if metadata available).
    """
    all_hypotheses = _get_all_hypotheses_with_parsed_metadata(db)

    validated_texts: List[str] = []
    falsified_texts: List[str] = []
    time_to_resolve_seconds: List[float] = []
    all_supporting_nodes: collections.Counter[str] = collections.Counter()
    all_audit_sources: collections.Counter[str] = collections.Counter()
    source_module_popularity: collections.Counter[str] = collections.Counter()
    author_popularity: collections.Counter[str] = collections.Counter()  # Based on 'user_id' in metadata

    for hyp in all_hypotheses:
        hyp_status = hyp.get("status")
        hyp_created_at = _parse_datetime_safely(hyp["created_at"]) if "created_at" in hyp else None
        
        # Determine last update/resolution time from history
        resolution_time = None
        if hyp.get("history"):
            # Safely parse all history timestamps
            history_times = []
            for entry in hyp["history"]:
                t_str = entry.get("t")
                if t_str:
                    parsed_t = _parse_datetime_safely(t_str)
                    if parsed_t:
                        history_times.append(parsed_t)
            if history_times:
                resolution_time = sorted(history_times)[-1]


        if hyp_created_at and resolution_time and hyp_status in ["validated", "falsified", "inconclusive", "merged"]:
            time_to_resolve_seconds.append((resolution_time - hyp_created_at).total_seconds())

        text = hyp.get("text", "")
        # Basic tokenization and frequency counts for keywords
        words = [word.lower() for word in text.split() if len(word) > 2 and word.isalnum()] # Simple filtering

        if hyp_status == "validated":
            validated_texts.extend(words)
        elif hyp_status == "falsified":
            falsified_texts.extend(words)

        all_supporting_nodes.update(hyp.get("supporting_nodes", []))
        all_audit_sources.update(hyp.get("audit_sources", []))

        # Check metadata for source module and user_id
        meta = hyp.get("metadata", {})
        if "source_module" in meta:
            source_module_popularity[meta["source_module"]] += 1
        if "user_id" in meta: # Assuming user_id is passed as metadata if applicable
            author_popularity[meta["user_id"]] += 1


    avg_time_to_resolve = sum(time_to_resolve_seconds) / len(time_to_resolve_seconds) if time_to_resolve_seconds else 0.0

    return {
        "most_common_validated_keywords": collections.Counter(validated_texts).most_common(5),
        "most_common_falsified_keywords": collections.Counter(falsified_texts).most_common(5),
        "average_time_to_resolve_seconds": avg_time_to_resolve,
        "frequent_supporting_nodes": all_supporting_nodes.most_common(5),
        "frequent_audit_sources": all_audit_sources.most_common(5),
        "source_module_popularity": source_module_popularity.most_common(5),
        "author_popularity": author_popularity.most_common(5),
    }


def detect_judgment_biases(db: Session) -> List[Dict[str, Any]]:
    """
    Flags possible reasoning biases, returning a structured list of detected biases.
    """
    all_hypotheses = _get_all_hypotheses_with_parsed_metadata(db)
    
    total_hypotheses_count = len(all_hypotheses)
    
    # Check if there's enough data for meaningful bias analysis
    if total_hypotheses_count < CONFIG.MIN_SAMPLES_FOR_BIAS_ANALYSIS:
        return [{"bias_type": "data_insufficiency", "magnitude": 0.0, "severity_estimate": "low", "details": f"Not enough hypotheses ({total_hypotheses_count}) for robust bias detection (min {CONFIG.MIN_SAMPLES_FOR_BIAS_ANALYSIS})."}]

    validated_hypotheses = [h for h in all_hypotheses if h.get("status") == "validated"]
    
    biases: List[Dict[str, Any]] = []

    # Bias 1: Disproportionate validation by source module/user
    module_validation_stats: Dict[str, Dict[str, int]] = collections.defaultdict(lambda: {"total": 0, "validated": 0})
    user_validation_stats: Dict[str, Dict[str, int]] = collections.defaultdict(lambda: {"total": 0, "validated": 0})

    for hyp in all_hypotheses:
        meta = hyp.get("metadata", {})
        source_module = meta.get("source_module")
        user_id = meta.get("user_id")

        if source_module:
            module_validation_stats[source_module]['total'] += 1
            if hyp.get("status") == "validated":
                module_validation_stats[source_module]['validated'] += 1
        if user_id:
            user_validation_stats[user_id]['total'] += 1
            if hyp.get("status") == "validated":
                user_validation_stats[user_id]['validated'] += 1

    overall_validation_rate = len(validated_hypotheses) / total_hypotheses_count if total_hypotheses_count > 0 else 0.0

    for module, data in module_validation_stats.items():
        if data['total'] >= CONFIG.MIN_SAMPLES_FOR_BIAS_ANALYSIS:
            module_rate = data['validated'] / data['total']
            if module_rate > overall_validation_rate * (1 + CONFIG.VALIDATION_RATE_DELTA_THRESHOLD):
                biases.append({
                    "bias_type": "source_module_disproportionate_validation",
                    "magnitude": module_rate - overall_validation_rate,
                    "severity_estimate": "medium", # Heuristic
                    "details": f"Module '{module}' validated disproportionately (Rate: {module_rate:.2f} vs Avg: {overall_validation_rate:.2f})"
                })
    
    for user, data in user_validation_stats.items():
        if data['total'] >= CONFIG.MIN_SAMPLES_FOR_BIAS_ANALYSIS:
            user_rate = data['validated'] / data['total']
            if user_rate > overall_validation_rate * (1 + CONFIG.VALIDATION_RATE_DELTA_THRESHOLD):
                biases.append({
                    "bias_type": "user_disproportionate_validation",
                    "magnitude": user_rate - overall_validation_rate,
                    "severity_estimate": "medium", # Heuristic
                    "details": f"User '{user}' validated disproportionately (Rate: {user_rate:.2f} vs Avg: {overall_validation_rate:.2f})"
                })


    # Bias 2: Over-reliance on specific audit sources/nodes
    all_validated_audit_sources = collections.Counter(
        source for hyp in validated_hypotheses for source in hyp.get("audit_sources", [])
    )
    all_validated_supporting_nodes = collections.Counter(
        node for hyp in validated_hypotheses for node in hyp.get("supporting_nodes", [])
    )

    if all_validated_audit_sources:
        most_common_audit_source, count = all_validated_audit_sources.most_common(1)[0]
        if count / len(validated_hypotheses) > 0.5: # If one source accounts for >50% of validated
            biases.append({
                "bias_type": "over_reliance_on_audit_source",
                "magnitude": count / len(validated_hypotheses),
                "severity_estimate": "high",
                "details": f"Over-reliance on audit source '{most_common_audit_source}' (accounts for {count/len(validated_hypotheses)*100:.1f}% of validated hypotheses)."
            })
    
    if all_validated_supporting_nodes:
        most_common_node, count = all_validated_supporting_nodes.most_common(1)[0]
        if count / len(validated_hypotheses) > 0.5: # If one node accounts for >50% of validated
            biases.append({
                "bias_type": "over_reliance_on_supporting_node",
                "magnitude": count / len(validated_hypotheses),
                "severity_estimate": "high",
                "details": f"Over-reliance on supporting node '{most_common_node}' (accounts for {count/len(validated_hypotheses)*100:.1f}% of validated hypotheses)."
            })


    # Bias 3: Overvalidation of hypotheses with low entropy deltas
    low_entropy_validated_count = 0
    total_validated_with_entropy_data = 0
    for hyp in validated_hypotheses:
        meta = hyp.get("metadata", {})
        entropy_delta = meta.get("entropy_delta") 
        if entropy_delta is not None:
            total_validated_with_entropy_data += 1
            if abs(entropy_delta) < CONFIG.LOW_ENTROPY_DELTA_THRESHOLD:
                low_entropy_validated_count += 1
    
    if total_validated_with_entropy_data >= CONFIG.MIN_SAMPLES_FOR_BIAS_ANALYSIS: 
        if low_entropy_validated_count / total_validated_with_entropy_data > 0.7: # Heuristic: >70% of validated have low delta
            biases.append({
                "bias_type": "overvalidation_of_low_entropy_deltas",
                "magnitude": low_entropy_validated_count / total_validated_with_entropy_data,
                "severity_estimate": "medium",
                "details": f"Tendency to overvalidate hypotheses with low entropy deltas ({low_entropy_validated_count}/{total_validated_with_entropy_data} validated hypotheses showed < {CONFIG.LOW_ENTROPY_DELTA_THRESHOLD} entropy change)."
            })

    return biases


def score_hypothesis_judgment_quality(db: Session) -> float:
    """
    Calculates a score (0.0–1.0) indicating systemic hypothesis judgment quality.
    """
    all_hypotheses = _get_all_hypotheses_with_parsed_metadata(db)
    total_hypotheses = len(all_hypotheses)
    
    if total_hypotheses == 0:
        return 0.0

    now = datetime.utcnow()

    # Metric 1: % of open hypotheses still unresolved after X days
    unresolved_stale_count = 0
    total_open_hypotheses = 0
    for hyp in all_hypotheses:
        if hyp.get("status") == "open":
            total_open_hypotheses += 1
            created_at = _parse_datetime_safely(hyp["created_at"])
            if created_at and (now - created_at).days > CONFIG.UNRESOLVED_HYPOTHESIS_THRESHOLD_DAYS:
                unresolved_stale_count += 1
    
    staleness_penalty = (unresolved_stale_count / total_open_hypotheses) if total_open_hypotheses > 0 else 0.0
    # Higher penalty for more stale hypotheses, so we subtract it from 1.0
    staleness_quality_factor = 1.0 - min(staleness_penalty, 1.0) # Clamp to [0,1]

    # Metric 2: Self-correction rate (hypotheses reversed from validated → falsified/inconclusive)
    reversals_count = 0
    total_validated_ever = 0
    for hyp in all_hypotheses:
        history = sorted(hyp.get("history", []), key=lambda x: x.get("t", ""))
        validated_seen = False
        for entry in history:
            if entry.get("status") == "validated":
                validated_seen = True
            elif validated_seen and entry.get("status") in ["falsified", "inconclusive"]:
                reversals_count += 1
                break # Count only one reversal per hypothesis
        if validated_seen: # Count hypotheses that were ever validated
            total_validated_ever += 1
    
    self_correction_penalty = (reversals_count / total_validated_ever) if total_validated_ever > 0 else 0.0
    self_correction_quality_factor = 1.0 - min(self_correction_penalty, 1.0) # Clamp to [0,1]

    # Metric 3: Diversity of audit evidence in validated set (entropy of sources)
    validated_hypotheses = [h for h in all_hypotheses if h.get("status") == "validated"]
    all_validated_audit_sources = [
        source for hyp in validated_hypotheses for source in hyp.get("audit_sources", [])
    ]
    source_counts = collections.Counter(all_validated_audit_sources)
    
    source_diversity_entropy = 0.0
    total_sources = sum(source_counts.values())
    if total_sources > 0:
        for count in source_counts.values():
            p = count / total_sources
            if p > 0:
                source_diversity_entropy -= p * math.log2(p)
    
    # Normalize entropy (max entropy for N sources is log2(N))
    num_unique_sources = len(source_counts)
    max_entropy = math.log2(num_unique_sources) if num_unique_sources > 1 else 0.0
    diversity_quality_factor = source_diversity_entropy / max_entropy if max_entropy > 0 else 0.0

    # Combine metrics into a single score (simple average for v3.9)
    quality_score = (staleness_quality_factor + self_correction_quality_factor + diversity_quality_factor) / 3.0
    
    return quality_score


def propose_judgment_heuristic_tweaks(db: Session) -> List[str]:
    """
    Outputs textual recommendations for improving judgment heuristics.
    These are static improvement suggestions only (v4.0 will handle reflective code adjustment).
    """
    all_hypotheses = _get_all_hypotheses_with_parsed_metadata(db)
    
    tweaks = []

    # Tweak 1: Based on Staleness
    unresolved_stale_count = 0
    total_open_hypotheses = 0
    now = datetime.utcnow()
    for hyp in all_hypotheses:
        if hyp.get("status") == "open":
            total_open_hypotheses += 1
            created_at = _parse_datetime_safely(hyp["created_at"])
            if created_at and (now - created_at).days > CONFIG.UNRESOLVED_HYPOTHESIS_THRESHOLD_DAYS:
                unresolved_stale_count += 1
    
    if total_open_hypotheses > 0 and (unresolved_stale_count / total_open_hypotheses) > 0.3: # If >30% are stale
        tweaks.append(f"Consider adjusting Config.UNRESOLVED_HYPOTHESIS_THRESHOLD_DAYS ({CONFIG.UNRESOLVED_HYPOTHESIS_THRESHOLD_DAYS} days currently) or increasing audit frequency to reduce stale hypotheses.")

    # Tweak 2: Based on Self-Correction Rate
    reversals_count = 0
    total_validated_ever = 0
    for hyp in all_hypotheses:
        history = sorted(hyp.get("history", []), key=lambda x: x.get("t", ""))
        validated_seen = False
        for entry in history:
            if entry.get("status") == "validated":
                validated_seen = True
            elif validated_seen and entry.get("status") in ["falsified", "inconclusive"]:
                reversals_count += 1
                break
        if validated_seen:
            total_validated_ever += 1
    
    if total_validated_ever > 0 and (reversals_count / total_validated_ever) > 0.15: # If >15% reversals
        tweaks.append(f"Review confidence thresholds and validation criteria; current self-correction rate ({reversals_count/total_validated_ever:.2f}) indicates potential over-validation or premature judgment.")

    # Tweak 3: Based on Bias Detection (simplified suggestions)
    biases_detected = detect_judgment_biases(db)
    if any(b.get("bias_type") == "source_module_disproportionate_validation" for b in biases_detected) or \
       any(b.get("bias_type") == "user_disproportionate_validation" for b in biases_detected):
        tweaks.append(f"Investigate potential biases in hypothesis source/author validation; consider diversifying input or re-evaluating trust metrics. (Bias threshold: {CONFIG.VALIDATION_RATE_DELTA_THRESHOLD*100:.1f}%)")
    if any(b.get("bias_type") in ["over_reliance_on_audit_source", "over_reliance_on_supporting_node"] for b in biases_detected):
        tweaks.append("Diversify audit sources and supporting nodes; avoid over-reliance on a few evidence types or entities.")
    if any(b.get("bias_type") == "overvalidation_of_low_entropy_deltas" for b in biases_detected):
        tweaks.append(f"Re-evaluate validation criteria for hypotheses linked to minor system changes (low entropy deltas < {CONFIG.LOW_ENTROPY_DELTA_THRESHOLD}); ensure robust evidence for small shifts.")

    # Tweak 4: General suggestions based on overall judgment quality score (using score_hypothesis_judgment_quality output)
    overall_quality_score = score_hypothesis_judgment_quality(db)
    if overall_quality_score < 0.5: # Low quality
        tweaks.append("Urgent: Overall hypothesis judgment quality is low. Review all reasoning heuristics, particularly confidence and conflict detection thresholds.")
    elif overall_quality_score < 0.75: # Medium quality, room for improvement
        tweaks.append("Consider fine-tuning conflict detection thresholds and synthesis logic to improve judgment precision.")


    return tweaks


def run_meta_evaluation(db: Session) -> str:
    """
    Executes the full meta-evaluation workflow and stores the results in SystemState.
    """
    timestamp = datetime.utcnow().isoformat()
    
    validation_trends = analyze_validation_patterns(db)
    bias_detections = detect_judgment_biases(db)
    judgment_quality_score = score_hypothesis_judgment_quality(db)
    proposed_tweaks = propose_judgment_heuristic_tweaks(db)

    # Summarize proposed tweaks for the "summary" field
    summary_text = "Meta-evaluation complete."
    if proposed_tweaks:
        summary_text += f" {len(proposed_tweaks)} improvement suggestions generated."
        if any("Urgent:" in t for t in proposed_tweaks): # Check if any tweak has "Urgent:"
            summary_text += " Urgent tweaks identified."
    else:
        summary_text += " No critical tweaks proposed, system judgment appears healthy."

    meta_eval_results = {
        "timestamp": timestamp,
        "summary": summary_text,
        "validation_trends": validation_trends,
        "bias_detections": bias_detections,
        "judgment_quality_score": judgment_quality_score,
        "proposed_tweaks": proposed_tweaks,
    }

    key = "meta_eval_JUDGE_v1"
    state_entry = db.query(SystemState).filter(SystemState.key == key).first()

    if state_entry:
        state_entry.value = json.dumps(meta_eval_results, default=str)  # type: ignore[assignment]
    else:
        state_entry = SystemState(key=key, value=json.dumps(meta_eval_results, default=str))
        db.add(state_entry)

    try:
        db.commit()
        return key
    except Exception as e:
        db.rollback()
        print(f"Error storing meta-evaluation results: {e}")
        raise RuntimeError("Failed to store meta-evaluation results.") from e
