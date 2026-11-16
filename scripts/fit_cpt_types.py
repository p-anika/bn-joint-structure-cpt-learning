"""Two-stage step 2: for a fixed structure, score STD, MLR and OLR for every node and pick one.

Inputs:  data/raw/BN-data.csv, a GOBNILP console log with the learned structure
         (default results/phase1/gobnilp-std-run.log), the variable-names file
Output:  a CSV with columns variable, n_parents, bic_std, bic_mlr, bic_olr, winner
         (default results/phase1/cpt-type-summary.csv)
Run:     python scripts/fit_cpt_types.py
         python scripts/fit_cpt_types.py --log other.log --out other.csv

The math is in `bnjoint.cpt_scores`; the log parsing in `bnjoint.gobnilp_io`.
Walkthrough: docs/code-guide/cpt-scoring.md.

Note: the winner rule is still the Phase 1 rule (no tie tolerance). Step 1.5.1 changes it.
"""

import argparse
from pathlib import Path

from bnjoint import config
from bnjoint.cpt_scores import fit_cpt_types
from bnjoint.gobnilp_io import parse_parent_sets
from bnjoint.io import read_bn_data


def main() -> None:
    """Parse arguments, read data and structure, fit, write the CSV, print the split."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--data", type=Path, default=config.BN_DATA_CSV, help="data CSV")
    parser.add_argument(
        "--log", type=Path, default=config.PHASE1_GOBNILP_LOG, help="GOBNILP console log"
    )
    parser.add_argument(
        "--varnames", type=Path, default=config.VARNAMES_FILE, help="variable-names file"
    )
    parser.add_argument("--out", type=Path, default=config.PHASE1_CPT_SUMMARY, help="output CSV")
    args = parser.parse_args()

    df = read_bn_data(args.data)
    varnames = args.varnames.read_text().split()
    if list(df.columns) != varnames:
        raise ValueError(f"columns of {args.data} do not match {args.varnames}")

    parents = parse_parent_sets(args.log.read_text(), varnames)
    n_arcs = sum(len(p) for p in parents.values())
    print(f"Structure from {args.log}: {len(parents)} nodes, {n_arcs} arcs")

    summary = fit_cpt_types(df, parents, varnames)
    summary.to_csv(args.out, index=False)
    counts = summary["winner"].value_counts()
    split = ", ".join(f"{t} {counts.get(t, 0)}" for t in ("STD", "MLR", "OLR"))
    print(f"Wrote {args.out}: {split}")


if __name__ == "__main__":
    main()
