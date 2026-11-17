"""Read network structures that do not come from GOBNILP, and compare per-node results with a
published reference table.

Inputs:
  - an adjacency-matrix CSV written by R's `write.csv(amat(dag))`, e.g.
    `results/phase-1/bnlearn-hc-dag.csv` (made by `R/bnlearn_hc.R`). Row = parent,
    column = child, 1 = arc, first column = the row names.
  - a reference table typed in from a paper, e.g. `data/reference/kybernetika-table2.csv`
    (columns variable, n_parents, parents separated by ";", cpt_type).
Output: Python dicts {child: [parents]} and a node-by-node comparison DataFrame.
Used by: `scripts/fit_cpt_types.py --structure hc` and `scripts/compare_with_table2.py`
(step 1.5.2). Walkthrough: docs/code-guide/cpt-scoring.md.

(Parent sets from a GOBNILP log are read by `bnjoint.gobnilp_io` instead.)
"""

from pathlib import Path

import pandas as pd


def read_adjacency_csv(path: Path, varnames: list[str]) -> dict[str, list[str]]:
    """Turn an adjacency-matrix CSV into {child: [parents]}.

    Parents are listed in the order of `varnames` (the matrix rows). Order does not affect any
    score; it only affects how the `parents` column of the output CSV is written.

    Args:
        path: the CSV (row = parent, column = child, 1 = arc).
        varnames: all variable names; the rows and the columns must be exactly these.

    Raises:
        ValueError: if the row or column names differ from `varnames`, or a value is not 0/1.

    Example:
        >>> read_adjacency_csv(config.PHASE1_HC_DAG_CSV, names)["a2"]   # doctest: +SKIP
        ['a4', 'a18']
    """
    adj = pd.read_csv(path, index_col=0)  # index_col=0: first column = row names
    if list(adj.index) != varnames or list(adj.columns) != varnames:
        raise ValueError(f"rows/columns of {path} are not the expected {len(varnames)} names")
    if not adj.isin([0, 1]).all().all():
        raise ValueError(f"{path} contains values other than 0 and 1")
    return {child: [p for p in varnames if adj.loc[p, child] == 1] for child in varnames}


def read_reference_table(path: Path) -> dict[str, tuple[list[str], str]]:
    """Read a typed-in reference table into {variable: ([parents], cpt_type)}.

    `keep_default_na=False` keeps an empty parents cell as "" (pandas would otherwise turn it
    into NaN, a float); "" then becomes the empty list.

    Raises:
        ValueError: if a row's `n_parents` does not match its parents list (a typing check).

    Example:
        >>> read_reference_table(config.KYBERNETIKA_TABLE2)["a2"]   # doctest: +SKIP
        (['a4', 'a18'], 'MLR')
    """
    table = pd.read_csv(path, keep_default_na=False, dtype=str)
    ref = {}
    for row in table.itertuples(index=False):
        parents = [p for p in row.parents.split(";") if p]
        if len(parents) != int(row.n_parents):
            raise ValueError(f"{path}: {row.variable} has n_parents={row.n_parents} but {parents}")
        ref[row.variable] = (parents, row.cpt_type)
    return ref


def compare_with_reference(
    summary: pd.DataFrame, reference: dict[str, tuple[list[str], str]]
) -> pd.DataFrame:
    """Compare our result node by node with a reference table.

    Args:
        summary: output of `cpt_scores.fit_cpt_types` (needs variable, parents, winner).
        reference: output of `read_reference_table`.

    Returns:
        DataFrame with columns variable, parents_ours, parents_ref, same_parents, type_ours,
        type_ref, same_type. Parent sets are compared as SETS (order ignored).

    Example:
        >>> compare_with_reference(summary, ref)["same_type"].all()   # doctest: +SKIP
        True
    """
    rows = []
    for row in summary.itertuples(index=False):
        ours = [p for p in row.parents.split(";") if p]
        ref_parents, ref_type = reference[row.variable]
        rows.append(
            {
                "variable": row.variable,
                "parents_ours": ";".join(ours),
                "parents_ref": ";".join(ref_parents),
                "same_parents": set(ours) == set(ref_parents),
                "type_ours": row.winner,
                "type_ref": ref_type,
                "same_type": row.winner == ref_type,
            }
        )
    return pd.DataFrame(rows)
