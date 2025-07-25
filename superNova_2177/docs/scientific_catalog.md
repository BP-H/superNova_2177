# Scientific Model Catalog

## time_weighted_weight
* **Source:** Exponential Decay
* **Model Type:** TimeWeightedEdge
* **Approximation:** simulated

Return time-decayed edge weight with structured metadata.

## calculate_influence_score
* **Source:** Brin & Page 1998
* **Model Type:** PageRank
* **Approximation:** simulated

Compute InfluenceScore for a user using the PageRank algorithm.

    Parameters
    ----------
    graph : nx.DiGraph
        Directed graph representing user interactions.
    user_id : int
        ID of the user whose influence is measured.

    Returns
    -------
    float
        PageRank value normalized between 0 and 1.

    Scientific Basis
    ----------------
    This method relies on the PageRank algorithm as described in
    *Brin and Page, 1998*, which assigns importance based on the
    link structure of a directed graph.

## calculate_interaction_entropy
* **Source:** Shannon 1948
* **Model Type:** Entropy
* **Approximation:** simulated

Calculate a user's interaction entropy with optional decay and impurity.

    The metric implements Shannon entropy over four interaction types:
    vibenodes created, comments posted, likes given, and follows.

    Scientific Basis
    ----------------
    Shannon's information entropy quantifies the uncertainty in a
    probability distribution. The result is normalized by log2(4).

## query_influence
* **Source:** Graph Theory
* **Model Type:** InfluencePropagation
* **Approximation:** simulated

Return a probabilistic influence value from source to target.

    Parameters
    ----------
    perturb_iterations : int, optional
        If greater than zero, performs edge weight perturbation sampling to
        estimate confidence.

## measure_superposition
* **Source:** Quantum Mechanics
* **Model Type:** Measurement
* **Approximation:** stochastic

Simulate measurement of a superposition for a decision.

        Scientific Basis
        ----------------
        Implements a simple stochastic process mimicking quantum measurement
        collapse by introducing a bias when ``fuzzy_enabled`` is True.
