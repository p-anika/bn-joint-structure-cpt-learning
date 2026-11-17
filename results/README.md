# results/: outputs, one folder per experiment

Each folder has a README saying which command and commit made each file. Results are never
overwritten silently: a corrected result gets a new file, and the old one is marked
"superseded by …" in its folder's README.

| Folder | Experiment |
|---|---|
| [`phase1/`](phase1/README.md) | Phase 1 two-stage baseline as reported to Jirka (Sep 7): exact GOBNILP structure, CPT types (superseded), bnlearn hc structure |
| [`phase1.5/`](phase1.5/README.md) | Phase 1.5: corrected CPT types (tie rule) on the GOBNILP structure; CPT types on the hc structure vs. the paper's Table 2 |
| [`test-data24/`](test-data24/README.md) | GOBNILP smoke test on Jirka's 23-variable example |
| [`data-provenance/`](data-provenance/README.md) | Check that Jirka's R code reproduces `BN-data.csv` |
