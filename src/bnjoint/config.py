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
# The CPT-type CSV reported to Jirka on Sep 7, 2026 (old winner rule, 10/30/4). It is no
# longer in the working tree; git keeps it at this commit, and the regression tests read it
# with `git show <PHASE1_CPT_SUMMARY_GIT>` to check that the BIC values never change.
PHASE1_CPT_SUMMARY_GIT: str = "9d80757:results/phase1/cpt-type-summary.csv"
PHASE1_HC_DAG_CSV: Path = PHASE1_DIR / "bnlearn-hc-dag.csv"  # bnlearn hill-climbing structure

# ---- Phase 1.5 results: results/phase1.5/<step>-<experiment>/ ----
PHASE15_DIR: Path = RESULTS / "phase1.5"
STEP151_DIR: Path = PHASE15_DIR / "1.5.1-gobnilp-tie-fix"
STEP151_CPT_SUMMARY: Path = STEP151_DIR / "cpt-type-summary.csv"
STEP152_DIR: Path = PHASE15_DIR / "1.5.2-hc-vs-table2"
STEP152_CPT_SUMMARY: Path = STEP152_DIR / "cpt-type-summary-hc.csv"
STEP152_COMPARISON: Path = STEP152_DIR / "table2-comparison.csv"

# ---- published reference tables (data/reference/README.md) ----
KYBERNETIKA_TABLE2: Path = DATA_REFERENCE / "kybernetika-table2.csv"  # Vomlel 2026, Table 2

# ---- model constants ----
K_STATES: int = 3  # every variable has 3 states (-1, 0, 1); paper Sec. 4.1
DATA_VALUES: tuple[int, ...] = (-1, 0, 1)  # the values allowed in BN-data.csv

# ---- CPT-type winner rule (CLAUDE.md conventions; decision log, step 1.5.1) ----
# Two BIC scores closer than TIE_TOLERANCE count as equal. 1e-6 is far above floating-point
# noise in a sum of ~1661 terms (about 1e-12) and far below any real difference (> 0.01 here).
TIE_TOLERANCE: float = 1e-6
# Among tied types, the first in this list wins: the simplest model first. STD before OLR
# before MLR, because a tie means the data cannot tell them apart (explainer 03).
TIE_ORDER: tuple[str, ...] = ("STD", "OLR", "MLR")

# ---- scoring2a settings used in Phase 1 (decision log entry 5) ----
# Kept here for documentation and for Python code that needs them; the Makefile passes the
# same values to scoring2a on its command line (ALPHA and PALIM there).
SCORING_ALPHA: int = 1  # 1 = the true BIC penalty (scoring-how-to-use-it.txt)
SCORING_PALIM: int = 9  # maximum number of parents per node
