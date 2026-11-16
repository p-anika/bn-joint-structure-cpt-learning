# tests/: automatic tests (pytest)

Run all of them with `make test` (about 5 seconds). Each file tests one module of
`src/bnjoint/`. A test that fails is reported, never weakened or deleted (CLAUDE.md).

| File | What it checks |
|---|---|
| `test_io.py` | BN-data.csv is 1661 × 44 with values −1/0/1; the `.dat` format; the package rebuilds `bn-data-44.dat` and the names file byte for byte |
| `test_gobnilp_io.py` | Parent sets are read correctly from GOBNILP log lines (including an empty parent set); arc-only lines are ignored; the Phase 1 log has 44 families and 69 arcs |
| `test_cpt_scores.py` | Parameter counts for STD/MLR/OLR; BIC on a 4-row example worked out by hand; the current winner rule (including the known no-tolerance behaviour that step 1.5.1 fixes) |
| `test_phase1_regression.py` | The refactored code reproduces `results/phase1/cpt-type-summary.csv` exactly |

All are originals written by us.
