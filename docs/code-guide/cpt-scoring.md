# Code guide: CPT scoring (STD, MLR, OLR)

**What it does.** For a fixed network structure, `bnjoint.cpt_scores` computes, for every
node, the BIC of three ways of writing its conditional probability table (CPT) and picks the
best. In Phase 1 this is the second stage of the two-stage method; from Phase 2 on the same
functions score candidate parent sets for joint learning. Entry point:
`scripts/fit_cpt_types.py` → `results/phase1/cpt-type-summary.csv`.

## Data flow

```
BN-data.csv ──► read_bn_data ──┐
GOBNILP log ──► parse_parent_sets ─► fit_cpt_types ─► for each node: score_family ─► pick_winner ─► CSV
                                                          ├─ bic_std  (counts)
                                                          ├─ bic_mlr  (statsmodels MNLogit)
                                                          └─ bic_olr  (statsmodels OrderedModel)
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
- **`mlr_design` + `bic_mlr`**: each parent becomes two 0/1 "dummy" columns (state 0? state +1?;
  −1 is the reference), plus a constant. `MNLogit` fits one logistic equation per non-reference
  child state.
- **`bic_olr`**: parents enter as plain numbers −1/0/+1 with a single slope each; the child's
  states are treated as ordered. Nodes without parents get −∞ (OLR is not used there).
- **`pick_winner`**: highest BIC; exact ties go to the first of STD, MLR, OLR.

## Why it is designed this way

- **One module, one copy of the math** (CLAUDE.md): joint learning in Phase 2 must give
  exactly the numbers the two-stage method gives for the same family.
- **statsmodels** for MLR/OLR: it reports the maximized log-likelihood (`.llf`) directly.
  Alternatives (scikit-learn) add regularization by default, which would change the BIC.
- **Failed fits become −∞** and print a message, so a failure can never silently win.
- **The STD summation order is kept exactly as in Phase 1**, so floating-point results are
  bit-for-bit the same (checked by `tests/test_phase1_regression.py`).

## Known issues (to be fixed in later steps, not here)

- **Tie-breaking** (step 1.5.1): MLR with one parent has the same fitted distribution as STD,
  but their BICs differ by rounding (~1e-13), so `max` picks whichever happens to be larger.
  This produced the reported 10/30/4 split; with a 1e-6 tolerance it is 16/24/4
  (`docs/reports/1.5.0a.md`).
- **Convergence** is not yet checked (step 1.5.1).
- **Parent coding for OLR** (raw values) is still to be confirmed with Jirka (decision log
  entry 8).

## How to run and change it

`python scripts/fit_cpt_types.py --log <gobnilp log> --out <csv>`; see `--help`. To change a
formula, change it here only and run `make test`; the regression test will tell you if a
reported Phase 1 number moved, which then needs a decision log entry.
