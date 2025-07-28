# --- MODULE: config.py ---
from decimal import Decimal
from typing import Dict, List
from functools import lru_cache
import os

class Config:
    ROOT_INITIAL_VALUE: Decimal = Decimal("1000000")
    TREASURY_SHARE: Decimal = Decimal("0.3333")
    REACTOR_SHARE: Decimal = Decimal("0.3333")
    CREATOR_SHARE: Decimal = Decimal("0.3334")  # To sum to 1
    KARMA_MINT_THRESHOLD: Decimal = Decimal("100")
    MIN_IMPROVEMENT_LEN: int = 50
    EMOJI_WEIGHTS: Dict[str, Decimal] = {
        "👍": Decimal("1"),
        "❤️": Decimal("2"),
    }  # Add supported emojis
    DAILY_DECAY: Decimal = Decimal("0.99")
    SNAPSHOT_INTERVAL: int = 100
    MAX_INPUT_LENGTH: int = 10000
    VAX_PATTERNS: Dict[str, List[str]] = {"block": [r"\b(blocked_word)\b"]}
    VAX_FUZZY_THRESHOLD: int = 2
    REACTOR_KARMA_PER_REACT: Decimal = Decimal("1")
    CREATOR_KARMA_PER_REACT: Decimal = Decimal("2")

    # --- Named constants for network effects and simulations ---
    NETWORK_CENTRALITY_BONUS_MULTIPLIER: Decimal = Decimal("5")
    CREATIVE_LEAP_NOISE_STD: float = 0.01
    BOOTSTRAP_Z_SCORE: float = 1.96

    FUZZINESS_RANGE_LOW: float = 0.1
    FUZZINESS_RANGE_HIGH: float = 0.4
    INTERFERENCE_FACTOR: float = 0.01
    DEFAULT_ENTANGLEMENT_FACTOR: float = 0.5
    CREATE_PROBABILITY_CAP: float = 0.9
    LIKE_PROBABILITY_CAP: float = 0.8
    FOLLOW_PROBABILITY_CAP: float = 0.6
    INFLUENCE_MULTIPLIER: float = 1.2
    ENTROPY_MULTIPLIER: float = 0.8
    CONTENT_ENTROPY_WINDOW_HOURS: int = 24
    PREDICTION_TIMEFRAME_HOURS: int = 24
    NEGENTROPY_SAMPLE_LIMIT: int = 100
    DISSONANCE_SIMILARITY_THRESHOLD: float = 0.8
    CREATIVE_LEAP_THRESHOLD: float = 0.5
    ENTROPY_REDUCTION_STEP: float = 0.2
    VOTING_DEADLINE_HOURS: int = 72
    CREATIVE_BARRIER_POTENTIAL: Decimal = Decimal("5000.0")
    SYSTEM_ENTROPY_BASE: float = 1000.0
    CREATION_COST_BASE: Decimal = Decimal("1000.0")
    ENTROPY_MODIFIER_SCALE: float = 2000.0
    ENTROPY_INTERVENTION_THRESHOLD: float = 1200.0
    ENTROPY_INTERVENTION_STEP: float = 50.0
    ENTROPY_CHAOS_THRESHOLD: float = 1500.0

    # --- Distribution constants ---
    CROSS_REMIX_CREATOR_SHARE: Decimal = Decimal("0.34")
    CROSS_REMIX_TREASURY_SHARE: Decimal = Decimal("0.33")
    CROSS_REMIX_COST: Decimal = Decimal("10")
    REACTION_ESCROW_RELEASE_FACTOR: Decimal = Decimal("100")

    # --- Background task tuning ---
    PASSIVE_AURA_UPDATE_INTERVAL_SECONDS: int = 3600
    PROPOSAL_LIFECYCLE_INTERVAL_SECONDS: int = 300
    NONCE_CLEANUP_INTERVAL_SECONDS: int = 3600
    NONCE_EXPIRATION_SECONDS: int = 86400
    CONTENT_ENTROPY_UPDATE_INTERVAL_SECONDS: int = 600
    NETWORK_CENTRALITY_UPDATE_INTERVAL_SECONDS: int = 3600
    PROACTIVE_INTERVENTION_INTERVAL_SECONDS: int = 3600
    AI_PERSONA_EVOLUTION_INTERVAL_SECONDS: int = 86400
    GUINNESS_PURSUIT_INTERVAL_SECONDS: int = 86400 * 3
    SCIENTIFIC_REASONING_CYCLE_INTERVAL_SECONDS: int = 3600
    ADAPTIVE_OPTIMIZATION_INTERVAL_SECONDS: int = 3600
    SELF_IMPROVE_INTERVAL_SECONDS: int = 3600
    ANNUAL_AUDIT_INTERVAL_SECONDS: int = 86400 * 365
    METRICS_PORT: int = int(os.environ.get("METRICS_PORT", "8001"))

    # Cooldown to prevent excessive universe forking
    FORK_COOLDOWN_SECONDS: int = 3600

    # --- Passive influence parameters ---
    INFLUENCE_THRESHOLD_FOR_AURA_GAIN: float = 0.1
    PASSIVE_AURA_GAIN_MULTIPLIER: Decimal = Decimal("10.0")

    AI_PERSONA_INFLUENCE_THRESHOLD: Decimal = Decimal("1000.0")
    MIN_GUILD_COUNT_FOR_GUINNESS: int = 500

    # Added for optional quantum tunneling simulations
    QUANTUM_TUNNELING_ENABLED: bool = True
    FUZZY_ANALOG_COMPUTATION_ENABLED: bool = False

    # FUSED: Added fields from v01_grok15.py Config
    GENESIS_BONUS_DECAY_YEARS: int = 4
    GOV_QUORUM_THRESHOLD: Decimal = Decimal("0.5")
    GOV_SUPERMAJORITY_THRESHOLD: Decimal = Decimal("0.9")
    GOV_EXECUTION_TIMELOCK_SEC: int = 259200  # 3 days
    ALLOWED_POLICY_KEYS: List[str] = ["DAILY_DECAY", "KARMA_MINT_THRESHOLD"]
    SPECIES: List[str] = ["human", "ai", "company"]

    # --- Meta-evaluation tuning ---
    # Minimum number of records required before bias analysis is considered
    MIN_SAMPLES_FOR_BIAS_ANALYSIS: int = 5
    # Proportional difference in validation rate that triggers bias flags
    VALIDATION_RATE_DELTA_THRESHOLD: float = 0.10
    # Threshold for detecting overvalidation of low entropy deltas
    LOW_ENTROPY_DELTA_THRESHOLD: float = 0.1
    # Days before unresolved hypotheses are considered stale in meta analyses
    UNRESOLVED_HYPOTHESIS_THRESHOLD_DAYS: int = 60


@lru_cache(maxsize=1)
def get_emoji_weights() -> Dict[str, Decimal]:
    """Return configured emoji reaction weights."""
    return Config.EMOJI_WEIGHTS
