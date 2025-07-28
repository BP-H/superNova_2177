import logging
import math
import random
from typing import Any, Dict, Optional, List

try:
    from config import Config

    FUZZINESS_RANGE_LOW = Config.FUZZINESS_RANGE_LOW
    FUZZINESS_RANGE_HIGH = Config.FUZZINESS_RANGE_HIGH
    INTERFERENCE_FACTOR = Config.INTERFERENCE_FACTOR
    DEFAULT_ENTANGLEMENT_FACTOR = Config.DEFAULT_ENTANGLEMENT_FACTOR
    ENTANGLEMENT_NORMALIZATION_FACTOR = getattr(
        Config,
        "ENTANGLEMENT_NORMALIZATION_FACTOR",
        DEFAULT_ENTANGLEMENT_FACTOR * 10,
    )
except Exception:  # pragma: no cover - fallback values

    class Config:
        FUZZINESS_RANGE_LOW = 0.1
        FUZZINESS_RANGE_HIGH = 0.4
        INTERFERENCE_FACTOR = 0.01
        DEFAULT_ENTANGLEMENT_FACTOR = 0.5
        ENTANGLEMENT_NORMALIZATION_FACTOR = DEFAULT_ENTANGLEMENT_FACTOR * 10
        ENTROPY_MODIFIER_SCALE = 2000.0
        ENTROPY_INTERVENTION_THRESHOLD = 1200.0
        ENTROPY_INTERVENTION_STEP = 50.0
        ENTROPY_CHAOS_THRESHOLD = 1500.0

    FUZZINESS_RANGE_LOW = Config.FUZZINESS_RANGE_LOW
    FUZZINESS_RANGE_HIGH = Config.FUZZINESS_RANGE_HIGH
    INTERFERENCE_FACTOR = Config.INTERFERENCE_FACTOR
    DEFAULT_ENTANGLEMENT_FACTOR = Config.DEFAULT_ENTANGLEMENT_FACTOR
    ENTANGLEMENT_NORMALIZATION_FACTOR = Config.ENTANGLEMENT_NORMALIZATION_FACTOR

from scientific_utils import ScientificModel, VerifiedScientificModel


class QuantumContext:
    """Lightweight quantum-inspired simulation context.

    Parameters
    ----------
    fuzzy_enabled:
        When ``True`` the :meth:`measure_superposition` method introduces a
        stochastic bias to the measurement outcome using ``FUZZINESS_RANGE_*``
        from :class:`superNova_2177.Config`.
    decoherence_rate:
        Rate controlling how quickly entanglement links decay each time
        :meth:`step` is called. The value represents an exponential decay
        coefficient per unit time.
    simulate:
        If ``True`` measurement functions return the full probability
        distribution rather than only the collapsed outcome.

    Notes
    -----
    Upon initialization the context contains no entangled entity pairs and the
    last measured state is ``None``. Basic initialization parameters are logged
    for traceability.
    """

    def __init__(
        self,
        fuzzy_enabled: bool = False,
        *,
        decoherence_rate: float = 0.01,
        simulate: bool = False,
    ):
        self.fuzzy_enabled = fuzzy_enabled
        self.decoherence_rate = decoherence_rate
        self.simulate = simulate
        self.entangled_pairs: Dict[tuple, float] = {}
        self._last_state: Optional[list[float]] = None
        logging.info(
            f"QuantumContext initialized with fuzzy_enabled={fuzzy_enabled}, decoherence_rate={decoherence_rate}, simulate={simulate}"
        )

        if FUZZINESS_RANGE_LOW > FUZZINESS_RANGE_HIGH:
            logging.error(
                "Invalid fuzziness range",
                extra={
                    "FUZZINESS_RANGE_LOW": FUZZINESS_RANGE_LOW,
                    "FUZZINESS_RANGE_HIGH": FUZZINESS_RANGE_HIGH,
                },
            )
            raise ValueError(
                "FUZZINESS_RANGE_LOW must be <= FUZZINESS_RANGE_HIGH"
            )

    def step(self, dt: float = 1.0) -> None:
        """Apply decoherence decay over ``dt`` time units."""
        decay = math.exp(-self.decoherence_rate * dt)
        before = len(self.entangled_pairs)
        for pair in list(self.entangled_pairs):
            self.entangled_pairs[pair] *= decay
            if self.entangled_pairs[pair] < 1e-6:
                del self.entangled_pairs[pair]
        lost = before - len(self.entangled_pairs)
        if lost:
            logging.info(f"Decoherence removed {lost} entangled pairs")

    @ScientificModel(
        source="Quantum Mechanics", model_type="Measurement", approximation="stochastic"
    )
    @VerifiedScientificModel(
        citation_uri="https://en.wikipedia.org/wiki/Quantum_measurement",
        assumptions="fuzzy bias heuristic",
        validation_notes="stochastic simulation",
        approximation="stochastic",
        value_bounds=(0.0, 1.0),
    )
    def measure_superposition(
        self, input_value: float, *, error_rate: float = 0.0
    ) -> Dict[str, Optional[float]]:
        r"""Simulate measurement of a superposition for a decision.

        Scientific Basis
        ----------------
        Implements a simple stochastic process mimicking quantum measurement
        collapse by introducing a bias when ``fuzzy_enabled`` is True.

        The core computation follows:

        ``O = 0.5 + (x - 0.5) * 2 * U(a, b)``

        where ``x`` is ``input_value`` and ``U(a, b)`` is a uniform random
        variable over ``[FUZZINESS_RANGE_LOW, FUZZINESS_RANGE_HIGH]``. An
        interference term ``\sum w_i * INTERFERENCE_FACTOR`` is then added and
        the result is clamped to ``[0, 1]``.

        Assumptions
        ----------
        * Entanglement effects are represented by a simple additive interference
          term.
        * Output value represents a probability and therefore lies within the
          closed interval ``[0, 1]``.

        Limitations
        -----------
        This model does not represent true quantum mechanics; it merely mimics
        qualitative behaviour for simulation purposes.

        Proposed Validation
        -------------------
        Compare large-sample measurement outcomes against an analytic
        expectation of the biased coin model to ensure the stochastic process
        behaves as expected.

        citation_uri: https://en.wikipedia.org/wiki/Quantum_measurement
        assumptions: fuzzy bias heuristic
        validation_notes: stochastic simulation
        """
        if self.fuzzy_enabled:
            bias = (input_value - 0.5) * 2
            outcome = 0.5 + bias * random.uniform(
                Config.FUZZINESS_RANGE_LOW, Config.FUZZINESS_RANGE_HIGH
            )
        else:
            outcome = input_value

        # interference from entangled pairs
        interference = sum(self.entangled_pairs.values()) * Config.INTERFERENCE_FACTOR
        outcome = max(0.0, min(1.0, outcome + interference))

        if error_rate:
            noise = random.uniform(-error_rate, error_rate)
            outcome = max(0.0, min(1.0, outcome + noise))

        distribution = [1.0 - outcome, outcome] if self.simulate else None

        if self._last_state is not None:
            trace = approximate_trace_distance(
                self._last_state, distribution or [1 - outcome, outcome]
            )
            fidelity = pseudo_fidelity_score(
                self._last_state, distribution or [1 - outcome, outcome]
            )
            logging.debug(
                f"trace_distance={trace['value']:.4f} fidelity={fidelity['value']:.4f}"
            )
        self._last_state = distribution or [1.0 - outcome, outcome]

        confidence = max(0.0, min(1.0, 1 - error_rate))
        return {
            "value": outcome,
            "unit": "probability",
            "confidence": confidence,
            "method": "fuzzy_superposition",
            "distribution": distribution,
        }

    def log_signal_instability(self, trace_distance: float) -> None:
        """Log a warning when the simulation deviates excessively.

        Parameters
        ----------
        trace_distance:
            L1-based trace distance between consecutive simulated states.

        Scientific Basis
        ----------------
        The trace distance is used as a heuristic indicator of divergence in
        the simulated quantum state. When ``trace_distance > 0.5`` the signal is
        considered unstable and a structured log entry is emitted.

        Proposed Validation
        -------------------
        Empirically evaluate typical trace distances generated during unit tests
        to confirm the threshold correctly flags unusual behaviour.
        """
        if trace_distance > 0.5:
            logging.warning(f"signal instability detected: {trace_distance:.4f}")

    @VerifiedScientificModel(
        citation_uri="https://en.wikipedia.org/wiki/Quantum_entanglement",
        assumptions="probabilistic weight models linkage",
        validation_notes="unit tests verify weight update",
    )
    def entangle_entities(
        self,
        entity1_id: Any,
        entity2_id: Any,
        influence_factor: float = DEFAULT_ENTANGLEMENT_FACTOR,
        *,
        bidirectional: bool = True,
    ) -> None:
        """Record a probabilistic link between two entities with optional reciprocity.

        Scientific Basis
        ----------------
        Metaphorically models quantum entanglement as weighted edges in a
        classical graph for future causal inference.

        Formally, each call updates the weight as
        ``w_{a,b} = w_{a,b} + influence_factor``. If ``bidirectional`` is True
        the symmetric edge ``w_{b,a}`` is updated in the same manner.

        Assumptions
        ----------
        * Entity identifiers are hashable and stable across calls.
        * Influence factors accumulate linearly over time.

        Limitations
        -----------
        The model abstracts entanglement strength as a single scalar weight and
        does not consider phase information or higher-order correlations.

        Proposed Validation
        -------------------
        Unit tests verify that repeated entanglement calls correctly increase
        stored weights and that optional bidirectionality behaves symmetrically.

        citation_uri: https://en.wikipedia.org/wiki/Quantum_entanglement
        assumptions: probabilistic weight models linkage
        validation_notes: unit tests verify weight update
        """
        if influence_factor < 0:
            raise ValueError("influence_factor must be >= 0")

        influence_factor = max(0.0, influence_factor)

        pair = tuple(sorted((entity1_id, entity2_id)))
        self.entangled_pairs[pair] = (
            self.entangled_pairs.get(pair, 0.0) + influence_factor
        )
        if bidirectional:
            self.entangled_pairs[(pair[1], pair[0])] = (
                self.entangled_pairs.get((pair[1], pair[0]), 0.0) + influence_factor
            )
        logging.debug(
            f"Entities {entity1_id} and {entity2_id} entangled with factor {self.entangled_pairs[pair]:.2f}"
        )

    @ScientificModel(source="Feedback control", model_type="AdaptiveParameter", approximation="heuristic")
    @VerifiedScientificModel(
        citation_uri="https://en.wikipedia.org/wiki/Feedback",
        assumptions="a linear relationship between entropy and optimal decoherence exists",
        validation_notes="monitor long-term system stability metrics after adaptation",
        approximation="heuristic",
    )
    def adapt_decoherence_rate(self, system_entropy: float) -> float:
        """Adapt ``decoherence_rate`` based on ``system_entropy``.

        Scientific Basis
        ----------------
        Implements a simple feedback mechanism where higher entropy accelerates
        decoherence and lower entropy slows it. This mirrors basic control
        theory feedback to maintain system stability.

        Parameters
        ----------
        system_entropy:
            Current entropy level from :class:`SystemStateService`.

        Returns
        -------
        float
            The updated ``decoherence_rate`` after clamping.

        Limitations
        -----------
        This adaptation uses a heuristic scaling and ignores potential
        non-linear effects in real quantum systems.

        Proposed Validation
        -------------------
        Track system entropy and decoherence rate over time to ensure the
        adjustments correlate with desired stability metrics.

        citation_uri: https://en.wikipedia.org/wiki/Feedback
        assumptions: a linear relationship between entropy and optimal decoherence exists
        validation_notes: monitor long-term system stability metrics after adaptation
        approximation: heuristic
        """
        if system_entropy > Config.ENTROPY_CHAOS_THRESHOLD:
            self.decoherence_rate += Config.ENTROPY_INTERVENTION_STEP / (
                Config.ENTROPY_MODIFIER_SCALE * 5
            )
        elif system_entropy < Config.ENTROPY_INTERVENTION_THRESHOLD:
            self.decoherence_rate -= Config.ENTROPY_INTERVENTION_STEP / (
                Config.ENTROPY_MODIFIER_SCALE * 10
            )

        self.decoherence_rate = max(0.001, min(0.1, self.decoherence_rate))
        logging.info(
            "decoherence_rate adapted",
            extra={"decoherence_rate": self.decoherence_rate, "entropy": system_entropy},
        )
        return self.decoherence_rate

    @ScientificModel(source="Quantum-inspired algorithm", model_type="Prediction", approximation="heuristic")
    @VerifiedScientificModel(
        citation_uri="https://en.wikipedia.org/wiki/Quantum-inspired_algorithm",
        assumptions="entanglement strength directly correlates with interaction likelihood",
        validation_notes="compare with actual future interactions in logged data",
        approximation="heuristic",
    )
    def quantum_prediction_engine(self, user_ids: List[Any]) -> Dict[str, Any]:
        """Forecast interaction likelihood from entanglement weights.

        Scientific Basis
        ----------------
        Uses summed entanglement weights as a proxy for the probability that a
        given user will engage in future interactions. The method aggregates
        these weights and scales them to ``[0,1]``.

        Parameters
        ----------
        user_ids:
            Sequence of user identifiers to evaluate.

        Returns
        -------
        Dict[str, Any]
            Structured prediction containing per-user probabilities,
            an overall coherence metric, and a simple uncertainty estimate.

        Limitations
        -----------
        Predictions rely solely on current entanglement weights and ignore
        temporal dynamics and external factors.

        Proposed Validation
        -------------------
        Compare predictions with actual user behaviour recorded in the system to
        assess calibration accuracy.

        citation_uri: https://en.wikipedia.org/wiki/Quantum-inspired_algorithm
        assumptions: entanglement strength directly correlates with interaction likelihood
        validation_notes: compare with actual future interactions in logged data
        approximation: heuristic
        """
        predicted: Dict[Any, float] = {}
        influences = []
        # Aggregate symmetric pairs so each connection counts only once
        aggregated: Dict[tuple, float] = {}
        for pair, weight in self.entangled_pairs.items():
            key = tuple(sorted(pair))
            aggregated[key] = max(aggregated.get(key, 0.0), weight)

        for uid in user_ids:
            total = sum(
                w for p, w in aggregated.items() if uid in p
            )
            prob = min(1.0, total / (ENTANGLEMENT_NORMALIZATION_FACTOR or 1.0))
            predicted[uid] = prob
            influences.append(prob)

        overall_coherence = min(1.0, sum(self.entangled_pairs.values()))
        mean = sum(influences) / len(influences) if influences else 0.0
        variance = (
            sum((p - mean) ** 2 for p in influences) / len(influences)
            if influences
            else 0.0
        )
        uncertainty = math.sqrt(variance)

        logging.debug(
            "quantum_prediction_engine",
            extra={"overall_coherence": overall_coherence, "uncertainty": uncertainty},
        )

        return {
            "predicted_interactions": predicted,
            "overall_quantum_coherence": overall_coherence,
            "uncertainty_estimate": uncertainty,
            "method": "quantum_inspired_heuristic",
        }


# expose adaptive and predictive capabilities as module-level functions
adapt_decoherence_rate = QuantumContext.adapt_decoherence_rate
quantum_prediction_engine = QuantumContext.quantum_prediction_engine


@VerifiedScientificModel(
    citation_uri="https://en.wikipedia.org/wiki/Quantum_state",
    assumptions="classical vector states",
    validation_notes="uses L1 norm as trace distance approximation",
    approximation="heuristic",
)
def approximate_trace_distance(
    state1: list[float], state2: list[float]
) -> Dict[str, Optional[float]]:
    r"""Approximate trace distance between two quantum states.

    Scientific Basis
    ----------------
    Computes ``d(\rho,\sigma) \approx \tfrac{1}{2}\|\rho-\sigma\|_1`` where the
    states are represented as classical probability vectors. The L1 norm
    ``\|x\|_1`` is evaluated as ``sum(abs(a-b))`` over vector components and the
    result is halved.

    Assumptions
    ----------
    * Input vectors are normalized to sum to one.
    * States are classical probability distributions rather than full density
      matrices.

    Proposed Validation
    -------------------
    Compare the output against an exact trace distance calculation for a set of
    simple two-state systems to confirm the heuristic implementation is within a
    reasonable error tolerance.

    citation_uri: https://en.wikipedia.org/wiki/Quantum_state
    assumptions: classical vector states
    validation_notes: uses L1 norm as trace distance approximation
    approximation: heuristic
    """
    try:
        diff = sum(abs(a - b) for a, b in zip(state1, state2)) / 2
        return {"value": diff, "unit": "distance", "confidence": None, "method": "l1"}
    except Exception as exc:
        logging.error(f"approximate_trace_distance failed: {exc}")
        return {"value": 0.0, "unit": "distance", "confidence": None, "method": "l1"}


@VerifiedScientificModel(
    citation_uri="https://en.wikipedia.org/wiki/Fidelity_of_quantum_states",
    assumptions="states normalized",
    validation_notes="cosine similarity heuristic",
    approximation="heuristic",
    value_bounds=(0.0, 1.0),
)
def pseudo_fidelity_score(
    initial: list[float], final: list[float]
) -> Dict[str, Optional[float]]:
    r"""Pseudo fidelity between initial and final states using cosine similarity.

    Scientific Basis
    ----------------
    Approximates the fidelity ``F(\rho,\sigma)`` for pure states represented as
    vectors by computing the cosine similarity between them. The returned score
    is ``(\mathrm{cos\_sim}+1)/2`` ensuring values are in ``[0,1]``.

    Assumptions
    ----------
    * Both ``initial`` and ``final`` vectors are real-valued and normalized.
    * Negative cosine similarity values correspond to orthogonal or opposite
      states and are mapped into ``[0,1]`` linearly.

    Proposed Validation
    -------------------
    Verify that ``pseudo_fidelity_score([1,0],[1,0])`` returns ``1`` and that
    orthogonal vectors yield ``0.5`` which mirrors the behaviour of a random
    guess in this heuristic model.

    citation_uri: https://en.wikipedia.org/wiki/Fidelity_of_quantum_states
    assumptions: states normalized
    validation_notes: cosine similarity heuristic
    approximation: heuristic
    """
    try:
        dot = sum(i * f for i, f in zip(initial, final))
        norm_i = math.sqrt(sum(i * i for i in initial))
        norm_f = math.sqrt(sum(f * f for f in final))
        denom = norm_i * norm_f or 1e-9
        cos_sim = dot / denom
        score = max(0.0, min(1.0, (cos_sim + 1) / 2))
        return {
            "value": score,
            "unit": "probability",
            "confidence": None,
            "method": "cosine",
        }
    except Exception as exc:
        logging.error(f"pseudo_fidelity_score failed: {exc}")
        return {
            "value": 0.0,
            "unit": "probability",
            "confidence": None,
            "method": "cosine",
        }
