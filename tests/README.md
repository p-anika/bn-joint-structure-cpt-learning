# tests/: automatic tests (pytest)

Run all of them with `make test` (about 10–20 seconds). Each file tests one module of
`src/bnjoint/`. A test that fails is reported, never weakened or deleted (CLAUDE.md).

| File | What it checks |
|---|---|
| `test_io.py` | BN-data.csv is 1661 × 44 with values −1/0/1; the `.dat` format; the package rebuilds `bn-data-44.dat` and the names file byte for byte |
| `test_gobnilp_io.py` | Parent sets are read correctly from GOBNILP log lines (including an empty parent set); arc-only lines are ignored; the Phase 1 log has 44 families and 69 arcs |
| `test_cpt_scores.py` | Parameter counts for STD/MLR/OLR; BIC on a 4-row example worked out by hand; MLR = STD for 0 and 1 parents (synthetic and all 18 such families of our data); convergence flags; the tie rule (1e-6; STD, OLR, MLR) |
| `test_structures.py` | Reading adjacency-matrix CSVs and reference tables; per-node comparison; the hc arcs equal Table 2's |
| `test_phase1_regression.py` | The BIC columns of the CPT-type CSV reported in Phase 1 (read from git: `git show 9d80757:results/phase1/cpt-type-summary.csv`) are reproduced exactly and only the six expected winners change; all fits converge; the `results/phase1.5/` CSVs are reproduced byte for byte; the hc result matches Table 2 on all 44 nodes (~10–20 s) |

All are originals written by us.
