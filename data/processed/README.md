# data/processed/: files our scripts derive from data/raw/

Everything here can be rebuilt with one command, and is checked into git only so that the
exact inputs behind reported numbers are visible (and because scoring takes ~15 minutes).
If you rebuild a file, `git diff` shows whether it changed. In step 1.5.0b all of them were
rebuilt from scratch and were byte-identical (`docs/reports/1.5.0b.md`).

| File | What it is | Made by |
|---|---|---|
| `bn-data-44.dat` | `data/raw/BN-data.csv` in scoring2a's format: header (44 variables, all with 3 states, 1661 rows), then the data with −1/0/1 shifted to states 0/1/2 | `make phase1` → `scripts/convert_data.py` |
| `bn-data-44-varnames.txt` | The 44 column names on one line (no final newline), for the `.bnsl` header | `make phase1` → `scripts/convert_data.py` |
| `bn-data-44-bic.scores` | Local BIC score of every candidate parent set kept by scoring2a's pruning (alpha 1, at most 9 parents) | `make phase1` → `tools/scoring2a/scoring2a … 1 9 prune 0 bic` |
| `bn-data-44-bic-fixed.bnsl` | The scores file with the two header lines GOBNILP needs; the file GOBNILP read for Phase 1 | `make phase1` → `scripts/add_bnsl_header.sh` |
| `data24-training-1-bic-fixed.bnsl` | Jirka's 23-variable scores (`data/raw/data24-training-1-bic.scores`) with the header; variable names are `0 … 22` | `make test-data24` → `scripts/add_bnsl_header.sh` |

The format of `.scores` / `.bnsl` files is described in `docs/setup.md` §8 and
`docs/code-guide/scoring2a.md`.
