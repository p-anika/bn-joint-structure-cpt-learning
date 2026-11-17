# Code guide: CPT scoring (STD, MLR, OLR)

**What it does.** For a fixed network structure, `bnjoint.cpt_scores` computes, for every
node, the BIC of three ways of writing its conditional probability table (CPT) and picks the
best. In Phase 1 this is the second stage of the two-stage method; from Phase 2 on the same
functions score candidate parent sets for joint learning. Entry point:
`scripts/fit_cpt_types.py --structure gobnilp|hc` → `results/phase1.5/<step>-…/cpt-type-summary*.csv`
(`make phase1.5`). Concepts: explainers [03](../explainers/03-cpt-types.md) (the three types) and
[04](../explainers/04-one-parent-mlr-equals-std.md) (why 1-parent MLR = STD, and the tie rule).

## Data flow

```
BN-data.csv ─────► read_bn_data ─────────────┐
GOBNILP log ─────► parse_parent_sets ───┐    │
  or hc adjacency CSV ► read_adjacency_csv ┴─► fit_cpt_types ─► per node: score_family ─► pick_winner ─► CSV
                                                      ├─ bic_std  (counts, closed form)
                                                      ├─ fit_mlr  (statsmodels MNLogit)      ─► LL + converged?
                                                      └─ fit_olr  (statsmodels OrderedModel) ─► LL + converged?

summary CSV (hc) + data/reference/kybernetika-table2.csv ─► compare_with_reference ─► table2-comparison.csv
                                                            (scripts/compare_with_table2.py)
```

## Walkthrough

All functions have docstrings with the formulas and an example; this is the overview.

- **`penalty_weight(N)`** = log(N)/2, the BIC price of one parameter. For N = 1661 it is about
  3.71, so a new parameter must raise the log-likelihood by more than 3.71 to pay for itself.
- **`n_params_std / n_params_mlr / n_params_olr`**: the parameter counts of CLAUDE.md. With 2
  parents: 18 (STD), 10 (MLR), 4 (OLR). This is why MLR/OLR can win: they need far fewer
  parameters than a full table when a node has several parents.
- **`loglik_std`**: groups the rows by parent configuration and adds up
  count × log(relative frequency). That is the exact maximum of the likelihood for a table, so
  no fitting is needed.
- **`mlr_design` + `fit_mlr`**: each parent becomes two 0/1 "dummy" columns (state 0? state +1?;
  −1 is the reference), plus a constant. `MNLogit` fits one logistic equation per non-reference
  child state. Returns a `Fit` (log-likelihood + converged flag); `bic_mlr` subtracts the penalty.
- **`fit_olr`**: parents enter as plain numbers −1/0/+1 with a single slope each; the child's
  states are treated as ordered. Nodes without parents return `None` (not fitted), which
  `score_family` turns into BIC −∞ and flag `None`.
- **`_converged`**: reads statsmodels' own flag `result.mle_retvals["converged"]`: True when the
  optimizer stopped at a maximum, False when it ran out of iterations.
- **`score_family`** fits each model once and returns a `FamilyScores` (the three BICs and the
  two convergence flags).
- **`pick_winner`** (step 1.5.1): best score; everything within 1e-6 of it is tied; the first
  tied type in (STD, OLR, MLR) wins. Constants `TIE_TOLERANCE`, `TIE_ORDER` live in `config.py`.
- **`fit_cpt_types`** loops over the nodes and returns the table that becomes the CSV (columns
  in its docstring), including `parents` and both convergence flags.
- **`bnjoint.structures`** (step 1.5.2): `read_adjacency_csv` reads bnlearn's adjacency matrix;
  `read_reference_table` reads Table 2 (and checks each row's `n_parents`);
  `compare_with_reference` compares parent **sets** and types node by node.

## Why it is designed this way

- **One module, one copy of the math** (CLAUDE.md): joint learning in Phase 2 must give
  exactly the numbers the two-stage method gives for the same family.
- **statsmodels** for MLR/OLR: it reports the maximized log-likelihood (`.llf`) directly.
  Alternatives (scikit-learn) add regularization by default, which would change the BIC.
- **Failed fits become −∞** and print a message, so a failure can never silently win.
- **The STD summation order is kept exactly as in Phase 1**, so floating-point results are
  bit-for-bit the same (checked by `tests/test_phase1_regression.py`).
- **Tie rule with a tolerance** rather than `max`: two types that are the same model must not
  be separated by rounding noise (explainer 04). Rejected: rounding scores before comparing
  (rounding can still split two near-equal numbers across a boundary, e.g. 0.49999 vs 0.50001).
- **Convergence flags in the CSV** rather than only a printed warning: the flag stays next to
  the number it qualifies, and a test (`test_all_fits_converged`) fails if any fit stops
  converging.
- **One `--structure` option** instead of a second script for hc: the fitting is identical,
  only the reader differs.
- **Parent sets compared as sets** with Table 2: the order in which parents are listed means
  nothing.

## Open questions

- **Parent coding for OLR** (raw values −1/0/1) is still to be confirmed with Jirka (decision log
  entry 8). Step 1.5.2 reproduces Table 2 exactly with it, which is strong evidence that it is
  what the paper did.

## How to run and change it

```bash
make phase1.5                                              # both structures + Table 2 comparison
python scripts/fit_cpt_types.py --structure hc --out /tmp/x.csv   # one structure, elsewhere
python scripts/fit_cpt_types.py --structure gobnilp --structure-file other.log --out other.csv
```

See `--help`. To change a formula, change it here only and run `make test`.
`tests/test_phase1_regression.py` then tells you whether a reported number moved (the Phase 1
BIC columns, the 1.5.1 and 1.5.2 CSVs, or the match with Table 2); a moved number needs a
decision log entry, a new results folder and a History line in the report, never an edited CSV. To change the tie
tolerance or order, edit `config.py` only.
