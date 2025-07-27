import numpy as np
import pytest

from governance_config import quantum_consensus


def test_quantum_consensus_no_entanglement():
    # Odd number of True votes -> parity consensus of 0
    result = quantum_consensus([True, True, True])
    assert result == pytest.approx(0.0)


def test_quantum_consensus_with_correlations():
    votes = [True, True, True]
    cm = np.ones((3, 3))
    val = quantum_consensus(votes, correlation_matrix=cm)
    assert val == pytest.approx(0.5)


def test_quantum_consensus_bad_matrix():
    with pytest.raises(ValueError):
        quantum_consensus([True, False], correlation_matrix=[[1, 0]])
