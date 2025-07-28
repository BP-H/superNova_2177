"""
temporal_consistency_checker.py — Temporal Validation Consistency (v4.3)

Analyzes timestamped validations for temporal coherence, delay-based confidence
adjustment, and consensus evolution over time. Flags abrupt shifts or suspicious
validation timing patterns.

Used to increase robustness of scientific hypothesis auditing in superNova_2177.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from statistics import mean, stdev
try:
    from dateutil import parser
except Exception:  # pragma: no cover - optional dependency may be missing
    parser = None  # type: ignore[assignment]

logger = logging.getLogger("superNova_2177.temporal")
logger.propagate = False

class Config:
    MAX_VALIDATION_GAP_HOURS = 96       # Warn if large time gaps appear
    MIN_VALIDATION_SPREAD_HOURS = 1.5   # Expect some temporal distribution
    CONTRADICTION_WINDOW_HOURS = 6      # Flag contradictory notes near-simultaneous
    CONSENSUS_VOLATILITY_THRESHOLD = 0.25  # Flag shifts in scoring patterns
    
    # Business hours analysis
    BUSINESS_START_HOUR = 9             # 9 AM
    BUSINESS_END_HOUR = 17              # 5 PM
    SUSPICIOUS_BUSINESS_HOURS_RATIO = 0.9  # >90% in business hours is suspicious
    
    # Chronological ordering
    MAX_OUT_OF_ORDER_TOLERANCE = 0.1   # 10% of validations can be out of order


def _safe_parse_timestamp(value: str) -> Optional[datetime]:
    """Parse an ISO timestamp string to ``datetime`` safely."""
    if not value or len(value) > 40:
        return None
    try:
        if parser is not None:
            return parser.isoparse(value)
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, OverflowError, TypeError):
        return None

def analyze_temporal_consistency(
    validations: List[Dict[str, Any]], 
    reputations: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    if not validations:
        return {
            "avg_delay_hours": 0.0,
            "consensus_volatility": 0.0,
            "weighted_volatility": 0.0,
            "flags": ["no_validations"],
            "timeline": [],
            "business_hours_ratio": 0.0
        }

    parsed_validations = []
    business_hours_count = 0
    out_of_order_count = 0
    
    for i, v in enumerate(validations):
        ts_raw = v.get("timestamp")
        ts = _safe_parse_timestamp(ts_raw)
        if ts is None:
            logger.warning(f"Invalid timestamp in validation {i}: {ts_raw}")
            continue
        try:
            score = float(v.get("score", 0.5))
            validator_id = v.get("validator_id", f"unknown_{i}")
            
            parsed_validations.append({
                "timestamp": ts,
                "score": score,
                "validator_id": validator_id,
                "note": str(v.get("note", "")).lower(),
                "original_index": i
            })
            
            if Config.BUSINESS_START_HOUR <= ts.hour <= Config.BUSINESS_END_HOUR:
                business_hours_count += 1
                
        except (ValueError, TypeError) as e:
            logger.warning(
                f"Invalid validation data in entry {i}: {ts_raw} - {e}"
            )
            continue

    if len(parsed_validations) < 2:
        return {
            "avg_delay_hours": 0.0,
            "consensus_volatility": 0.0,
            "weighted_volatility": 0.0,
            "flags": ["insufficient_valid_timestamps"],
            "timeline": [],
            "business_hours_ratio": 0.0
        }

    sorted_validations = sorted(parsed_validations, key=lambda x: x["timestamp"])
    
    for i, val in enumerate(sorted_validations):
        if val["original_index"] != i:
            out_of_order_count += 1
    
    out_of_order_ratio = out_of_order_count / len(parsed_validations)
    business_hours_ratio = business_hours_count / len(parsed_validations)
    
    timestamps = [v["timestamp"] for v in sorted_validations]
    scores = [v["score"] for v in sorted_validations]
    timeline = [(v["timestamp"].isoformat(), v["score"], v["validator_id"]) 
                for v in sorted_validations]
    
    flags = []
    
    total_span = (timestamps[-1] - timestamps[0]).total_seconds() / 3600.0
    avg_gap = total_span / (len(timestamps) - 1) if len(timestamps) > 1 else 0.0

    if avg_gap > Config.MAX_VALIDATION_GAP_HOURS:
        flags.append("large_time_gap")
    if total_span < Config.MIN_VALIDATION_SPREAD_HOURS:
        flags.append("temporal_cluster")
    if out_of_order_ratio > Config.MAX_OUT_OF_ORDER_TOLERANCE:
        flags.append("chronological_disorder")
    if business_hours_ratio > Config.SUSPICIOUS_BUSINESS_HOURS_RATIO:
        flags.append("suspicious_business_hours_concentration")

    contradiction_indices = []
    for i, v in enumerate(sorted_validations):
        if any(k in v["note"] for k in ["contradict", "refute", "oppose", "disagree"]):
            contradiction_indices.append(i)

    if len(contradiction_indices) > 1:
        for i in range(len(contradiction_indices) - 1):
            t1 = timestamps[contradiction_indices[i]]
            t2 = timestamps[contradiction_indices[i+1]]
            gap = abs((t2 - t1).total_seconds()) / 3600.0
            if gap <= Config.CONTRADICTION_WINDOW_HOURS:
                flags.append("contradiction_near_simultaneous")

    volatility = stdev(scores) if len(scores) >= 2 else 0.0
    weighted_volatility = 0.0
    
    if reputations and len(scores) >= 2:
        weighted_scores = []
        total_weight = 0.0
        
        for v in sorted_validations:
            validator_id = v["validator_id"]
            reputation = reputations.get(validator_id, 0.5)
            weighted_scores.append(v["score"] * reputation)
            total_weight += reputation
        
        if total_weight > 0:
            normalized_weighted_scores = [s / total_weight for s in weighted_scores]
            weighted_volatility = stdev(normalized_weighted_scores) if len(normalized_weighted_scores) >= 2 else 0.0

    if volatility > Config.CONSENSUS_VOLATILITY_THRESHOLD:
        flags.append("unstable_consensus")
    if weighted_volatility > Config.CONSENSUS_VOLATILITY_THRESHOLD:
        flags.append("unstable_weighted_consensus")

    result = {
        "avg_delay_hours": round(avg_gap, 2),
        "consensus_volatility": round(volatility, 3),
        "weighted_volatility": round(weighted_volatility, 3),
        "flags": flags,
        "timeline": timeline,
        "business_hours_ratio": round(business_hours_ratio, 3),
        "chronological_order_ratio": round(1.0 - out_of_order_ratio, 3)
    }
    
    logger.info(f"Temporal analysis: {len(flags)} flags, volatility: {volatility:.3f}, business hours: {business_hours_ratio:.1%}")
    
    return result

def assess_temporal_trust_factor(temporal_result: Dict[str, Any]) -> float:
    flags = temporal_result.get("flags", [])
    volatility = temporal_result.get("consensus_volatility", 0.0)
    business_ratio = temporal_result.get("business_hours_ratio", 0.0)
    
    trust_factor = 1.0
    
    flag_penalties = {
        "large_time_gap": 0.1,
        "temporal_cluster": 0.15,
        "chronological_disorder": 0.2,
        "suspicious_business_hours_concentration": 0.1,
        "contradiction_near_simultaneous": 0.25,
        "unstable_consensus": 0.2,
        "unstable_weighted_consensus": 0.15
    }
    
    for flag in flags:
        penalty = flag_penalties.get(flag, 0.05)
        trust_factor -= penalty
    
    if volatility > 0.5:
        trust_factor -= 0.1
    
    return max(0.0, min(1.0, trust_factor))
