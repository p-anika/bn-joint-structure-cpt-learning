# R/: R scripts (bnlearn)

Run from the repo root with `Rscript R/<script>.R [arguments]`. Package versions are in
`docs/setup.md`.

| File | Job | Called by |
|---|---|---|
| `bnlearn_hc.R` | Hill-climbing structure with BIC (how the paper's structure was learned); writes `results/phase-1/bnlearn-hc-dag.csv` | `make phase-1` |
| `convert_jirka_aug5.R` | Re-runs Jirka's Aug 5 conversion (his code, verbatim) on `preprocessed-data.csv` and checks it reproduces `BN-data.csv` | `make provenance` |

Both are written by us, except the block in `convert_jirka_aug5.R` marked as verbatim from
Jirka's email.
