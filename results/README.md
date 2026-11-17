# results/: outputs, one folder per experiment

Each folder has a README saying which command and commit made each file. A corrected result
gets a new file; the superseded one is deleted (git keeps it), and the report's History
section names the commit that holds it.

| Folder | Experiment |
|---|---|
| [`phase-1/`](phase-1/README.md) | Phase 1 structures: exact GOBNILP structure and bnlearn hc structure |
| [`phase-1.5/`](phase-1.5/README.md) | Phase 1.5: corrected CPT types (tie rule) on the GOBNILP structure; CPT types on the hc structure vs. the paper's Table 2 |
| [`test-data24/`](test-data24/README.md) | GOBNILP smoke test on Jirka's 23-variable example |
| [`data-provenance/`](data-provenance/README.md) | Check that Jirka's R code reproduces `BN-data.csv` |
