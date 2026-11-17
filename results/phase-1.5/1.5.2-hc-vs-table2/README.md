# results/phase-1.5/1.5.2-hc-vs-table2/

CPT types per node on the bnlearn hill-climbing (hc) structure (`results/phase-1/bnlearn-hc-dag.csv`,
the method the Kybernetika paper used), with the same tie rule and convergence check as
step 1.5.1, compared node by node with Table 2 of
[Vomlel, Kybernetika 62(3) 2026](../../../docs/references.md#vomlel2026), p. 411
(`data/reference/kybernetika-table2.csv`). Write-up:
[`docs/reports/phase-1.5.md`](../../../docs/reports/phase-1.5.md).

Commands (both run by `make phase-1.5`):
`python scripts/fit_cpt_types.py --structure hc --structure-file results/phase-1/bnlearn-hc-dag.csv --varnames data/processed/bn-data-44-varnames.txt --out results/phase-1.5/1.5.2-hc-vs-table2/cpt-type-summary-hc.csv`, then
`python scripts/compare_with_table2.py --ours results/phase-1.5/1.5.2-hc-vs-table2/cpt-type-summary-hc.csv --reference data/reference/kybernetika-table2.csv --out results/phase-1.5/1.5.2-hc-vs-table2/table2-comparison.csv`.
Made 2026-11-16 on branch `step-1.5.1` (working tree on `cc1d09d`); the commit on `main` is
the one for steps 1.5.1–1.5.2 (`git log -- results/phase-1.5` shows it).

| File | What it is | Status |
|---|---|---|
| `cpt-type-summary-hc.csv` | Same columns as `../1.5.1-gobnilp-tie-fix/cpt-type-summary.csv`, for the hc structure. Derived. | Current. Checked byte for byte by `tests/test_regression.py`. |
| `table2-comparison.csv` | One row per node: `variable`, `parents_ours`, `parents_ref`, `same_parents`, `type_ours`, `type_ref`, `same_type` (parent sets compared as sets). Derived. | Current. |
| `fit-log.txt` | Console output of the fitting command (convergence counts, split). Derived. | Current. |
| `comparison-log.txt` | Console output of the comparison (both splits, number of matching nodes, any node that differs). Derived. | Current. |
