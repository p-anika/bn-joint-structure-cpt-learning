# results/: outputs, one folder per experiment

Each folder has a README saying which command and commit made each file. Results are never
overwritten silently: a corrected result gets a new file, and the old one is marked
"superseded by …" in its folder's README.

| Folder | Experiment |
|---|---|
| [`phase1/`](phase1/README.md) | Phase 1 two-stage baseline: exact GOBNILP structure, CPT types, bnlearn hc structure |
| [`test-data24/`](test-data24/README.md) | GOBNILP smoke test on Jirka's 23-variable example |
| [`data-provenance/`](data-provenance/README.md) | Check that Jirka's R code reproduces `BN-data.csv` |
