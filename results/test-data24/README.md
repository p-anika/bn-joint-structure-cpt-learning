# results/test-data24/: GOBNILP smoke test (23-variable example)

A quick check (a few seconds) that GOBNILP works, on Jirka's example
`data/raw/data24-training-1-bic.scores`. The variables are just numbered `0 … 22`. Not a
research result. Command: `make test-data24`.

| File | What it is | Made |
|---|---|---|
| `adjmat.txt`, `adjmat.dot` | The optimal DAG as a 23 × 23 adjacency matrix (row = parent, column = child) and as a Graphviz drawing | GOBNILP; first committed Aug 18, 2026 (`de88a7e`), moved to `results/` Sep 6 (`fa3b2ef`), moved here in step 1.5.0b |
| `pdagadjmat.txt`, `pdagadjmat.dot` | Its CPDAG (the equivalence class: arcs whose direction the data can't decide become undirected) | same |
| `gobnilp-data24.log` | GOBNILP's console output: objective −3411.597651 | `make test-data24`, step 1.5.0b |

Re-running `make test-data24` with GOBNILP in `~/tools/gobnilp/` gives the same objective and
byte-identical adjmat/pdagadjmat files.
