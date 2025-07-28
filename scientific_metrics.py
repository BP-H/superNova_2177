import logging
import math
import random
import statistics
import datetime
import json
from decimal import Decimal
from typing import Any, TYPE_CHECKING, Dict, Optional

try:
    import networkx as nx
except Exception:  # pragma: no cover - optional dependency
    nx = None
from sqlalchemy.orm import Session
from scientific_utils import ScientificModel, VerifiedScientificModel
from causal_graph import InfluenceGraph, build_causal_graph as _build

try:
    from config import Config
    BOOTSTRAP_Z_SCORE = Config.BOOTSTRAP_Z_SCORE
    CREATE_CAP = Config.CREATE_PROBABILITY_CAP
    LIKE_CAP = Config.LIKE_PROBABILITY_CAP
    FOLLOW_CAP = Config.FOLLOW_PROBABILITY_CAP
    INFLUENCE_MULT = Config.INFLUENCE_MULTIPLIER
    ENTROPY_MULT = Config.ENTROPY_MULTIPLIER
except Exception:  # pragma: no cover - fallback during circular import
    BOOTSTRAP_Z_SCORE = 1.96
    CREATE_CAP = 0.9
    LIKE_CAP = 0.8
    FOLLOW_CAP = 0.6
    INFLUENCE_MULT = 1.2
    ENTROPY_MULT = 0.8

if TYPE_CHECKING:
    from db_models import Harmonizer

try:  # Prefer SystemState from db_models if available
    from db_models import SystemState, Base, engine
except Exception:  # pragma: no cover - fallback definition
    from sqlalchemy import Column, Integer, String
    from db_models import Base, engine

    class SystemState(Base):  # type: ignore
        __tablename__ = "system_state"

        id = Column(Integer, primary_key=True)
        key = Column(String, unique=True, nullable=False)
        value = Column(String, nullable=False)

    if hasattr(Base.metadata, "create_all") and engine is not None:
        Base.metadata.create_all(bind=engine)


@VerifiedScientificModel(
    citation_uri="https://en.wikipedia.org/wiki/PageRank",
    assumptions="graph static; edge weights positive and normalized",
    validation_notes="bootstrap sampling verifies 0<=score<=1",
    approximation="heuristic",
    value_bounds=(0.0, 1.0),
)
@ScientificModel(source="Brin & Page 1998", model_type="PageRank", approximation="simulated")
def calculate_influence_score(graph: nx.DiGraph, user_id: int, *, iterations: int = 10) -> Dict[str, Optional[float]]:
    r"""Compute a user's PageRank-based InfluenceScore.

    Parameters
    ----------
    graph : nx.DiGraph
        Directed graph of user interactions where edge weights represent
        influence magnitude and sum to one for outgoing edges.
    user_id : int
        Identifier of the target user.
    iterations : int, optional
        Number of bootstrap perturbations to generate a confidence estimate.

    Returns
    -------
    Dict[str, Optional[float]]
        Dictionary with ``value`` in the interval [0, 1] representing the
        PageRank score, ``unit`` of ``probability`` and optional ``confidence``.

    Scientific Basis
    ----------------
    Given a transition matrix :math:`P` derived from ``graph``, the PageRank
    value is the stationary distribution :math:`\pi` satisfying
    :math:`\pi = \alpha P^T \pi + (1-\alpha) v`, with damping factor
    :math:`\alpha=0.85`.  The implementation delegates to
    :func:`networkx.pagerank` and bootstraps by randomly perturbing edge weights.

    Limitations
    -----------
    Results assume a static snapshot and may not reflect temporal dynamics.

    citation_uri: https://en.wikipedia.org/wiki/PageRank
    assumptions: graph static; edge weights positive and normalized
    validation_notes: bootstrap sampling verifies 0<=score<=1
    approximation: heuristic
    """
    if nx is None:
        logging.warning("networkx not installed; returning default influence score")
        return {"value": 0.0, "unit": "probability", "confidence": None, "method": "PageRank"}
    try:
        if user_id not in graph:
            return {"value": 0.0, "unit": "probability", "confidence": None, "method": "PageRank"}

        scores = nx.pagerank(graph)
        base_score = scores.get(user_id, 0.0)

        # Bootstrap confidence by perturbing edge weights
        def _perturb(_):
            g2 = graph
            if hasattr(graph, "copy"):
                g2 = graph.copy()
            for u, v, data in list(g2.edges(data=True)):
                data["weight"] = data.get("weight", 1.0) * random.uniform(0.9, 1.1)
            pr = nx.pagerank(g2)
            return pr.get(user_id, 0.0)

        samples = []
        try:
            from concurrent.futures import ThreadPoolExecutor

            with ThreadPoolExecutor() as ex:
                samples = list(ex.map(_perturb, range(iterations)))
        except Exception:
            for i in range(iterations):
                samples.append(_perturb(i))
        conf = None
        if len(samples) > 1:
            std = statistics.stdev(samples)
            conf = max(0.0, min(1.0, 1 - BOOTSTRAP_Z_SCORE * std))
        logging.debug(f"InfluenceScore for {user_id}: {base_score:.4f} (conf={conf})")
        return {
            "value": float(base_score),
            "unit": "probability",
            "confidence": conf,
            "method": "PageRank",
        }
    except Exception as exc:
        logging.error(f"InfluenceScore calculation failed: {exc}")
        return {"value": 0.0, "unit": "probability", "confidence": None, "method": "PageRank"}


@VerifiedScientificModel(
    citation_uri="https://en.wikipedia.org/wiki/Entropy_(information_theory)",
    assumptions="four interaction types treated as independent",
    validation_notes="bootstrap sampling for confidence",
    approximation="heuristic",
    value_bounds=(0.0, 1.0),
)
@ScientificModel(source="Shannon 1948", model_type="Entropy", approximation="simulated")
def calculate_interaction_entropy(
    user: "Harmonizer",
    db: Session,
    *,
    method: str = "shannon",
    decay_rate: float = 0.0,
) -> Dict[str, Optional[float]]:
    r"""Measure diversity of user actions with optional temporal decay.

    Parameters
    ----------
    user : Harmonizer
        User record providing ``vibenodes``, ``comments``, ``liked_vibenodes``
        and ``following`` collections.
    method : {{"shannon", "gini"}}
        Entropy formulation to use. ``"shannon"`` computes
        :math:`H=-\sum_i p_i \log_2 p_i` normalized by ``log2(4)``.
        ``"gini"`` computes :math:`1-\sum_i p_i^2`.
    decay_rate : float, optional
        If greater than zero, interactions are weighted by
        ``exp(-decay_rate * age_seconds)`` where ``age_seconds`` is the time
        between ``now`` and each event's ``created_at`` timestamp.

    Returns
    -------
    Dict[str, Optional[float]]
        Normalized entropy value in ``bits`` for the Shannon method or impurity
        for the Gini method along with an optional confidence estimate.

    Limitations
    -----------
    Independence between interaction types may not hold and the decay assumes
    exponential memoryless behavior.

    citation_uri: https://en.wikipedia.org/wiki/Entropy_(information_theory)
    assumptions: four interaction types treated as independent
    validation_notes: bootstrap sampling for confidence
    approximation: heuristic
    """
    try:
        def _wcount(items: list[Any]) -> float:
            if not decay_rate:
                return float(len(items))
            now = datetime.datetime.utcnow()
            total_w = 0.0
            for it in items:
                ts = getattr(it, "created_at", None)
                if isinstance(ts, str):
                    ts = datetime.datetime.fromisoformat(ts)
                age = (now - ts).total_seconds() if ts else 0.0
                total_w += math.exp(-decay_rate * age)
            return total_w

        counts = [
            _wcount(list(getattr(user, "vibenodes", []))),
            _wcount(list(getattr(user, "comments", []))),
            _wcount(list(getattr(user, "liked_vibenodes", []))),
            _wcount(list(getattr(user, "following", []))),
        ]
        total = sum(counts)
        if total == 0:
            return {"value": 0.0, "unit": "bits", "confidence": None, "method": method}
        probs = [c / total for c in counts]

        if method == "gini":
            entropy = 1 - sum(p ** 2 for p in probs)
            norm_entropy = entropy
        else:
            entropy = -sum(p * math.log2(p) for p in probs if p > 0)
            norm_entropy = entropy / math.log2(len(counts))

        # Bootstrap confidence using multinomial resampling
        samples = []
        for _ in range(10):
            k = int(round(total))
            sample = random.choices(range(len(probs)), probs, k=k)
            sample_counts = [sample.count(i) for i in range(len(probs))]
            s_probs = [c / total for c in sample_counts]
            if method == "gini":
                s_entropy = 1 - sum(p ** 2 for p in s_probs)
            else:
                s_entropy = -sum(p * math.log2(p) for p in s_probs if p > 0)
                if method == "shannon":
                    s_entropy = s_entropy / math.log2(len(probs))
            samples.append(s_entropy)
        conf = None
        if len(samples) > 1:
            std = statistics.stdev(samples)
            conf = max(0.0, min(1.0, 1 - BOOTSTRAP_Z_SCORE * std))
        logging.debug(
            f"Interaction entropy for user {user.id}: {norm_entropy:.4f}"
        )
        return {
            "value": float(norm_entropy),
            "unit": "bits" if method == "shannon" else "impurity",
            "confidence": conf,
            "method": method,
        }
    except Exception as exc:
        logging.error(f"Interaction entropy calculation failed: {exc}")
        return {"value": 0.0, "unit": "bits", "confidence": None, "method": method}

def build_causal_graph(db: Session) -> InfluenceGraph:
    """Construct a time-aware :class:`InfluenceGraph` from user interactions."""
    return _build(db)


@VerifiedScientificModel(
    citation_uri="https://en.wikipedia.org/wiki/Scientific_method",
    assumptions="individual metrics independent; no weighting",
    validation_notes="unit test checks field presence",
    approximation="aggregation",
)
def generate_scientific_report(user: Any, db: Session) -> Dict[str, Any]:
    """Aggregate core metrics for a user into a structured report.

    The function calls :func:`calculate_influence_score` and
    :func:`calculate_interaction_entropy` then bundles their outputs along with
    the ``user_id``.  No additional weighting or cross-metric correlation is
    applied.

    citation_uri: https://en.wikipedia.org/wiki/Scientific_method
    assumptions: individual metrics independent; no weighting
    validation_notes: unit test checks field presence
    approximation: aggregation
    """
    graph = build_causal_graph(db)
    influence_score = calculate_influence_score(graph.graph, getattr(user, "id", 0))
    entropy = calculate_interaction_entropy(user, db)
    report = {
        "user_id": getattr(user, "id", None),
        "influence_score": influence_score,
        "interaction_entropy": entropy,
    }
    return report


@VerifiedScientificModel(
    citation_uri="https://en.wikipedia.org/wiki/Graph_theory",
    assumptions="path strength proxy for influence",
    validation_notes="confidence via path sampling",
    approximation="heuristic",
    value_bounds=(0.0, 1.0),
)
@ScientificModel(source="Graph Theory", model_type="InfluencePropagation", approximation="simulated")
def query_influence(
    graph: Any,
    source_id: int,
    target_id: int,
    *,
    perturb_iterations: int = 0,
) -> Dict[str, Optional[float]]:
    """Return a probabilistic influence value from ``source_id`` to ``target_id``.

    The influence score is defined as the maximum product of edge weights over
    all simple paths between the two nodes.  Edge weights are assumed to lie in
    ``[0, 1]`` and represent the probability of influence propagation along that
    edge.

    Parameters
    ----------
    perturb_iterations : int, optional
        If greater than zero, additional confidence estimation is performed by
        randomly perturbing edge weights and recomputing the path-strength
        heuristic.

    citation_uri: https://en.wikipedia.org/wiki/Graph_theory
    assumptions: path strength proxy for influence
    validation_notes: confidence via path sampling
    approximation: heuristic
    """
    if graph is None:
        return {"value": 0.0, "unit": "probability", "confidence": None, "method": "path_strength"}

    try:
        if isinstance(graph, InfluenceGraph):
            prob = graph.query_influence(source_id, target_id)
        else:
            if nx is None:
                logging.warning("networkx not installed; influence set to 0")
                return {"value": 0.0, "unit": "probability", "confidence": None, "method": "path_strength"}
            if not (source_id in graph and target_id in graph):
                return {"value": 0.0, "unit": "probability", "confidence": None, "method": "path_strength"}
            if source_id == target_id:
                prob = 1.0
            elif not nx.has_path(graph, source_id, target_id):
                prob = 0.0
            else:
                paths = list(nx.all_simple_paths(graph, source_id, target_id))
                strengths = []
                for p in paths:
                    w = 1.0
                    for u, v in zip(p[:-1], p[1:]):
                        w *= graph[u][v].get("weight", 1.0)
                    strengths.append(w)
                prob = max(strengths) if strengths else 0.0
            prob = max(0.0, min(1.0, prob))

        # simple confidence derived from path count
        conf = None
        if isinstance(graph, InfluenceGraph) and graph.graph:
            path_count = len(list(nx.all_simple_paths(graph.graph, source_id, target_id)))
            conf = max(0.0, min(1.0, 1.0 - 1.0 / (path_count + 1)))
        elif not isinstance(graph, InfluenceGraph) and nx is not None:
            path_count = len(list(nx.all_simple_paths(graph, source_id, target_id))) if nx.has_path(graph, source_id, target_id) else 0
            conf = max(0.0, min(1.0, 1.0 - 1.0 / (path_count + 1)))

        # optional perturbation-based confidence refinement
        if perturb_iterations > 0 and nx is not None and path_count > 0:
            def _p_iter(_):
                g2 = graph.graph.copy() if isinstance(graph, InfluenceGraph) else graph.copy()
                for u, v, data in g2.edges(data=True):
                    data["weight"] = data.get("weight", 1.0) * random.uniform(0.9, 1.1)
                if isinstance(graph, InfluenceGraph):
                    s_prob = InfluenceGraph(); s_prob.graph = g2
                    return s_prob.query_influence(source_id, target_id)
                if nx.has_path(g2, source_id, target_id):
                    paths = list(nx.all_simple_paths(g2, source_id, target_id))
                    st = []
                    for p in paths:
                        w = 1.0
                        for u2, v2 in zip(p[:-1], p[1:]):
                            w *= g2[u2][v2].get("weight", 1.0)
                        st.append(w)
                    return max(st) if st else 0.0
                return 0.0

            samples = []
            try:
                from concurrent.futures import ThreadPoolExecutor

                with ThreadPoolExecutor() as ex:
                    samples = list(ex.map(_p_iter, range(perturb_iterations)))
            except Exception:
                for i in range(perturb_iterations):
                    samples.append(_p_iter(i))
            if len(samples) > 1:
                std = statistics.stdev(samples)
                perturb_conf = max(0.0, min(1.0, 1 - BOOTSTRAP_Z_SCORE * std))
                if conf is None:
                    conf = perturb_conf
                else:
                    conf = (conf + perturb_conf) / 2
        logging.debug(f"Influence from {source_id} to {target_id}: {prob:.4f} (conf={conf})")
        return {"value": prob, "unit": "probability", "confidence": conf, "method": "path_strength"}
    except Exception as exc:
        logging.error(f"query_influence failed: {exc}")
        return {"value": 0.0, "unit": "probability", "confidence": None, "method": "path_strength"}


@VerifiedScientificModel(
    citation_uri="https://en.wikipedia.org/wiki/Information_gain",
    assumptions="probabilities normalized",
    validation_notes="difference in Shannon entropy",
    approximation="heuristic",
)
def track_information_gain(previous: Dict[str, float], current: Dict[str, float]) -> Dict[str, Optional[float]]:
    r"""Track entropy reduction between two probability distributions.

    ``previous`` and ``current`` are dictionaries mapping discrete outcomes to
    their probabilities.  Information gain is defined as
    :math:`IG = H(previous) - H(current)` where ``H`` denotes Shannon entropy
    :math:`H(p) = -\sum_i p_i \log_2 p_i`.

    citation_uri: https://en.wikipedia.org/wiki/Information_gain
    assumptions: probabilities normalized
    validation_notes: difference in Shannon entropy
    approximation: heuristic
    """
    try:
        def entropy(dist):
            return -sum(p * math.log2(p) for p in dist.values() if p > 0)

        gain = entropy(previous) - entropy(current)
        return {"value": gain, "unit": "bits", "confidence": None, "method": "entropy_diff"}
    except Exception as exc:  # pragma: no cover - safety
        logging.error(f"track_information_gain failed: {exc}")
        return {"value": 0.0, "unit": "bits", "confidence": None, "method": "entropy_diff"}


@VerifiedScientificModel(
    citation_uri="https://en.wikipedia.org/wiki/Lyapunov_exponent",
    assumptions="small perturbations",
    validation_notes="compares trajectory divergence",
    approximation="heuristic",
)
def estimate_lyapunov_stability(series_a: list[float], series_b: list[float]) -> Dict[str, Optional[float]]:
    r"""Approximate chaotic sensitivity via divergence of nearby trajectories.

    ``series_a`` and ``series_b`` should represent two time series starting from
    nearly identical initial conditions.  The Lyapunov exponent is estimated as
    :math:`\lambda = \frac{1}{N}\log\frac{|x_N - y_N|}{|x_0 - y_0|}` where ``N``
    is ``len(series_a)``.

    citation_uri: https://en.wikipedia.org/wiki/Lyapunov_exponent
    assumptions: small perturbations
    validation_notes: compares trajectory divergence
    approximation: heuristic
    """
    try:
        if not series_a or not series_b or len(series_a) != len(series_b):
            return {"value": 0.0, "unit": "divergence", "confidence": None, "method": "lyapunov"}
        initial_sep = abs(series_a[0] - series_b[0]) or 1e-9
        final_sep = abs(series_a[-1] - series_b[-1])
        exponent = math.log(final_sep / initial_sep) / len(series_a)
        return {"value": exponent, "unit": "divergence", "confidence": None, "method": "lyapunov"}
    except Exception as exc:
        logging.error(f"estimate_lyapunov_stability failed: {exc}")
        return {"value": 0.0, "unit": "divergence", "confidence": None, "method": "lyapunov"}


@VerifiedScientificModel(
    citation_uri="https://en.wikipedia.org/wiki/Convergence_(mathematics)",
    assumptions="series numeric",
    validation_notes="logs when stability reached",
    approximation="heuristic",
)
def log_metric_convergence(series: list[float], *, drift_threshold: float = 0.01) -> Dict[str, Optional[float]]:
    """Log whether the tail of ``series`` is converging or drifting.

    ``series`` is expected to be a chronological list of numeric values.
    The function computes ``delta = series[-1] - series[-2]`` and compares the
    absolute value to ``drift_threshold``.  Convergence is logged when
    ``|delta| < drift_threshold``.

    citation_uri: https://en.wikipedia.org/wiki/Convergence_(mathematics)
    assumptions: series numeric
    validation_notes: logs when stability reached
    approximation: heuristic
    """
    try:
        if len(series) < 2:
            return {"value": 0.0, "unit": "drift", "confidence": None, "method": "convergence"}
        delta = series[-1] - series[-2]
        if abs(delta) < drift_threshold:
            logging.info("metric convergence detected")
        else:
            logging.warning("metric drift detected")
        return {"value": delta, "unit": "drift", "confidence": None, "method": "convergence"}
    except Exception as exc:
        logging.error(f"log_metric_convergence failed: {exc}")
        return {"value": 0.0, "unit": "drift", "confidence": None, "method": "convergence"}


@VerifiedScientificModel(
    citation_uri="https://en.wikipedia.org/wiki/Graph_theory",
    assumptions="graph represents directed influence",
    validation_notes="unit tests verify detection for known cycles and strength calculation",
    approximation="heuristic",
)
def detect_feedback_loops(graph: InfluenceGraph) -> list[Dict[str, Any]]:
    """Identify recurrent influence cycles within ``graph``.

    The algorithm searches for all simple directed cycles in ``graph.graph``
    using :func:`networkx.simple_cycles` when available.  If ``networkx`` is
    unavailable or lacks ``simple_cycles`` (as in the lightweight test stub), a
    basic depth-first search fallback enumerates cycles.  For each detected
    cycle the function computes a *strength* heuristic: the geometric mean of
    the edge weights along that cycle.  This provides a proxy for the
    persistence of influence.

    citation_uri: https://en.wikipedia.org/wiki/Graph_theory
    assumptions: graph represents directed influence
    validation_notes: unit tests verify detection for known cycles and strength calculation
    approximation: heuristic
    """

    if nx is None:
        return []

    def _fallback_simple_cycles(dg: Any) -> list[list[Any]]:
        nodes = list(getattr(dg, "_adj", dg))
        cycles: list[list[Any]] = []

        def dfs(start: Any, current: Any, path: list[Any], visited: set[Any]) -> None:
            for nbr in dg[current]:
                if nbr == start and len(path) > 1:
                    cycles.append(path[:])
                elif nbr not in visited:
                    visited.add(nbr)
                    path.append(nbr)
                    dfs(start, nbr, path, visited)
                    path.pop()
                    visited.remove(nbr)

        for n in nodes:
            dfs(n, n, [n], {n})

        # deduplicate by canonical rotation
        unique: list[list[Any]] = []
        for c in cycles:
            m = min(range(len(c)), key=lambda i: str(c[i]))
            canon = c[m:] + c[:m]
            if canon not in unique:
                unique.append(canon)
        return unique

    if hasattr(nx, "simple_cycles"):
        cycles = list(nx.simple_cycles(graph.graph))
    else:
        cycles = _fallback_simple_cycles(graph.graph)

    result: list[Dict[str, Any]] = []
    for c in cycles:
        strength = 1.0
        for u, v in zip(c, c[1:] + c[:1]):
            strength *= graph.graph[u][v].get("weight", 1.0)
        geom_mean = strength ** (1.0 / len(c)) if c else 0.0
        result.append({"nodes": c, "strength": geom_mean})

    return result


@VerifiedScientificModel(
    citation_uri="https://en.wikipedia.org/wiki/Time_series",
    assumptions="logs are ordered; simple correlation implies lag",
    validation_notes="unit tests verify lag calculation for known log data",
    approximation="heuristic",
)
def estimate_lag_effects(
    intervention_log: list[dict],
    metric_log: list[dict],
    delay_range: tuple = (10, 300),
) -> dict:
    """Estimate temporal delay between interventions and metric shifts.

    Each intervention entry should contain a ``timestamp`` and a target
    ``metric_id``.  Metric log entries contain their ``metric_id``,
    ``timestamp`` and ``value``.  For every intervention this function searches
    for the first significant metric change after the intervention within the
    provided ``delay_range``.  The average of these delays forms the lag
    estimate.  ``correlation_strength`` is a coarse measure derived from the
    proportion of interventions with detected lags.

    citation_uri: https://en.wikipedia.org/wiki/Time_series
    assumptions: logs are ordered; simple correlation implies lag
    validation_notes: unit tests verify lag calculation for known log data
    approximation: heuristic
    """

    if not intervention_log or not metric_log:
        return {
            "lag_estimate_seconds": 0.0,
            "correlation_strength": 0.0,
            "affected_metric_id": "",
            "method": "lag_correlation",
        }

    metric_series: dict[str, list[tuple[datetime.datetime, float]]] = {}
    for m in metric_log:
        mid = m.get("metric_id")
        ts = m.get("timestamp")
        if isinstance(ts, str):
            ts = datetime.datetime.fromisoformat(ts)
        val = float(m.get("value", 0.0))
        metric_series.setdefault(str(mid), []).append((ts, val))

    for lst in metric_series.values():
        lst.sort(key=lambda x: x[0])

    delays: list[float] = []
    detections = 0

    for iv in intervention_log:
        ts0 = iv.get("timestamp")
        if isinstance(ts0, str):
            ts0 = datetime.datetime.fromisoformat(ts0)
        metric_id = str(iv.get("metric_id") or iv.get("target_metric_id"))
        series = metric_series.get(metric_id, [])
        prev_val = None
        for ts1, val in series:
            if ts1 <= ts0:
                prev_val = val
                continue
            if prev_val is None:
                prev_val = val
            change = abs(val - prev_val)
            delay = (ts1 - ts0).total_seconds()
            if change >= 0.1 and delay_range[0] <= delay <= delay_range[1]:
                delays.append(delay)
                detections += 1
                break
            prev_val = val

    if not delays:
        return {
            "lag_estimate_seconds": 0.0,
            "correlation_strength": 0.0,
            "affected_metric_id": "",
            "method": "lag_correlation",
        }

    avg_delay = sum(delays) / len(delays)
    corr_strength = detections / len(intervention_log)

    return {
        "lag_estimate_seconds": avg_delay,
        "correlation_strength": corr_strength,
        "affected_metric_id": metric_log[0].get("metric_id", ""),
        "method": "lag_correlation",
    }


@VerifiedScientificModel(
    citation_uri="https://en.wikipedia.org/wiki/Behavioral_prediction",
    assumptions="user behavior correlates with influence and entropy metrics",
    validation_notes="simple heuristic baseline for future ML models",
    approximation="heuristic",
)
def predict_user_interactions(
    user_id: int, db: Session, prediction_window_hours: int = 24
) -> Dict[str, Any]:
    """Predict whether a user will take certain actions in the near future.

    A simple heuristic uses the user's InfluenceScore and interaction entropy to
    derive probabilities for creating content, liking posts and following other
    users.  The formulas are

    * ``create_probability = min(CREATE_CAP, influence_score + (1 - entropy))``
    * ``like_probability   = min(LIKE_CAP, influence_score * INFLUENCE_MULT)``
    * ``follow_probability = min(FOLLOW_CAP, entropy * ENTROPY_MULT)``

    citation_uri: https://en.wikipedia.org/wiki/Behavioral_prediction
    assumptions: user behavior correlates with influence and entropy metrics
    validation_notes: simple heuristic baseline for future ML models
    approximation: heuristic
    """

    graph = build_causal_graph(db)
    influence = calculate_influence_score(graph.graph, user_id)
    from db_models import Harmonizer as HarmonizerModel  # local to avoid circular import
    user = db.query(HarmonizerModel).filter(HarmonizerModel.id == user_id).first()
    entropy = calculate_interaction_entropy(user, db)

    influence_score = influence["value"]
    entropy_score = entropy["value"]

    create_probability = min(CREATE_CAP, influence_score + (1 - entropy_score))
    like_probability = min(LIKE_CAP, influence_score * INFLUENCE_MULT)
    follow_probability = min(FOLLOW_CAP, entropy_score * ENTROPY_MULT)

    return {
        "user_id": user_id,
        "prediction_window_hours": prediction_window_hours,
        "predictions": {
            "will_create_content": {
                "probability": create_probability,
                "confidence": 0.7,
                "method": "influence_entropy_heuristic",
            },
            "will_like_posts": {
                "probability": like_probability,
                "confidence": 0.8,
                "method": "influence_based",
            },
            "will_follow_users": {
                "probability": follow_probability,
                "confidence": 0.6,
                "method": "entropy_based",
            },
        },
        "expires_at": (datetime.datetime.utcnow() + datetime.timedelta(hours=prediction_window_hours)).isoformat(),
        "created_at": datetime.datetime.utcnow().isoformat(),
    }


@VerifiedScientificModel(
    citation_uri="https://en.wikipedia.org/wiki/Prediction_accuracy",
    assumptions="binary outcome validation",
    validation_notes="tracks prediction vs reality",
    approximation="exact",
)
def validate_user_prediction(
    prediction: Dict[str, Any], actual_actions: Dict[str, bool]
) -> Dict[str, Any]:
    """Validate prediction accuracy against actual user actions.

    ``prediction`` should follow the structure produced by
    :func:`predict_user_interactions`.  For each action a binary outcome is
    inferred from ``probability > 0.5`` and compared with ``actual_actions``.
    The function returns per-action error metrics and the overall accuracy.
    """

    results = {}
    total_score = 0
    count = 0

    for action_type, predicted in prediction["predictions"].items():
        key = action_type.replace("will_", "")
        if key in actual_actions:
            actual = actual_actions[key]
            predicted_prob = predicted["probability"]
            predicted_outcome = predicted_prob > 0.5
            correct = predicted_outcome == actual

            results[action_type] = {
                "predicted_probability": predicted_prob,
                "predicted_outcome": predicted_outcome,
                "actual_outcome": actual,
                "correct": correct,
                "error": abs(predicted_prob - (1.0 if actual else 0.0)),
            }

            total_score += 1 if correct else 0
            count += 1

    overall_accuracy = total_score / count if count > 0 else 0.0

    return {
        "prediction_id": prediction.get("user_id"),
        "overall_accuracy": overall_accuracy,
        "detailed_results": results,
        "validation_timestamp": datetime.datetime.utcnow().isoformat(),
    }


@VerifiedScientificModel(
    citation_uri="https://en.wikipedia.org/wiki/Time_series_forecasting",
    assumptions="future trends resemble past trends",
    validation_notes="compare with actual outcomes via analyze_prediction_accuracy",
    approximation="heuristic",
)
@ScientificModel(source="Time Series Forecasting", model_type="SystemPrediction", approximation="heuristic")
def generate_system_predictions(db: Session, timeframe_hours: int) -> Dict[str, Any]:
    """Forecast global metrics for the coming ``timeframe_hours``.

    The function aggregates current system metrics such as average user
    interaction entropy and influence scores.  A simple linear extrapolation of
    the most recent window is used as a crude forecast for the next period.

    citation_uri: https://en.wikipedia.org/wiki/Time_series_forecasting
    assumptions: future trends resemble past trends
    validation_notes: compare with actual outcomes via analyze_prediction_accuracy
    approximation: heuristic
    """

    graph = build_causal_graph(db)
    from db_models import Harmonizer as HarmonizerModel

    users = db.query(HarmonizerModel).all()
    influence_scores: list[tuple[int, float]] = []
    entropies: list[float] = []

    for u in users:
        inf = calculate_influence_score(graph.graph, u.id)
        influence_scores.append((u.id, inf["value"]))
        ent = calculate_interaction_entropy(u, db)
        entropies.append(ent["value"])

    avg_entropy = sum(entropies) / len(entropies) if entropies else 0.0
    negentropy = 1.0 - avg_entropy
    entropy_std = statistics.stdev(entropies) if len(entropies) > 1 else 0.0

    top_influencers = [uid for uid, _ in sorted(influence_scores, key=lambda x: x[1], reverse=True)[:3]]

    return {
        "timeframe_hours": timeframe_hours,
        "predicted_system_entropy": {
            "value": avg_entropy,
            "unit": "bits",
            "confidence_interval": max(0.0, 1.0 - entropy_std),
        },
        "predicted_content_diversity": {
            "value": negentropy,
            "unit": "diversity",
            "confidence_interval": max(0.0, 1.0 - entropy_std),
        },
        "top_influencers_next_day": top_influencers,
        "falsifiability_criteria": "compare predicted metrics with observed metrics after timeframe",
        "generated_at": datetime.datetime.utcnow().isoformat(),
    }


@VerifiedScientificModel(
    citation_uri="https://en.wikipedia.org/wiki/Experiment", 
    assumptions="simple A/B or observational designs suffice", 
    validation_notes="experiments manually reviewed", 
    approximation="heuristic",
)
@ScientificModel(source="Basic Experiment Design", model_type="ValidationExperiment", approximation="heuristic")
def design_validation_experiments(predictions_list: list[Dict[str, Any]]) -> list[Dict[str, Any]]:
    """Design experiments to validate system predictions.

    For each prediction dictionary, an experiment is proposed.  High predicted
    entropy triggers an A/B test where the user "CosmicNexus" posts harmonizing
    content in the treatment group.

    citation_uri: https://en.wikipedia.org/wiki/Experiment
    assumptions: simple A/B or observational designs suffice
    validation_notes: experiments manually reviewed
    approximation: heuristic
    """

    experiments: list[Dict[str, Any]] = []
    for idx, pred in enumerate(predictions_list):
        pid = pred.get("prediction_id", f"pred_{idx}")
        entropy = pred.get("predicted_system_entropy", {}).get("value", 0.0)

        if entropy > 0.6:
            exp_type = "A/B"
            control = "no intervention"
            treatment = "CosmicNexus posts harmonizing content"
        else:
            exp_type = "observational"
            control = "passive observation"
            treatment = "N/A"

        experiments.append(
            {
                "experiment_id": f"exp_{idx}",
                "prediction_id": pid,
                "type": exp_type,
                "control_group_criteria": control,
                "treatment_group_criteria": treatment,
                "success_metrics": [
                    "calculate_interaction_entropy",
                    "query_influence",
                ],
                "duration_hours": pred.get("timeframe_hours", 24),
                "ethical_considerations": "placeholder",
            }
        )

    return experiments


@VerifiedScientificModel(
    citation_uri="https://en.wikipedia.org/wiki/Prediction_error",
    assumptions="historical predictions comparable to outcomes",
    validation_notes="percentage error averaged",
    approximation="heuristic",
)
@ScientificModel(source="Prediction Evaluation", model_type="AccuracyAnalysis", approximation="heuristic")
def analyze_prediction_accuracy(
    prediction_id: str,
    actual_outcome: Dict[str, Any],
    historical_predictions: list[Dict[str, Any]],
) -> Dict[str, Any]:
    """Compare ``prediction_id`` against ``actual_outcome`` and update confidence.

    Absolute percentage error is used to derive an accuracy score.  Bias is
    detected when the sign of recent errors is consistently positive or
    negative.

    citation_uri: https://en.wikipedia.org/wiki/Prediction_error
    assumptions: historical predictions comparable to outcomes
    validation_notes: percentage error averaged
    approximation: heuristic
    """

    try:
        pred = next((p for p in historical_predictions if p.get("prediction_id") == prediction_id), None)
        if pred is None:
            return {
                "prediction_id": prediction_id,
                "accuracy_score": 0.0,
                "bias_detected": False,
                "model_confidence_adjustment": 0.0,
                "detailed_comparison": {},
            }

        comparisons: Dict[str, float] = {}
        errors: list[float] = []
        for key, val in actual_outcome.items():
            pred_val = pred.get(key) or pred.get("predictions", {}).get(key, {}).get("value")
            if isinstance(pred_val, dict):
                pred_val = pred_val.get("value")
            if pred_val is None:
                continue
            error = abs(float(pred_val) - float(val))
            comparisons[key] = error
            errors.append(error)

        mean_error = sum(errors) / len(errors) if errors else 1.0

        past_errors = []
        for hp in historical_predictions:
            ao = hp.get("actual_outcome")
            if ao is None:
                continue
            pv = hp.get(key) or hp.get("predictions", {}).get(key, {}).get("value")
            if isinstance(pv, dict):
                pv = pv.get("value")
            if pv is not None and key in ao:
                past_errors.append(float(pv) - float(ao[key]))

        bias = False
        if past_errors:
            mean_sign = sum(1 if e > 0 else -1 for e in past_errors) / len(past_errors)
            current_sign = 1 if (pred_val or 0) - float(actual_outcome.get(key, 0)) > 0 else -1
            bias = abs(mean_sign) > 0.5 and current_sign == int(mean_sign > 0)

        accuracy = max(0.0, 1.0 - mean_error)
        adjustment = -mean_error if bias else mean_error

        return {
            "prediction_id": prediction_id,
            "accuracy_score": accuracy,
            "bias_detected": bias,
            "model_confidence_adjustment": adjustment,
            "detailed_comparison": comparisons,
        }
    except Exception as exc:  # pragma: no cover - safety
        logging.error("analyze_prediction_accuracy failed: %s", exc)
        return {
            "prediction_id": prediction_id,
            "accuracy_score": 0.0,
            "bias_detected": False,
            "model_confidence_adjustment": 0.0,
            "detailed_comparison": {},
        }


def _compute_delta(old_value: Any, new_value: Any) -> Optional[float]:
    """Return ``new_value - old_value`` if both are numeric; otherwise ``None``."""
    numeric_types = (int, float, Decimal)
    if isinstance(old_value, numeric_types) and isinstance(new_value, numeric_types):
        try:
            return float(new_value) - float(old_value)
        except Exception:
            return None
    return None


def log_metric_change(
    db: Session,
    metric_name: str,
    old_value: Any,
    new_value: Any,
    source_module: str,
    optional_note: str = "",
) -> None:
    """Persist a single metric change event to ``SystemState`` audit log."""

    # Import inside the function to ensure the freshest model definition is used.
    from db_models import SystemState

    entry = {
        "metric_name": metric_name,
        "old_value": float(old_value) if isinstance(old_value, Decimal) else old_value,
        "new_value": float(new_value) if isinstance(new_value, Decimal) else new_value,
        "source_module": source_module,
        "note": optional_note,
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "delta": _compute_delta(old_value, new_value),
    }

    state = (
        db.query(SystemState).filter(SystemState.key == "metric_audit_log").first()
    )
    log: list[Any]
    if state:
        try:
            log = json.loads(state.value)
        except Exception:
            log = []
    else:
        log = []

    log.append(entry)
    if len(log) > 1000:
        log = log[-1000:]

    if state:
        state.value = json.dumps(log, default=str)
    else:
        state = SystemState(key="metric_audit_log", value=json.dumps(log, default=str))
        db.add(state)
    db.commit()


def get_metric_history(db: Session, metric_name: str) -> list[Dict[str, Any]]:
    """Return all audit log entries for ``metric_name``."""

    # Import inside the function to avoid stale references during migrations.
    from db_models import SystemState

    state = (
        db.query(SystemState).filter(SystemState.key == "metric_audit_log").first()
    )
    if not state:
        return []

    try:
        log = json.loads(state.value)
    except Exception:
        return []

    return [entry for entry in log if entry.get("metric_name") == metric_name]


@VerifiedScientificModel(
    citation_uri="https://en.wikipedia.org/wiki/Scientific_method",
    assumptions="historical hypotheses include confidence and novelty",
    validation_notes="unit tests validate aggregation on sample data",
    approximation="heuristic",
)
@ScientificModel(source="Research log heuristics", model_type="Metacognition", approximation="heuristic")
def measure_autonomous_reasoning(hypotheses_history: list[dict]) -> dict:
    """Aggregate hypothesis metrics to quantify autonomous reasoning.

    Parameters
    ----------
    hypotheses_history : list[dict]
        Historical hypothesis records, each potentially containing ``id``,
        ``status``, ``confidence`` and ``novelty_score`` fields.

    Returns
    -------
    dict
        Dictionary summarizing the number of unique hypotheses generated,
        how many were falsified and the average ``confidence`` and
        ``novelty_score`` for those not falsified.

    citation_uri: https://en.wikipedia.org/wiki/Scientific_method
    assumptions: historical hypotheses include confidence and novelty
    validation_notes: unit tests validate aggregation on sample data
    approximation: heuristic
    """

    unique_ids = set()
    falsified = 0
    confs: list[float] = []
    novs: list[float] = []

    for idx, hyp in enumerate(hypotheses_history):
        hid = hyp.get("id") or hyp.get("hypothesis_id") or idx
        unique_ids.add(hid)
        if hyp.get("status") == "falsified":
            falsified += 1
            continue
        try:
            confs.append(float(hyp.get("confidence", 0.0)))
        except Exception:
            confs.append(0.0)
        try:
            novs.append(float(hyp.get("novelty_score", 0.0)))
        except Exception:
            novs.append(0.0)

    non_falsified = len(confs)
    avg_conf = sum(confs) / non_falsified if non_falsified else 0.0
    avg_novelty = sum(novs) / non_falsified if non_falsified else 0.0

    return {
        "total_hypotheses": len(unique_ids),
        "falsified_count": falsified,
        "average_confidence": avg_conf,
        "average_novelty": avg_novelty,
    }


@VerifiedScientificModel(
    citation_uri="https://en.wikipedia.org/wiki/Prediction_error",
    assumptions="validation logs contain accuracy_score and bias_detected",
    validation_notes="unit tests validate aggregation on sample logs",
    approximation="heuristic",
)
@ScientificModel(source="Prediction audits", model_type="Metacognition", approximation="heuristic")
def assess_meta_cognitive_awareness(prediction_validation_logs: list[dict]) -> dict:
    """Summarize validation logs for self-correction and accuracy awareness.

    Parameters
    ----------
    prediction_validation_logs : list[dict]
        Sequence of validation result dictionaries including fields like
        ``accuracy_score`` and ``bias_detected``.

    Returns
    -------
    dict
        Dictionary containing aggregate counts of validations, bias correction
        events and the mean accuracy achieved.

    citation_uri: https://en.wikipedia.org/wiki/Prediction_error
    assumptions: validation logs contain accuracy_score and bias_detected
    validation_notes: unit tests validate aggregation on sample logs
    approximation: heuristic
    """

    total = len(prediction_validation_logs)
    bias_events = 0
    acc_scores: list[float] = []

    for log in prediction_validation_logs:
        if log.get("bias_detected"):
            bias_events += 1
        try:
            acc_scores.append(float(log.get("accuracy_score", 0.0)))
        except Exception:
            acc_scores.append(0.0)

    avg_acc = sum(acc_scores) / total if total else 0.0

    return {
        "total_validations": total,
        "bias_correction_events": bias_events,
        "average_accuracy": avg_acc,
    }
