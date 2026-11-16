"""BIC scores of the three CPT types (STD, MLR, OLR) for one family, and the per-node winner.

This is the ONE copy of the CPT-scoring math in the project (CLAUDE.md). Used by
`scripts/fit_cpt_types.py`; walkthrough in `docs/code-guide/cpt-scoring.md`.

A *family* is a child variable v plus its parent set pa(v). For each family we fit three ways
of writing the conditional probability table P(v | pa(v)) and compare their BIC:

    BIC = LL - (log N / 2) * C                       (paper eq. 7/9; natural log; higher = better)

"The paper" here and below is Vomlel, Kybernetika 2026 (docs/references.md#vomlel2026).

where LL is the maximized log-likelihood on all N rows and C is the number of free parameters.
With k = 3 states and n parents (CLAUDE.md conventions):

    STD  general table, one distribution per parent configuration    C = (k-1) * k^n   (eq. 6)
    MLR  multinomial logistic regression, parents dummy-coded         C = (k-1) * (1 + n(k-1))
    OLR  ordinal logistic regression, parents used as numbers -1/0/1 C = (k-1) + n

The equation numbers for the STD count (eq. 6) and BIC (eq. 7/9) are the ones used throughout
the Phase 1 code; the MLR (eq. 10-13) and OLR (eq. 16-17) references come from the original
script's comments. Coding choices are decision log entries 7-9.

Winner rule (`pick_winner`): the highest BIC; an EXACT tie goes to the type listed first
(STD, then MLR, then OLR). This is the Phase 1 rule, kept unchanged in step 1.5.0b. It has a
known flaw: rounding-size differences (~1e-13) are not treated as ties. Step 1.5.1 replaces it
with a 1e-6 tolerance and the order STD, OLR, MLR.

Run the whole fit: `python scripts/fit_cpt_types.py` (or `make phase1`).
"""

import warnings

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.discrete.discrete_model import MNLogit
from statsmodels.miscmodels.ordinal_model import OrderedModel

from bnjoint import config

CPT_TYPES: tuple[str, ...] = ("STD", "MLR", "OLR")  # also the tie-break order (see module doc)


# ---------------------------------------------------------------- parameter counts
def n_params_std(n: int, k: int = config.K_STATES) -> int:
    """Free parameters of a general table: (k-1) per parent configuration, k^n configurations.

    All k^n configurations are counted, even ones that never occur in the data (decision 7).

    Example:
        >>> n_params_std(2)
        18
    """
    return (k - 1) * k**n


def n_params_mlr(n: int, k: int = config.K_STATES) -> int:
    """Free parameters of MLR: for each of k-1 non-reference child states, an intercept plus
    (k-1) dummy coefficients per parent.

    Example:
        >>> n_params_mlr(2)
        10
    """
    return (k - 1) * (1 + n * (k - 1))


def n_params_olr(n: int, k: int = config.K_STATES) -> int:
    """Free parameters of OLR: k-1 thresholds (cut-points) plus one slope per parent.

    Example:
        >>> n_params_olr(2)
        4
    """
    return (k - 1) + n


def penalty_weight(n_obs: int) -> float:
    """BIC penalty per parameter, log(N)/2 (natural log).

    Example:
        >>> round(penalty_weight(1661), 4)
        3.7076
    """
    return np.log(n_obs) / 2.0


# ---------------------------------------------------------------- STD
def loglik_std(df: pd.DataFrame, child: str, parents: list[str]) -> float:
    """Maximized log-likelihood of a general table: sum over parent configurations j and
    child states i of N_ij * log(N_ij / N_j), using only configurations seen in the data.

    Args:
        df: the data (values -1/0/1).
        child: the child column.
        parents: the parent columns (may be empty).

    Example:
        >>> loglik_std(pd.DataFrame({"x": [-1, -1, 1, 1], "y": [-1, -1, -1, 1]}), "y", ["x"])
        -1.386294...   # = 2 * log(1/2)
    """
    # The summation order below is the one used for the reported Phase 1 numbers. Changing
    # it can change the last digits of the floating-point result, so leave it as is.
    if parents:
        ll = 0.0
        for _, sub in df.groupby(parents)[child]:  # one group per observed configuration
            counts = sub.value_counts()
            total = counts.sum()
            for c in counts:
                ll += c * np.log(c / total)
        return ll
    counts = df[child].value_counts()
    total = counts.sum()
    return sum(c * np.log(c / total) for c in counts)


def bic_std(df: pd.DataFrame, child: str, parents: list[str], k: int, w: float) -> float:
    """BIC of a general table (STD). `w` is `penalty_weight(len(df))`.

    Example:
        >>> d = pd.DataFrame({"x": [-1, -1, 1, 1], "y": [-1, -1, -1, 1]})
        >>> bic_std(d, "y", ["x"], k=3, w=penalty_weight(4))
        -5.545177...   # = -8 log 2
    """
    return loglik_std(df, child, parents) - w * n_params_std(len(parents), k)


# ---------------------------------------------------------------- MLR
def mlr_design(df: pd.DataFrame, parents: list[str], k: int) -> pd.DataFrame:
    """Predictor matrix for MLR: a constant column plus k-1 dummy (0/1) columns per parent.

    `pd.get_dummies(..., drop_first=True)` drops the lowest state (-1) of each parent, so -1 is
    the reference state (decision 8). If a parent never takes one of its states, it gets fewer
    columns than the parameter count assumes; a warning says so.

    Example:
        >>> mlr_design(pd.DataFrame({"x": [-1, 0, 1]}), ["x"], 3).columns.tolist()
        ['const', 'x_0', 'x_1']
    """
    if not parents:
        return pd.DataFrame({"const": np.ones(len(df))})
    X = pd.get_dummies(df[parents].astype("category"), drop_first=True).astype(float)
    X = sm.add_constant(X)
    expected = 1 + len(parents) * (k - 1)
    if X.shape[1] != expected:
        warnings.warn(
            f"expected {expected} MLR columns for parents {parents}, got {X.shape[1]}: a parent "
            "is missing a state in this data, so the MLR parameter count may not match the fit.",
            stacklevel=2,
        )
    return X


def bic_mlr(df: pd.DataFrame, child: str, parents: list[str], k: int, w: float) -> float:
    """BIC of multinomial logistic regression (statsmodels MNLogit). -inf if the fit fails.

    Example:
        >>> bic_mlr(df, "a3", ["a4"], k=3, w=penalty_weight(len(df)))   # doctest: +SKIP
    """
    try:
        ll = MNLogit(df[child], mlr_design(df, parents, k)).fit(disp=0).llf
    except Exception as e:  # report and give the type no chance of winning
        print(f"[{child}] MLR fit failed: {e}")
        return -np.inf
    return ll - w * n_params_mlr(len(parents), k)


# ---------------------------------------------------------------- OLR
def bic_olr(df: pd.DataFrame, child: str, parents: list[str], k: int, w: float) -> float:
    """BIC of ordinal logistic regression (statsmodels OrderedModel, logit link, BFGS).

    Parents enter as their raw values -1/0/1, one slope each (NOT dummy-coded; decision 8).
    A node without parents gets -inf: OLR is only used with parents (decision 9).

    Example:
        >>> bic_olr(pd.DataFrame({"y": [0, 1]}), "y", [], k=3, w=1.0)
        -inf
    """
    if not parents:
        return -np.inf
    try:
        model = OrderedModel(df[child], df[parents].astype(float), distr="logit")
        ll = model.fit(method="bfgs", disp=0).llf
    except Exception as e:
        print(f"[{child}] OLR fit failed: {e}")
        return -np.inf
    return ll - w * n_params_olr(len(parents), k)


# ---------------------------------------------------------------- per family and whole network
def score_family(
    df: pd.DataFrame, child: str, parents: list[str], k: int = config.K_STATES
) -> dict[str, float]:
    """BIC of all three CPT types for one family, as {"STD": ..., "MLR": ..., "OLR": ...}.

    Example:
        >>> score_family(df, "a3", ["a4"])   # doctest: +SKIP
        {'STD': -1142.508..., 'MLR': -1142.508..., 'OLR': ...}
    """
    w = penalty_weight(len(df))
    return {
        "STD": bic_std(df, child, parents, k, w),
        "MLR": bic_mlr(df, child, parents, k, w),
        "OLR": bic_olr(df, child, parents, k, w),
    }


def pick_winner(scores: dict[str, float]) -> str:
    """Return the CPT type with the highest BIC (Phase 1 rule; see the module docstring).

    Python's `max` returns the FIRST key with the largest value, so exact ties go to the
    type that comes first in `scores` (STD, MLR, OLR as built by `score_family`).

    Example:
        >>> pick_winner({"STD": -9.0, "MLR": -9.0, "OLR": -10.0})
        'STD'
    """
    return max(scores, key=scores.get)


def fit_cpt_types(
    df: pd.DataFrame,
    parents_by_var: dict[str, list[str]],
    varnames: list[str],
    k: int = config.K_STATES,
) -> pd.DataFrame:
    """Score every family of a network and pick each node's CPT type.

    Args:
        df: the data (values -1/0/1).
        parents_by_var: {child: [parents]}, e.g. from `gobnilp_io.parse_parent_sets`.
        varnames: the variables, in the order the output rows should have.
        k: number of states.

    Returns:
        DataFrame with columns variable, n_parents, bic_std, bic_mlr, bic_olr, winner
        (the columns of `results/phase1/cpt-type-summary.csv`).
    """
    rows = []
    for v in varnames:
        parents = parents_by_var[v]
        scores = score_family(df, v, parents, k)
        rows.append(
            {
                "variable": v,
                "n_parents": len(parents),
                "bic_std": scores["STD"],
                "bic_mlr": scores["MLR"],
                "bic_olr": scores["OLR"],
                "winner": pick_winner(scores),
            }
        )
    return pd.DataFrame(rows)
