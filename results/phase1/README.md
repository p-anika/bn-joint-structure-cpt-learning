# results/phase1/: Phase 1 structures

The two Phase 1 structures: the exact BIC-optimal structure (GOBNILP) and the bnlearn
hill-climbing structure. Write-up: [`docs/reports/phase-1.md`](../../docs/reports/phase-1.md).
The CPT types on these structures are in [`results/phase1.5/`](../phase1.5/README.md).

Command: `make phase1` (stages and design: `docs/code-guide/phase1-pipeline.md`). These are
the files reported to Jirka on Sep 7, 2026. To check them, rebuild into a scratch folder
(`make -B phase1 PROCESSED=<scratch>/p OUT=<scratch>/r`) and compare, rather than re-running in
place: GOBNILP's log contains timings that differ on every run. A re-run counts as "the same"
when the objective and all `child:-{…}` lines are unchanged.

| File | What it is | Made by |
|---|---|---|
| `gobnilp-std-run.log` | GOBNILP console log: the exact BIC-optimal structure with STD tables (`child:-{parents}` lines), solve statistics, build details. Derived. | `make phase1` stage 4; commit `fd2b479`, Sep 6, 2026 |
| `adjmat.txt`, `adjmat.dot` | The GOBNILP DAG as a 44 × 44 adjacency matrix (row = parent, column = child) and as a Graphviz drawing. Derived; input of step 1.5.3. | `make phase1` stage 4 (GOBNILP writes them automatically) |
| `pdagadjmat.txt`, `pdagadjmat.dot` | The CPDAG of that DAG (arcs whose direction is not determined by the data are undirected). Derived; input of step 1.5.3. | same |
| `bnlearn-hc-dag.csv` | Adjacency matrix of the bnlearn hill-climbing structure (row = parent, column = child). Derived; input of step 1.5.2. | `make phase1` stage 6 (`R/bnlearn_hc.R`); commit `a53bdd9`, Sep 7, 2026 |
