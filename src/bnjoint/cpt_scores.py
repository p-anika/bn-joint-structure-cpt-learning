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

Winner rule (`pick_winner`, step 1.5.1): the highest BIC wins, but scores within
`config.TIE_TOLERANCE` = 1e-6 of the best count as tied, and a tie goes to the simplest type:
STD, then OLR, then MLR (`config.TIE_ORDER`). Why: with 0 or 1 parents MLR and STD are the SAME
model (docs/explainers/one-parent-mlr-equals-std.md), so their BICs differ only by rounding
(~1e-13). Without a tolerance, rounding decides such ties (it did in Phase 1:
docs/reports/phase-1.md, "What we tried that didn't work").

Convergence: MLR and OLR are fitted by iterative optimizers. Each fit records whether its
optimizer reported convergence (statsmodels `mle_retvals["converged"]`); a fit that did not
converge may have a too-low log-likelihood, so its BIC would be unreliable. `fit_cpt_types`
writes the flags into the output CSV and `scripts/fit_cpt_types.py` prints any failures.

Run the whole fit: `python scripts/fit_cpt_types.py [--structure hc]` (or `make phase-1.5`).
"""

import warnings
from dataclasses import dataclass

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.discrete.discrete_model import MNLogit
from statsmodels.miscmodels.ordinal_model import OrderedModel

from bnjoint import config

# The three types, in the order of the output columns (bic_std, bic_mlr, bic_olr). This is NOT
# the tie-break order; that is config.TIE_ORDER (STD, OLR, MLR).
CPT_TYPES: tuple[str, ...] = ("STD", "MLR", "OLR")


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


@dataclass
class Fit:
    """The result of one iterative fit (MLR or OLR).

    Attributes:
        loglik: maximized log-likelihood, or -inf if the fit raised an error.
        converged: True/False as reported by the optimizer; False if the fit raised an error.
    """

    loglik: float
    converged: bool


def _converged(result) -> bool:
    """Read the optimizer's own convergence flag from a statsmodels result.

    `mle_retvals` is a dict statsmodels fills in after fitting; its "converged" entry is True
    when the optimizer stopped because the gradient was ~0 (a maximum), and False when it
    stopped because it ran out of iterations. Missing key -> treated as not converged.
    """
    return bool(result.mle_retvals.get("converged", False))


def fit_mlr(df: pd.DataFrame, child: str, parents: list[str], k: int = config.K_STATES) -> Fit:
    """Fit multinomial logistic regression (statsmodels MNLogit, Newton's method by default).

    Args:
        df: the data. child: the child column. parents: parent columns (may be empty).
        k: number of states (only used to check the design matrix).

    Returns:
        A `Fit`. If statsmodels raises an error, the error is printed and the result is
        Fit(-inf, False), so this type can never win.

    Example:
        >>> fit_mlr(df, "a3", ["a4"])   # doctest: +SKIP
        Fit(loglik=-1120.27..., converged=True)
    """
    try:
        result = MNLogit(df[child], mlr_design(df, parents, k)).fit(disp=0)  # disp=0: quiet
    except Exception as e:  # report and give the type no chance of winning
        print(f"[{child}] MLR fit failed: {e}")
        return Fit(-np.inf, False)
    return Fit(result.llf, _converged(result))  # llf = log-likelihood at the fitted parameters


def bic_mlr(df: pd.DataFrame, child: str, parents: list[str], k: int, w: float) -> float:
    """BIC of multinomial logistic regression; -inf if the fit fails. `w` = penalty weight.

    Example:
        >>> bic_mlr(df, "a3", ["a4"], k=3, w=penalty_weight(len(df)))   # doctest: +SKIP
        -1142.508...
    """
    return fit_mlr(df, child, parents, k).loglik - w * n_params_mlr(len(parents), k)


# ---------------------------------------------------------------- OLR
def fit_olr(df: pd.DataFrame, child: str, parents: list[str]) -> Fit | None:
    """Fit ordinal logistic regression (statsmodels OrderedModel, logit link, BFGS optimizer).

    Parents enter as their raw values -1/0/1, one slope each (NOT dummy-coded; decision 8).
    A node without parents is not fitted (decision 9): the result is None.

    Returns:
        A `Fit`, Fit(-inf, False) if statsmodels raises an error, or None without parents.

    Example:
        >>> fit_olr(pd.DataFrame({"y": [0, 1]}), "y", []) is None
        True
    """
    if not parents:
        return None
    try:
        model = OrderedModel(df[child], df[parents].astype(float), distr="logit")
        result = model.fit(method="bfgs", disp=0)
    except Exception as e:
        print(f"[{child}] OLR fit failed: {e}")
        return Fit(-np.inf, False)
    return Fit(result.llf, _converged(result))


def bic_olr(df: pd.DataFrame, child: str, parents: list[str], k: int, w: float) -> float:
    """BIC of ordinal logistic regression; -inf without parents or if the fit fails.

    Example:
        >>> bic_olr(pd.DataFrame({"y": [0, 1]}), "y", [], k=3, w=1.0)
        -inf
    """
    fit = fit_olr(df, child, parents)
    if fit is None:
        return -np.inf
    return fit.loglik - w * n_params_olr(len(parents), k)


# ---------------------------------------------------------------- per family and whole network
@dataclass
class FamilyScores:
    """BIC of the three CPT types for one family, plus the convergence flags.

    Attributes:
        bic: {"STD": ..., "MLR": ..., "OLR": ...}; OLR is -inf for a node without parents.
        converged: {"MLR": bool, "OLR": bool or None}; None means "not fitted" (no parents).
            STD has no flag: its maximum is a closed formula (counts), not an optimizer.
    """

    bic: dict[str, float]
    converged: dict[str, bool | None]


def score_family(
    df: pd.DataFrame, child: str, parents: list[str], k: int = config.K_STATES
) -> FamilyScores:
    """Score all three CPT types for one family (each model is fitted exactly once).

    Example:
        >>> score_family(df, "a3", ["a4"])   # doctest: +SKIP
        FamilyScores(bic={'STD': -1142.508..., 'MLR': -1142.508..., 'OLR': -1159.886...},
                     converged={'MLR': True, 'OLR': True})
    """
    w = penalty_weight(len(df))
    n = len(parents)
    mlr = fit_mlr(df, child, parents, k)
    olr = fit_olr(df, child, parents)
    return FamilyScores(
        bic={
            "STD": bic_std(df, child, parents, k, w),
            "MLR": mlr.loglik - w * n_params_mlr(n, k),
            "OLR": -np.inf if olr is None else olr.loglik - w * n_params_olr(n, k),
        },
        converged={"MLR": mlr.converged, "OLR": None if olr is None else olr.converged},
    )


def pick_winner(
    scores: dict[str, float],
    tol: float = config.TIE_TOLERANCE,
    order: tuple[str, ...] = config.TIE_ORDER,
) -> str:
    """Return the winning CPT type under the tie rule (see the module docstring).

    Step by step: find the best score; every type within `tol` of it is "tied for best";
    of those, return the one that comes first in `order` (STD, OLR, MLR).

    Args:
        scores: {"STD": bic, "MLR": bic, "OLR": bic}; -inf is allowed.
        tol: tie tolerance (default 1e-6).
        order: preference among tied types (default simplest first).

    Example:
        >>> pick_winner({"STD": -9.0, "MLR": -9.0 + 1e-13, "OLR": -10.0})   # rounding noise
        'STD'
        >>> pick_winner({"STD": -9.0, "MLR": -8.0, "OLR": -10.0})           # a real difference
        'MLR'
    """
    best = max(scores.values())
    tied = [t for t in order if scores[t] >= best - tol]
    return tied[0]


def fit_cpt_types(
    df: pd.DataFrame,
    parents_by_var: dict[str, list[str]],
    varnames: list[str],
    k: int = config.K_STATES,
) -> pd.DataFrame:
    """Score every family of a network and pick each node's CPT type.

    Args:
        df: the data (values -1/0/1).
        parents_by_var: {child: [parents]}, e.g. from `gobnilp_io.parse_parent_sets` or
            `structures.read_adjacency_csv`.
        varnames: the variables, in the order the output rows should have.
        k: number of states.

    Returns:
        DataFrame with columns variable, n_parents, parents (";"-separated, as in
        data/reference/kybernetika-table2.csv), bic_std, bic_mlr, bic_olr, mlr_converged,
        olr_converged (empty for a node without parents), winner.

    Example:
        >>> fit_cpt_types(df, {"a3": ["a4"], "a4": []}, ["a3", "a4"])   # doctest: +SKIP
          variable  n_parents parents      bic_std  ...  winner
        0       a3          1      a4 -1142.508...  ...     STD
    """
    rows = []
    for v in varnames:
        parents = parents_by_var[v]
        fam = score_family(df, v, parents, k)
        rows.append(
            {
                "variable": v,
                "n_parents": len(parents),
                "parents": ";".join(parents),
                "bic_std": fam.bic["STD"],
                "bic_mlr": fam.bic["MLR"],
                "bic_olr": fam.bic["OLR"],
                "mlr_converged": fam.converged["MLR"],
                "olr_converged": fam.converged["OLR"],
                "winner": pick_winner(fam.bic),
            }
        )
    return pd.DataFrame(rows)
