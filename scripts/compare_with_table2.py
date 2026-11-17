"""Step 1.5.2: compare our CPT types on the hill-climbing structure with the paper's Table 2.

Inputs:  our per-node result (default results/phase-1.5/1.5.2-hc-vs-table2/cpt-type-summary-hc.csv,
         made by `python scripts/fit_cpt_types.py --structure hc`) and the reference table
         data/reference/kybernetika-table2.csv (Vomlel, Kybernetika 62(3) 2026, Table 2, p. 411).
Output:  a CSV with one row per node: variable, parents_ours, parents_ref, same_parents,
         type_ours, type_ref, same_type (default .../table2-comparison.csv); the console
         shows both splits and lists every node that differs.
Run:     python scripts/compare_with_table2.py      (normally via `make phase-1.5`)

Logic lives in `bnjoint.structures.compare_with_reference`.
"""

import argparse
from pathlib import Path

import pandas as pd

from bnjoint import config
from bnjoint.structures import compare_with_reference, read_reference_table


def main() -> None:
    """Read both tables, compare, write the CSV, print the summary."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--ours", type=Path, default=config.STEP152_CPT_SUMMARY)
    parser.add_argument("--reference", type=Path, default=config.KYBERNETIKA_TABLE2)
    parser.add_argument("--out", type=Path, default=config.STEP152_COMPARISON)
    args = parser.parse_args()

    # keep_default_na=False: an empty parents cell stays "" instead of becoming NaN
    ours = pd.read_csv(args.ours, keep_default_na=False)
    cmp = compare_with_reference(ours, read_reference_table(args.reference))
    cmp.to_csv(args.out, index=False)

    def split(col: str) -> str:
        counts = cmp[col].value_counts()
        return "/".join(str(counts.get(t, 0)) for t in ("STD", "MLR", "OLR"))

    print(f"Split STD/MLR/OLR: ours {split('type_ours')}, reference {split('type_ref')}")
    print(f"Same parent set: {int(cmp['same_parents'].sum())}/{len(cmp)} nodes")
    print(f"Same CPT type:   {int(cmp['same_type'].sum())}/{len(cmp)} nodes")
    for row in cmp[~(cmp["same_parents"] & cmp["same_type"])].itertuples(index=False):
        print(
            f"  DIFFERS: {row.variable}: ours {row.parents_ours} {row.type_ours}, "
            f"reference {row.parents_ref} {row.type_ref}"
        )
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
