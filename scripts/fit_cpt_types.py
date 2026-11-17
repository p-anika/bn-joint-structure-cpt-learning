"""Two-stage step 2: for a fixed structure, score STD, MLR and OLR for every node and pick one.

Inputs:  data/raw/BN-data.csv, a learned structure, the variable-names file.
         The structure is either a GOBNILP console log (--structure gobnilp, default
         results/phase1/gobnilp-std-run.log) or a bnlearn adjacency-matrix CSV
         (--structure hc, default results/phase1/bnlearn-hc-dag.csv).
Output:  a CSV with columns variable, n_parents, parents, bic_std, bic_mlr, bic_olr,
         mlr_converged, olr_converged, winner. Default:
         results/phase1.5/1.5.1-gobnilp-tie-fix/cpt-type-summary.csv (gobnilp) or
         results/phase1.5/1.5.2-hc-vs-table2/cpt-type-summary-hc.csv (hc).
         The console output lists the split and every fit that did not converge.
Run:     python scripts/fit_cpt_types.py                       (GOBNILP structure)
         python scripts/fit_cpt_types.py --structure hc        (hill-climbing structure)
         python scripts/fit_cpt_types.py --structure gobnilp --structure-file other.log --out x.csv
         (normally via `make phase1.5`)

The math (including the 1e-6 tie rule) is in `bnjoint.cpt_scores`; reading structures in
`bnjoint.gobnilp_io` and `bnjoint.structures`. Walkthrough: docs/code-guide/cpt-scoring.md.
"""

import argparse
from pathlib import Path

from bnjoint import config
from bnjoint.cpt_scores import fit_cpt_types
from bnjoint.gobnilp_io import parse_parent_sets
from bnjoint.io import read_bn_data
from bnjoint.structures import read_adjacency_csv

# --structure value -> (default structure file, default output CSV)
DEFAULTS = {
    "gobnilp": (config.PHASE1_GOBNILP_LOG, config.STEP151_CPT_SUMMARY),
    "hc": (config.PHASE1_HC_DAG_CSV, config.STEP152_CPT_SUMMARY),
}


def read_structure(kind: str, path: Path, varnames: list[str]) -> dict[str, list[str]]:
    """Read {child: [parents]} from a GOBNILP log ("gobnilp") or an adjacency CSV ("hc").

    Example:
        >>> read_structure("hc", config.PHASE1_HC_DAG_CSV, names)["a3"]   # doctest: +SKIP
        []
    """
    if kind == "gobnilp":
        return parse_parent_sets(path.read_text(), varnames)
    return read_adjacency_csv(path, varnames)


def main() -> None:
    """Parse arguments, read data and structure, fit, write the CSV, print split + convergence."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--structure", choices=sorted(DEFAULTS), default="gobnilp")
    parser.add_argument(
        "--structure-file", type=Path, help="GOBNILP log or adjacency CSV (default by type)"
    )
    parser.add_argument("--data", type=Path, default=config.BN_DATA_CSV, help="data CSV")
    parser.add_argument(
        "--varnames", type=Path, default=config.VARNAMES_FILE, help="variable-names file"
    )
    parser.add_argument("--out", type=Path, help="output CSV (default by structure type)")
    args = parser.parse_args()
    default_file, default_out = DEFAULTS[args.structure]
    structure_file = args.structure_file or default_file
    out = args.out or default_out

    df = read_bn_data(args.data)
    varnames = args.varnames.read_text().split()
    if list(df.columns) != varnames:
        raise ValueError(f"columns of {args.data} do not match {args.varnames}")

    parents = read_structure(args.structure, structure_file, varnames)
    n_arcs = sum(len(p) for p in parents.values())
    print(
        f"Structure ({args.structure}) from {structure_file}: {len(parents)} nodes, {n_arcs} arcs"
    )

    summary = fit_cpt_types(df, parents, varnames)
    out.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(out, index=False)

    # Convergence report: OLR is only fitted for nodes with parents (olr_converged empty else)
    fitted_olr = summary[summary["n_parents"] > 0]
    n_mlr_ok = int(summary["mlr_converged"].eq(True).sum())
    n_olr_ok = int(fitted_olr["olr_converged"].eq(True).sum())
    print(f"MLR fits converged: {n_mlr_ok}/{len(summary)}")
    print(f"OLR fits converged: {n_olr_ok}/{len(fitted_olr)} (nodes without parents not fitted)")
    for row in summary.itertuples(index=False):
        if row.mlr_converged is not True:
            print(f"  NOT CONVERGED: MLR for {row.variable} | {row.parents}")
        if row.n_parents > 0 and row.olr_converged is not True:
            print(f"  NOT CONVERGED: OLR for {row.variable} | {row.parents}")

    counts = summary["winner"].value_counts()
    split = ", ".join(f"{t} {counts.get(t, 0)}" for t in ("STD", "MLR", "OLR"))
    print(f"Wrote {out}: {split}")


if __name__ == "__main__":
    main()
