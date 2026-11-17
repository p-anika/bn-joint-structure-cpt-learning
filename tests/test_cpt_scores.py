"""Tests for `bnjoint.cpt_scores`: parameter counts, BIC on a hand-computed example, MLR = STD
for 0 and 1 parents, convergence flags, and the tie rule (step 1.5.1).

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


# ---------------------------------------------------------------- MLR = STD for 0 and 1 parents
# Why they must agree: docs/explainers/04-one-parent-mlr-equals-std.md. With 0 or 1 parents,
# MLR has exactly as many free parameters as STD and can represent every table STD can, so the
# maximized log-likelihoods are equal (up to the optimizer's rounding) and so are the BICs.


def test_mlr_one_parent_equals_std_synthetic() -> None:
    """Random 1-parent data in which every (parent, child) combination occurs."""
    rng = np.random.default_rng(1)
    x = rng.choice([-1, 0, 1], size=300)
    # child depends on the parent, so the test is not just "both are the marginal"
    y = np.where(rng.random(300) < 0.6, x, rng.choice([-1, 0, 1], size=300))
    df = pd.DataFrame({"x": x, "y": y})
    assert (pd.crosstab(df["x"], df["y"]) > 0).all().all()  # no empty cell (see explainer 04)
    w = cs.penalty_weight(len(df))
    assert cs.n_params_mlr(1) == cs.n_params_std(1)
    assert cs.bic_mlr(df, "y", ["x"], k=3, w=w) == pytest.approx(
        cs.bic_std(df, "y", ["x"], k=3, w=w), abs=1e-6
    )


def _families_with_at_most_one_parent() -> list[tuple[str, list[str]]]:
    """The 0- and 1-parent families of the Phase 1 GOBNILP structure: 17 with one parent,
    plus d11 with none."""
    from bnjoint import config
    from bnjoint.gobnilp_io import parse_parent_sets

    varnames = config.VARNAMES_FILE.read_text().split()
    parents = parse_parent_sets(config.PHASE1_GOBNILP_LOG.read_text(), varnames)
    return [(v, p) for v, p in parents.items() if len(p) <= 1]


@pytest.mark.parametrize(("child", "parents"), _families_with_at_most_one_parent())
def test_mlr_equals_std_on_our_data(child: str, parents: list[str]) -> None:
    """On BN-data.csv, every 0- or 1-parent family has BIC_MLR == BIC_STD within 1e-6.
    In Phase 1 they differed by about 1e-13, which is why the tie tolerance is needed."""
    from bnjoint import config
    from bnjoint.io import read_bn_data

    df = read_bn_data(config.BN_DATA_CSV)
    w = cs.penalty_weight(len(df))
    assert cs.bic_mlr(df, child, parents, k=3, w=w) == pytest.approx(
        cs.bic_std(df, child, parents, k=3, w=w), abs=1e-6
    )


# ---------------------------------------------------------------- convergence flags
def test_score_family_reports_convergence(tiny: pd.DataFrame) -> None:
    """MLR and OLR report whether their optimizer converged; OLR without parents is not
    fitted at all, so its flag is None (not False)."""
    rng = np.random.default_rng(2)
    df = pd.DataFrame({"x": rng.choice([-1, 0, 1], 200), "y": rng.choice([-1, 0, 1], 200)})
    fam = cs.score_family(df, "y", ["x"])
    assert fam.converged == {"MLR": True, "OLR": True}
    fam0 = cs.score_family(df, "y", [])
    assert fam0.converged == {"MLR": True, "OLR": None}
    assert fam0.bic["OLR"] == -np.inf


# ---------------------------------------------------------------- winner rule (step 1.5.1)
# CLAUDE.md: scores within 1e-6 are tied; ties go to STD, then OLR, then MLR (simplest first).
def test_pick_winner_takes_highest_bic() -> None:
    assert cs.pick_winner({"STD": -10.0, "MLR": -9.0, "OLR": -11.0}) == "MLR"


def test_tie_rule_picks_std_over_rounding_noise() -> None:
    """The Phase 1 bug: MLR was 1e-13 higher than STD only through rounding and won.
    Under the tie rule this is a tie, and STD wins."""
    assert cs.pick_winner({"STD": -9.0, "MLR": -9.0 + 1e-13, "OLR": -20.0}) == "STD"


def test_tie_rule_real_phase1_case() -> None:
    """a13 in results/phase1/cpt-type-summary.csv: MLR won the old rule by ~2e-13."""
    scores = {"STD": -1583.719733998301, "MLR": -1583.7197339983009, "OLR": -1592.7923607959506}
    assert cs.pick_winner(scores) == "STD"


def test_tie_rule_exact_three_way_tie_goes_to_std() -> None:
    assert cs.pick_winner({"STD": -9.0, "MLR": -9.0, "OLR": -9.0}) == "STD"


def test_tie_rule_olr_beats_mlr_in_a_tie() -> None:
    """Order is STD, OLR, MLR: OLR has fewer parameters than MLR, so it wins their tie."""
    assert cs.pick_winner({"STD": -20.0, "MLR": -9.0 + 5e-7, "OLR": -9.0}) == "OLR"


def test_tie_rule_tolerance_is_1e6() -> None:
    """Just inside 1e-6 is a tie (STD); clearly outside it is not (MLR)."""
    assert cs.pick_winner({"STD": -9.0, "MLR": -9.0 + 0.9e-6, "OLR": -20.0}) == "STD"
    assert cs.pick_winner({"STD": -9.0, "MLR": -9.0 + 1e-5, "OLR": -20.0}) == "MLR"


def test_tie_rule_handles_minus_infinity() -> None:
    """A root node has OLR = -inf (not fitted); that must never cause an error or a win."""
    assert cs.pick_winner({"STD": -9.0, "MLR": -9.0 + 1e-13, "OLR": -np.inf}) == "STD"
