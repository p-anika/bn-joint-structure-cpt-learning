# results/phase1/: Phase 1 two-stage baseline

Command: `make phase1` (stages and design: `docs/code-guide/phase1-pipeline.md`).
Write-up of the results: [`docs/reports/phase-1.md`](../../docs/reports/phase-1.md).
Moved here from `results/` in step 1.5.0b; contents unchanged.

| File | What it is | Made by | Status |
|---|---|---|---|
| `gobnilp-std-run.log` | GOBNILP console log: the exact BIC-optimal structure with STD tables (`child:-{parents}` lines), solve statistics, build details | `make phase1` stage 4; commit `fd2b479`, Sep 6, 2026 | Reported to Jirka. Current. |
| `cpt-type-summary.csv` | Per node: number of parents, BIC of STD/MLR/OLR, winner | `make phase1` stage 5 (`scripts/fit_cpt_types.py`); commit `fd2b479`, Sep 6, 2026 | Reported to Jirka. **Its winner column has the known tie bug** (10/30/4 split); a corrected file comes in step 1.5.1, and this file will then be marked superseded. |
| `bnlearn-hc-dag.csv` | Adjacency matrix of the bnlearn hill-climbing structure (row = parent, column = child) | `make phase1` stage 6 (`R/bnlearn_hc.R`); commit `a53bdd9`, Sep 7, 2026 | Current. |
| `adjmat.txt`, `adjmat.dot` | The GOBNILP DAG as a 44 × 44 adjacency matrix (row = parent, column = child) and as a Graphviz drawing | `make phase1` stage 4 (GOBNILP writes them automatically); added in step 1.5.0b | Current. For step 1.5.3. |
| `pdagadjmat.txt`, `pdagadjmat.dot` | The CPDAG of that DAG (arcs whose direction is not determined by the data are undirected) | same | Current. For step 1.5.3. |

The log's timing lines differ on every run; a re-run counts as "the same" when the objective
and all `child:-{…}` lines are unchanged.
