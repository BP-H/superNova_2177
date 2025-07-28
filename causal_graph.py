"""Causal influence graph utilities."""
import math
from datetime import datetime, timedelta
from typing import Any, Optional, Iterable, Dict, List
import inspect
import json
import logging
from sqlalchemy import select

try:
    import networkx as nx
except Exception:  # pragma: no cover - optional dependency
    from typing import Any, Dict, Iterable, List

    class _NodeView(dict):
        """Minimal dictionary-like node view supporting call syntax."""

        def __call__(self) -> List[Any]:
            return list(self.keys())

    class DiGraph:
        def __init__(self) -> None:
            self._adj: Dict[Any, Dict[Any, Dict[str, Any]]] = {}
            self._nodes = _NodeView()

        @property
        def nodes(self) -> _NodeView:
            return self._nodes

        def add_node(self, node: Any, **attrs) -> None:
            self._adj.setdefault(node, {})
            self._nodes.setdefault(node, {}).update(attrs)

        def add_edge(self, u: Any, v: Any, weight: float = 1.0, **attrs) -> None:
            self.add_node(u)
            self.add_node(v)
            data = {"weight": weight}
            data.update(attrs)
            self._adj[u][v] = data

        def edges(self, data: bool = False):
            for u, nbrs in self._adj.items():
                for v, attr in nbrs.items():
                    yield (u, v, attr) if data else (u, v)

        def number_of_nodes(self) -> int:
            return len(self._nodes)

        def number_of_edges(self) -> int:
            return sum(len(nbrs) for nbrs in self._adj.values())

        def copy(self) -> "DiGraph":
            g = DiGraph()
            for n, attr in self.nodes.items():
                g.add_node(n, **attr)
            for u, nbrs in self._adj.items():
                for v, data in nbrs.items():
                    g.add_edge(u, v, **data)
            return g

        def has_edge(self, u: Any, v: Any) -> bool:
            return v in self._adj.get(u, {})

        def __contains__(self, node: Any) -> bool:
            return node in self._adj

        def get_edge_data(self, u: Any, v: Any, default=None):
            return self._adj.get(u, {}).get(v, default)

        def __getitem__(self, node: Any):
            return self._adj[node]

    def _has_path(graph: DiGraph, source: Any, target: Any) -> bool:
        visited = set()
        stack = [source]
        while stack:
            node = stack.pop()
            if node == target:
                return True
            if node in visited:
                continue
            visited.add(node)
            stack.extend(graph._adj.get(node, {}))
        return False

    def _all_simple_paths(graph: DiGraph, source: Any, target: Any) -> Iterable[List[Any]]:
        path = [source]
        visited = {source}

        def dfs(current: Any):
            if current == target:
                yield list(path)
                return
            for nbr in graph._adj.get(current, {}):
                if nbr not in visited:
                    visited.add(nbr)
                    path.append(nbr)
                    yield from dfs(nbr)
                    path.pop()
                    visited.remove(nbr)

        yield from dfs(source)

    class nx:  # type: ignore
        DiGraph = DiGraph

        @staticmethod
        def has_path(graph: DiGraph, source: Any, target: Any) -> bool:
            return _has_path(graph, source, target)

        @staticmethod
        def all_simple_paths(graph: DiGraph, source: Any, target: Any) -> List[List[Any]]:
            return list(_all_simple_paths(graph, source, target))

from scientific_utils import ScientificModel, VerifiedScientificModel


class CausalGraph:
    """Wrapper around :class:`networkx.DiGraph` with time weighted edges."""

    def __init__(self) -> None:
        """Initialize an empty directed graph.

        Notes
        -----
        The underlying structure is a :class:`networkx.DiGraph`. Edges may
        carry additional metadata such as ``timestamp`` and ``edge_type`` which
        are used by higher level influence queries.
        """
        self.graph = nx.DiGraph()

    def add_node(self, node: Any) -> None:
        """Add ``node`` to the graph.

        Parameters
        ----------
        node : Any
            Identifier for the node to add.
        """
        self.graph.add_node(node)

    def add_causal_node(
        self,
        node: Any,
        *,
        timestamp: Optional[datetime] = None,
        source_module: Optional[str] = None,
        trigger_event: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[Any] = None,
        system_entropy_at_creation: Optional[float] = None,
        node_specific_entropy: Optional[float] = None,
        debug_payload: Optional[Dict[str, Any]] = None,
        inference_commentary: Optional[str] = None,
        system_state_ref: Optional[str] = None,
        log_entry_id: Optional[int] = None,
    ) -> None:
        """Add a node with standardized causal metadata."""

        if timestamp is None:
            timestamp = datetime.utcnow()

        if debug_payload is None:
            frame = inspect.currentframe()
            if frame and frame.f_back:
                f = frame.f_back
                debug_payload = {
                    "function": f.f_code.co_name,
                    "locals": {k: repr(v) for k, v in f.f_locals.items()},
                }

        self.graph.add_node(
            node,
            timestamp=timestamp,
            source_module=source_module,
            trigger_event=trigger_event,
            entity_type=entity_type,
            entity_id=entity_id,
            system_entropy_at_creation=system_entropy_at_creation,
            node_specific_entropy=node_specific_entropy,
            debug_payload=debug_payload,
            inference_commentary=inference_commentary,
            system_state_ref=system_state_ref,
            log_entry_id=log_entry_id,
        )

    def __contains__(self, node: Any) -> bool:
        """Return ``True`` if ``node`` exists in the graph."""
        return node in self.graph

    def get_edge_data(self, u: Any, v: Any, default=None):
        """Return attribute dictionary for the edge ``u``->``v``.

        Parameters
        ----------
        u, v : Any
            Source and target node identifiers.
        default : Any, optional
            Value returned if the edge is not present.

        Returns
        -------
        dict | Any
            Edge attribute dictionary or ``default`` if missing.
        """
        return self.graph.get_edge_data(u, v, default)

    def __getitem__(self, item):
        """Return adjacency mapping for ``item``."""
        return self.graph[item]

    def has_path(self, source: Any, target: Any) -> bool:
        """Return ``True`` if a directed path exists from ``source`` to ``target``."""
        return nx.has_path(self.graph, source, target)

    def all_simple_paths(self, source: Any, target: Any) -> Iterable:
        """Yield all simple directed paths from ``source`` to ``target``."""
        return list(nx.all_simple_paths(self.graph, source, target))

    def add_edge(
        self,
        source: Any,
        target: Any,
        weight: float = 1.0,
        edge_type: str = "follow",
        timestamp: Optional[datetime] = None,
        negative: bool = False,
        source_reason: Optional[str] = None,
    ) -> None:
        """Insert a directed edge with optional metadata.

        Parameters
        ----------
        source, target : Any
            Identifiers of the edge's start and end nodes.
        weight : float, optional
            Magnitude of the connection. If ``negative`` is ``True`` the value
            is stored as ``-abs(weight)``.
        edge_type : str, optional
            Categorical label describing the interaction type.
        timestamp : datetime, optional
            Time at which the interaction occurred. Defaults to ``now`` when not
            provided.
        negative : bool, optional
            When ``True`` the edge weight is treated as inhibitory.
        source_reason : str, optional
            Free-form note describing why the edge was added.

        Notes
        -----
        Additional metadata fields are stored on the underlying NetworkX edge
        dictionary. Missing timestamps default to ``datetime.utcnow``.
        """
        if timestamp is None:
            timestamp = datetime.utcnow()
        w = -abs(weight) if negative else weight
        self.graph.add_edge(source, target, weight=w)
        try:
            data = self.graph[source][target]
            data["edge_type"] = edge_type
            data["timestamp"] = timestamp
            data["source_reason"] = source_reason
        except Exception:
            pass

    @ScientificModel(source="Exponential Decay", model_type="TimeWeightedEdge", approximation="simulated")
    def time_weighted_weight(self, source: Any, target: Any, decay_rate: float = 0.0) -> dict:
        """Return time-decayed edge weight with structured metadata.

        Parameters
        ----------
        decay_rate : float
            Exponential decay constant in 1/seconds.

        Returns
        -------
        dict
            Dictionary with the decayed weight under the ``value`` key.

        Notes
        -----
        The decayed weight is computed as
        ``weight * exp(-decay_rate * age_seconds)`` where ``age_seconds`` is the
        elapsed time since the edge ``timestamp``.
        """
        data = self.graph.get_edge_data(source, target, {})
        weight = data.get("weight", 0.0)
        ts = data.get("timestamp", datetime.utcnow())
        age = (datetime.utcnow() - ts).total_seconds()
        value = weight * math.exp(-decay_rate * age)
        assert not math.isnan(value)
        return {
            "value": value,
            "unit": "weight",
            "confidence": None,
            "method": "exponential_decay",
        }

    def to_tensor(self):  # optional differentiable export
        try:
            import numpy as np
            nodes = list(self.graph.nodes())
            index = {n: i for i, n in enumerate(nodes)}
            mat = np.zeros((len(nodes), len(nodes)), dtype=float)
            for u, v, d in self.graph.edges(data=True):
                mat[index[u], index[v]] = d.get("weight", 1.0)
            return mat
        except Exception:  # pragma: no cover - optional feature
            return None

    def query_influence(self, source: Any, target: Any) -> float:
        """Compute influence probability from ``source`` to ``target``.

        The method enumerates all simple directed paths between ``source`` and
        ``target`` and returns the maximum product of edge weights along any
        path. If no path exists the return value is ``0.0``.

        Notes
        -----
        Enumerating all simple paths has worst-case exponential complexity in
        the number of nodes between ``source`` and ``target``.
        """
        if not self.has_path(source, target):
            return 0.0
        paths = self.all_simple_paths(source, target)
        strengths = []
        for p in paths:
            w = 1.0
            for u, v in zip(p[:-1], p[1:]):
                w *= self.graph[u][v].get("weight", 1.0)
            strengths.append(w)
        return max(strengths) if strengths else 0.0


def build_causal_graph(db) -> "InfluenceGraph":
    """Construct an :class:`InfluenceGraph` from a database session.

    Nodes correspond to ``Harmonizer`` IDs. Directed edges capture:

    - ``follow`` from follower to followee
    - ``like`` from a liker to the author of a liked ``VibeNode``
    - ``remix`` from the author of a remix ``VibeNode`` to the author of its
      parent

    ``InfluenceGraph.add_interaction`` is used to record each relationship.

    Returns
    -------
    InfluenceGraph
        Populated graph of user interactions.
    """

    # Import ORM models
    from db_models import Harmonizer, VibeNode, vibenode_likes

    g = InfluenceGraph()

    # Add all users as nodes and encode follow relationships.
    users = db.query(Harmonizer).all()
    for user in users:
        g.add_node(user.id)
    for user in users:
        for followed in getattr(user, "following", []):
            g.add_interaction(user.id, followed.id, edge_type="follow")

    # Cache vibenodes by id for lookups and handle likes.
    nodes = db.query(VibeNode).all()
    node_map = {n.id: n for n in nodes}

    like_rows = []
    if hasattr(db, "execute"):
        try:
            like_rows = db.execute(
                select(vibenode_likes.c.harmonizer_id, vibenode_likes.c.vibenode_id)
            ).fetchall()
        except Exception:
            like_rows = []
    else:  # pragma: no cover - fallback for dummy objects in tests
        for n in nodes:
            for liker in getattr(n, "likes", []):
                like_rows.append((getattr(liker, "id", liker), n.id))

    for liker_id, node_id in like_rows:
        node = node_map.get(node_id)
        if node is not None:
            g.add_interaction(liker_id, node.author_id, edge_type="like")

    # Add remix edges between authors when a vibenode references a parent node.
    for node in nodes:
        parent_id = getattr(node, "parent_vibenode_id", None)
        if parent_id and parent_id in node_map:
            parent = node_map[parent_id]
            g.add_interaction(node.author_id, parent.author_id, edge_type="remix")

    return g


class InfluenceGraph(CausalGraph):
    """CausalGraph specialization with influence methods."""

    def add_interaction(
        self,
        source: Any,
        target: Any,
        *,
        weight: float = 1.0,
        edge_type: str = "follow",
        timestamp: Optional[datetime] = None,
    ) -> None:
        """Convenience wrapper to record user interactions.

        Parameters
        ----------
        source, target : Any
            Nodes participating in the interaction.
        weight : float, optional
            Edge strength passed directly to :meth:`add_edge`.
        edge_type : str, optional
            Categorical interaction label such as ``"follow"`` or ``"like"``.
        timestamp : datetime, optional
            Time the interaction occurred.
        """
        self.add_edge(source, target, weight=weight, edge_type=edge_type, timestamp=timestamp)

    def trace_to_ancestors(
        self, node_id: Any, max_depth: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Return a list of upstream causal nodes with metadata."""
        if node_id not in self.graph:
            return []

        results: List[Dict[str, Any]] = []
        visited = set([node_id])
        queue = [(node_id, 0)]

        while queue:
            current, depth = queue.pop(0)
            if max_depth is not None and depth >= max_depth:
                continue
            preds = []
            if hasattr(self.graph, "predecessors"):
                preds = list(self.graph.predecessors(current))  # type: ignore[attr-defined]
            else:
                preds = [u for u, v in self.graph.edges() if v == current]
            for p in preds:
                if p in visited:
                    continue
                visited.add(p)
                edge_data = self.get_edge_data(p, current, {})
                node_data = self.graph.nodes.get(p, {})
                results.append(
                    {
                        "node_id": p,
                        "edge": {"source": p, "target": current, **edge_data},
                        "node_data": node_data,
                    }
                )
                queue.append((p, depth + 1))

        return results

    def trace_to_descendants(
        self, node_id: Any, max_depth: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Return a list of downstream causal nodes with metadata."""
        if node_id not in self.graph:
            return []

        results: List[Dict[str, Any]] = []
        visited = set([node_id])
        queue = [(node_id, 0)]

        while queue:
            current, depth = queue.pop(0)
            if max_depth is not None and depth >= max_depth:
                continue
            succs = []
            if hasattr(self.graph, "successors"):
                succs = list(self.graph.successors(current))  # type: ignore[attr-defined]
            else:
                succs = [v for u, v in self.graph.edges() if u == current]
            for s in succs:
                if s in visited:
                    continue
                visited.add(s)
                edge_data = self.get_edge_data(current, s, {})
                node_data = self.graph.nodes.get(s, {})
                results.append(
                    {
                        "node_id": s,
                        "edge": {"source": current, "target": s, **edge_data},
                        "node_data": node_data,
                    }
                )
                queue.append((s, depth + 1))

        return results

    def snapshot_graph(self, db_session, key_prefix: str = "graph_snapshot") -> str:
        """Serialize the graph and store it in ``SystemState``."""
        snapshot = {
            "timestamp": datetime.utcnow().isoformat(),
            "nodes": [
                {"id": n, **(self.graph.nodes.get(n, {}))} for n in self.graph.nodes
            ],
            "edges": [
                {"source": u, "target": v, **d}
                for u, v, d in self.graph.edges(data=True)
            ],
        }

        data = json.dumps(snapshot, default=str)

        try:
            from db_models import SystemState
        except Exception:
            return ""

        key = f"{key_prefix}_{int(datetime.utcnow().timestamp())}"
        stmt = select(SystemState).where(SystemState.key == key)
        state = db_session.execute(stmt).scalar_one_or_none()
        if state:
            state.value = data
        else:
            db_session.add(SystemState(key=key, value=data))
        db_session.commit()
        return key


@VerifiedScientificModel(
    citation_uri="https://en.wikipedia.org/wiki/Counterfactual_thinking",
    assumptions="observed metrics comparable to predictions",
    validation_notes="simple difference calculation",
    approximation="heuristic",
)
def validate_intervention_effect(node: Any, prediction: float, observed: float) -> dict:
    """Compare modeled counterfactuals to real outcomes using log replay.

    Parameters
    ----------
    node : Any
        Identifier of the intervention point.
    prediction : float
        Modeled counterfactual outcome.
    observed : float
        Actual measured outcome.

    Returns
    -------
    dict
        ``{"deviation": observed - prediction, "abs_deviation": |observed - prediction|}``

    citation_uri: https://en.wikipedia.org/wiki/Counterfactual_thinking
    assumptions: observed metrics comparable to predictions
    validation_notes: simple difference calculation
    approximation: heuristic
    """
    deviation = observed - prediction
    return {"deviation": deviation, "abs_deviation": abs(deviation)}


@VerifiedScientificModel(
    citation_uri="https://en.wikipedia.org/wiki/Heat_map",
    assumptions="validation count reflects confidence",
    validation_notes="frequency scaled to [0,1]",
    approximation="heuristic",
)
def confidence_log(graph: InfluenceGraph) -> dict:
    """Output confidence heatmap for edges based on validation frequency.

    Parameters
    ----------
    graph : InfluenceGraph
        Graph with edge ``validation_count`` attributes.

    Returns
    -------
    dict
        Mapping of edge tuples to a confidence value in ``[0, 1]``.

    Notes
    -----
    The confidence value is a linear scaling ``min(1.0, 0.1 * validation_count)``.

    citation_uri: https://en.wikipedia.org/wiki/Heat_map
    assumptions: validation count reflects confidence
    validation_notes: frequency scaled to [0,1]
    approximation: heuristic
    """
    heatmap = {}
    for u, v, d in graph.graph.edges(data=True):
        count = d.get("validation_count", 0)
        heatmap[(u, v)] = min(1.0, 0.1 * count)
    return {"edge_confidence": heatmap}


@ScientificModel(
    source="Causal inference heuristics",
    model_type="DynamicCausalDiscovery",
    approximation="heuristic",
)
@VerifiedScientificModel(
    citation_uri="https://en.wikipedia.org/wiki/Causal_inference",
    assumptions="observed correlations imply potential causation post-intervention",
    validation_notes="requires further experimentation for robust validation",
    approximation="heuristic",
)
def discover_causal_mechanisms(
    graph: InfluenceGraph, intervention_log: list[dict]
) -> list[dict]:
    """Infer causal links from interventions using time-aligned edge weights.

    Parameters
    ----------
    graph : InfluenceGraph
        Graph representing relationships such as follows or likes.
    intervention_log : list[dict]
        Sequence of intervention records with ``timestamp`` and ``target_entity``.

    Returns
    -------
    list[dict]
        Each entry describes a hypothesized causal mechanism with fields
        ``causal_id`` and ``strength_score``.

    Scientific Basis
    ----------------
    Metric changes following an intervention are treated as evidence for a
    causal relationship between the intervention and affected entity. The
    heuristic aggregates decayed edge weights that occur after the
    intervention timestamp.

    citation_uri: https://en.wikipedia.org/wiki/Causal_inference
    assumptions: observed correlations imply potential causation post-intervention
    validation_notes: requires further experimentation for robust validation
    approximation: heuristic
    """

    mechanisms: list[dict] = []

    def _out_edges(node: Any):
        g = graph.graph
        if hasattr(g, "out_edges"):
            return list(g.out_edges(node, data=True))  # type: ignore[attr-defined]
        if hasattr(g, "edges"):
            return [(u, v, d) for u, v, d in g.edges(data=True) if u == node]
        if hasattr(g, "_adj"):
            return [(node, v, d) for v, d in g._adj.get(node, {}).items()]
        return []

    for idx, iv in enumerate(intervention_log):
        ts = iv.get("timestamp")
        if isinstance(ts, str):
            try:
                ts = datetime.fromisoformat(ts)
            except Exception:
                ts = datetime.utcnow()
        if ts is None:
            ts = datetime.utcnow()

        target = iv.get("target_entity")
        metric = iv.get("effect_metric", "metric")
        pre_val = iv.get("pre_metric")
        post_val = iv.get("post_metric")
        delta = iv.get("metric_delta") or iv.get("delta")
        if delta is None:
            try:
                delta = (float(post_val) if post_val is not None else 0.0) - (
                    float(pre_val) if pre_val is not None else 0.0
                )
            except Exception:
                delta = 0.0
        try:
            delta = float(delta)
        except Exception:
            delta = 0.0

        related_edges = [
            (u, v, d)
            for u, v, d in _out_edges(target)
            if d.get("timestamp") and d["timestamp"] >= ts
        ]

        edge_strength = sum(
            graph.time_weighted_weight(u, v, decay_rate=0.001).get("value", 0.0)
            for u, v, _ in related_edges
        )

        strength_score = abs(delta) + edge_strength

        mechanism = {
            "causal_id": f"cm_{idx}",
            "cause_description": f"Intervention on {target}",
            "effect_description": f"{metric} change of {delta}",
            "strength_score": strength_score,
            "evidence_links": [f"log_{idx}"],
            "testable_hypothesis": f"Intervening on {target} modifies {metric}",
        }
        logging.info("causal_mechanism_discovered", extra={"data": mechanism})
        mechanisms.append(mechanism)

    return mechanisms


@ScientificModel(
    source="Causal inference heuristics",
    model_type="TemporalCausality",
    approximation="heuristic",
)
@VerifiedScientificModel(
    citation_uri="https://en.wikipedia.org/wiki/Causal_inference",
    assumptions="edge timestamps indicate order of influence",
    validation_notes="requires further experimentation for robust validation",
    approximation="heuristic",
)
def temporal_causality_analysis(
    graph: InfluenceGraph, time_periods: list[str]
) -> dict:
    """Analyze delayed influence chains within the graph.

    Parameters
    ----------
    graph : InfluenceGraph
        Graph containing timestamped edges.
    time_periods : list[str]
        Strings such as ``"last_24_hours"`` or ``"last_week"`` specifying
        analysis windows.

    Returns
    -------
    dict
        Summary of temporal causal insights for the provided periods.

    Scientific Basis
    ----------------
    Edges are ordered by timestamp and combined to reveal chains of
    influence. Decayed edge weights from
    :meth:`InfluenceGraph.time_weighted_weight` provide a heuristic
    measure of impact.

    citation_uri: https://en.wikipedia.org/wiki/Causal_inference
    assumptions: edge timestamps indicate order of influence
    validation_notes: requires further experimentation for robust validation
    approximation: heuristic
    """

    def _edges():
        g = graph.graph
        if hasattr(g, "edges"):
            return list(g.edges(data=True))
        if hasattr(g, "_adj"):
            acc = []
            for u, nbrs in g._adj.items():
                for v, d in nbrs.items():
                    acc.append((u, v, d))
            return acc
        return []

    def _period_delta(label: str) -> timedelta:
        label = label.lower()
        digits = "".join(ch for ch in label if ch.isdigit())
        qty = int(digits) if digits else 1
        if "week" in label:
            return timedelta(weeks=qty)
        if "day" in label:
            return timedelta(days=qty)
        if "hour" in label:
            return timedelta(hours=qty)
        return timedelta(hours=24 * qty)

    analyses: list[dict] = []
    now = datetime.utcnow()

    for period in time_periods:
        start = now - _period_delta(period)

        edges = [e for e in _edges() if e[2].get("timestamp") and e[2]["timestamp"] >= start]
        edges.sort(key=lambda x: x[2].get("timestamp", now))

        longest: list[Any] = []
        for u, v, d in edges:
            chain = [u, v]
            last_ts = d.get("timestamp", start)
            cur = v
            while True:
                candidate = None
                cand_ts = None
                for uu, vv, dd in edges:
                    ts = dd.get("timestamp")
                    if uu == cur and ts and ts > last_ts:
                        if cand_ts is None or ts < cand_ts:
                            candidate = (uu, vv, ts)
                            cand_ts = ts
                if candidate is None:
                    break
                cur = candidate[1]
                last_ts = candidate[2]
                chain.append(cur)
            if len(chain) > len(longest):
                longest = chain

        max_edge = None
        max_score = -1.0
        for u, v, d in edges:
            meta = graph.time_weighted_weight(u, v, decay_rate=0.001)
            val = meta.get("value", 0.0)
            if val > max_score:
                max_score = val
                max_edge = (u, v)

        analyses.append(
            {
                "time_period": period,
                "longest_causal_chain": longest,
                "most_impactful_temporal_link": {"edge": max_edge, "score": max_score},
                "notes": f"analysis window starting {start.isoformat()}",
            }
        )
        logging.info("temporal_causality_analysis", extra={"data": analyses[-1]})

    return {"analyses": analyses}
