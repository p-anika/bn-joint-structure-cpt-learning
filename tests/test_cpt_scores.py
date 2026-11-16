"""Tests for `bnjoint.cpt_scores`: parameter counts, BIC on a hand-computed example, winner rule.

Run with `make test` (or `pytest tests/test_cpt_scores.py -v`).

The tiny example used below (4 rows, one parent) is small enough to check with a calculator:

    x = [-1, -1, 1, 1]      (parent)
    y = [-1, -1, -1, 1]     (child)

    STD log-likelihood: for x = -1 both y are -1, so that group contributes 2*log(2/2) = 0.
    For x = 1 the y values are -1 and 1: 1*log(1/2) + 1*log(1/2) = -2*log 2 = -1.386294...
    N = 4, so the penalty weight is log(4)/2 = log 2 = 0.693147...
    STD parameters with k = 3, n = 1: (k-1)*k^n = 2*3 = 6.
    BIC_STD = -2*log 2 - 6*log 2 = -8*log 2 = -5.545177...
"""

import math

import numpy as np
import pandas as pd
import pytest

from bnjoint import cpt_scores as cs


# ---------------------------------------------------------------- parameter counts (CLAUDE.md)
@pytest.mark.parametrize(
    ("n", "std", "mlr", "olr"),
    [
        (0, 2, 2, 2),  # no parents: every type is just the 2 free probabilities of the child
        (1, 6, 6, 3),
        (2, 18, 10, 4),
        (3, 54, 14, 5),
    ],
)
def test_parameter_counts_k3(n: int, std: int, mlr: int, olr: int) -> None:
    """STD (k-1)k^n, MLR (k-1)(1+n(k-1)), OLR (k-1)+n, with k = 3."""
    assert cs.n_params_std(n, 3) == std
    assert cs.n_params_mlr(n, 3) == mlr
    assert cs.n_params_olr(n, 3) == olr


def test_penalty_weight_is_half_log_n() -> None:
    """BIC penalty per parameter is log(N)/2 with the natural log (paper eq. 7/9)."""
    assert cs.penalty_weight(1661) == pytest.approx(math.log(1661) / 2)


# ---------------------------------------------------------------- STD on the tiny example
@pytest.fixture
def tiny() -> pd.DataFrame:
    """The 4-row example from the module docstring."""
    return pd.DataFrame({"x": [-1, -1, 1, 1], "y": [-1, -1, -1, 1]})


def test_loglik_std_tiny(tiny: pd.DataFrame) -> None:
    assert cs.loglik_std(tiny, "y", ["x"]) == pytest.approx(-2 * math.log(2))


def test_bic_std_tiny(tiny: pd.DataFrame) -> None:
    w = cs.penalty_weight(len(tiny))
    assert cs.bic_std(tiny, "y", ["x"], k=3, w=w) == pytest.approx(-8 * math.log(2))


def test_loglik_std_no_parents(tiny: pd.DataFrame) -> None:
    """No parents: y has three -1 and one 1, LL = 3 log(3/4) + log(1/4)."""
    expected = 3 * math.log(3 / 4) + math.log(1 / 4)
    assert cs.loglik_std(tiny, "y", []) == pytest.approx(expected)


def test_olr_needs_a_parent(tiny: pd.DataFrame) -> None:
    """OLR is not used for a node without parents: its score is -inf so it can never win."""
    w = cs.penalty_weight(len(tiny))
    assert cs.bic_olr(tiny, "y", [], k=3, w=w) == -np.inf


def test_mlr_no_parents_equals_std_no_parents() -> None:
    """With no parents, MLR (intercepts only) fits the same marginal distribution as STD,
    and both have k-1 = 2 parameters, so their BICs agree."""
    rng = np.random.default_rng(0)
    df = pd.DataFrame({"y": rng.choice([-1, 0, 1], size=200, p=[0.2, 0.3, 0.5])})
    w = cs.penalty_weight(len(df))
    assert cs.bic_mlr(df, "y", [], k=3, w=w) == pytest.approx(
        cs.bic_std(df, "y", [], k=3, w=w), abs=1e-6
    )


# ---------------------------------------------------------------- winner rule
def test_pick_winner_takes_highest_bic() -> None:
    assert cs.pick_winner({"STD": -10.0, "MLR": -9.0, "OLR": -11.0}) == "MLR"


def test_pick_winner_exact_tie_goes_to_first_listed() -> None:
    """Current (pre-1.5.1) rule: Python's max() keeps the first of exactly equal scores,
    and the order is STD, MLR, OLR."""
    assert cs.pick_winner({"STD": -9.0, "MLR": -9.0, "OLR": -9.0}) == "STD"


def test_pick_winner_current_rule_has_no_tolerance() -> None:
    """Documents the known bug that step 1.5.1 fixes: a rounding-size difference (1e-13)
    is NOT treated as a tie today, so MLR wins. Step 1.5.1 changes this rule on purpose
    (decision log) and replaces this test with the 1e-6 tie rule."""
    assert cs.pick_winner({"STD": -9.0, "MLR": -9.0 + 1e-13, "OLR": -20.0}) == "MLR"
