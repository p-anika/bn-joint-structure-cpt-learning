# scripts/: command-line entry points

Each script does one job, takes command-line arguments (`--help` lists them), and keeps its
logic in `src/bnjoint/`. Defaults come from `src/bnjoint/config.py`. Normally you run them
through `make` (see the root README) rather than by hand.

| File | Job | Called by |
|---|---|---|
| `convert_data.py` | `data/raw/BN-data.csv` → `data/processed/bn-data-44.dat` + `bn-data-44-varnames.txt` | `make phase1` |
| `add_bnsl_header.sh` | Add the variable-names line and `SCORES START` that GOBNILP needs to a `.scores` file | `make phase1`, `make test-data24` |
| `fit_cpt_types.py` | Score STD/MLR/OLR for every node of a learned structure (`--structure gobnilp` or `hc`), with the tie rule and convergence report; write a `cpt-type-summary*.csv` | `make phase1.5` |
| `compare_with_table2.py` | Compare our per-node parents and CPT types with the paper's Table 2; write `table2-comparison.csv` | `make phase1.5` |
| `check_inventory.py` | List tracked files that no README mentions | `make inventory` |

All are originals written by us. `run_gobnilp_pipeline.sh` was replaced by the Makefile in
step 1.5.0b (decision log).
