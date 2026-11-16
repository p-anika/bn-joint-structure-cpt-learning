"""Shared file paths and constants, so no script hard-codes them.

Every path is built from `REPO_ROOT`, the folder that holds this repository. It is found from
the location of this file (`src/bnjoint/config.py` is two folders below the root), so the code
works wherever the repo is cloned. Scripts use these as the *defaults* of their command-line
arguments; you can always point a script at other files instead.

Example
-------
>>> from bnjoint import config
>>> config.BN_DATA_CSV.name
'BN-data.csv'
"""

from pathlib import Path

# parents[0] = src/bnjoint, parents[1] = src, parents[2] = the repository root
REPO_ROOT: Path = Path(__file__).resolve().parents[2]

# ---- data folders (see data/*/README.md) ----
DATA_RAW: Path = REPO_ROOT / "data" / "raw"  # Jirka's originals, read-only
DATA_PROCESSED: Path = REPO_ROOT / "data" / "processed"  # files our scripts derive
DATA_REFERENCE: Path = REPO_ROOT / "data" / "reference"  # typed-in tables from papers
RESULTS: Path = REPO_ROOT / "results"

# ---- the 44-variable data set ----
BN_DATA_CSV: Path = DATA_RAW / "BN-data.csv"
DAT_FILE: Path = DATA_PROCESSED / "bn-data-44.dat"  # scoring2a input
VARNAMES_FILE: Path = DATA_PROCESSED / "bn-data-44-varnames.txt"

# ---- Phase 1 results ----
PHASE1_DIR: Path = RESULTS / "phase1"
PHASE1_GOBNILP_LOG: Path = PHASE1_DIR / "gobnilp-std-run.log"
PHASE1_CPT_SUMMARY: Path = PHASE1_DIR / "cpt-type-summary.csv"

# ---- model constants ----
K_STATES: int = 3  # every variable has 3 states (-1, 0, 1); paper Sec. 4.1
DATA_VALUES: tuple[int, ...] = (-1, 0, 1)  # the values allowed in BN-data.csv

# ---- scoring2a settings used in Phase 1 (decision log entry 5) ----
# Kept here for documentation and for Python code that needs them; the Makefile passes the
# same values to scoring2a on its command line (ALPHA and PALIM there).
SCORING_ALPHA: int = 1  # 1 = the true BIC penalty (scoring-how-to-use-it.txt)
SCORING_PALIM: int = 9  # maximum number of parents per node
