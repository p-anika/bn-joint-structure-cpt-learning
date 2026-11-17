# results/phase1.5/1.5.1-gobnilp-tie-fix/

CPT types (STD / MLR / OLR) per node on the exact GOBNILP structure of Phase 1, with the tie
rule of CLAUDE.md (BICs within 1e-6 are tied; ties go to STD, then OLR, then MLR) and a
convergence check of every MLR and OLR fit. Write-up and numbers:
[`docs/reports/1.5.1-1.5.2.md`](../../../docs/reports/1.5.1-1.5.2.md).

Command: `make phase1.5` (rule `$(CPT151)`), i.e.
`python scripts/fit_cpt_types.py --structure gobnilp --structure-file results/phase1/gobnilp-std-run.log --varnames data/processed/bn-data-44-varnames.txt --out results/phase1.5/1.5.1-gobnilp-tie-fix/cpt-type-summary.csv`.
Made 2026-11-16 on branch `step-1.5.1` (working tree on `cc1d09d`); the commit on `main` is
the one for steps 1.5.1–1.5.2 (`git log -- results/phase1.5` shows it).

| File | What it is | Status |
|---|---|---|
| `cpt-type-summary.csv` | One row per node: `variable`, `n_parents`, `parents` (`;`-separated), `bic_std`, `bic_mlr`, `bic_olr` (−inf = OLR not fitted, node has no parents), `mlr_converged`, `olr_converged` (empty = not fitted), `winner`. Derived. | Current. **Supersedes `results/phase1/cpt-type-summary.csv`** (same BIC values to the last digit; 6 winners corrected). Checked byte for byte by `tests/test_phase1_regression.py`. |
| `fit-log.txt` | Console output of the command: structure size, convergence counts, any non-converged fit, the split. Derived. | Current. |
