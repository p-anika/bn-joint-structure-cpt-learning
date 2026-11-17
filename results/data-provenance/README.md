# results/data-provenance/: where BN-data.csv comes from

This folder holds only this README: the record of a check. No data file is kept here.

**Command:** `make provenance`. It runs `R/convert_jirka_aug5.R` (Jirka's Aug 5, 2026 R code,
verbatim) on `data/raw/preprocessed-data.csv` and writes the result to the git-ignored scratch
file `scratch/provenance/BN-data-from-jirka-code.csv`. A regenerated copy of a data file is never
committed (CLAUDE.md), so only the comparison is recorded here.

**Result (2026-11-15, step 1.5.0b):** 1661 × 44, column names identical, 0 of 73,084 values
differ, and the rebuilt file has the same SHA-256 as `data/raw/BN-data.csv`:

| File | SHA-256 |
|---|---|
| `scratch/provenance/BN-data-from-jirka-code.csv` (rebuilt) | `e8a1aeb11d0709e81cdbd8d6ed6315b8bb8d644fa4a305254aab3aa62c0891d7` |
| `data/raw/BN-data.csv` (Jirka's original) | `e8a1aeb11d0709e81cdbd8d6ed6315b8bb8d644fa4a305254aab3aa62c0891d7` |

Details: `docs/reports/infrastructure.md`.
