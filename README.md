# BN Joint Structure + CPT-Type Learning

Learning a Bayesian network's structure and each node's CPT type (STD, MLR or OLR) together,
with safe pruning rules. Research project with Dr. Jiří Vomlel (UTIA, Prague).

The baseline ([Vomlel, Kybernetika 2026](docs/references.md#vomlel2026)) learns the structure with standard tables (STD) and
only then picks a CPT type per node. This project scores every candidate parent set with
max(BIC_STD, BIC_MLR, BIC_OLR) and lets GOBNILP find the optimal structure for that joint
score. The research contribution is new pruning rules that skip parent sets which cannot be
optimal. The step-by-step plan is [`docs/research-plan.md`](docs/research-plan.md).

## Setup

Full instructions (WSL2, Python, R, SCIP, GOBNILP, scoring2a): [`docs/setup.md`](docs/setup.md).
Short version, once SCIP and GOBNILP are built:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
make test            # all tests pass
make test-data24     # GOBNILP works: objective value -3411.597651
```

## How to run each phase

| Phase | Command | Output | Report |
|---|---|---|---|
| 1: two-stage baseline structures (exact GOBNILP structure, hc comparison) | `make phase1` (~20 min from scratch; prints `objective value -64837.738627`). Rewrites the reported `results/phase1/` files, so for a check run it into scratch: `make -B phase1 PROCESSED=scratch/p OUT=scratch/r` | `results/phase1/` (as reported to Jirka) | [`docs/reports/phase-1.md`](docs/reports/phase-1.md) |
| 1.5.1–1.5.2: CPT types with the tie rule on the GOBNILP and hc structures; hc vs. the paper's Table 2 | `make phase1.5` (~10 s; prints 16/24/4 for GOBNILP and 19/22/3 with 44/44 nodes matching Table 2) | `results/phase1.5/` | [`docs/reports/1.5.1-1.5.2.md`](docs/reports/1.5.1-1.5.2.md) |
| later steps | added as each step is done | | `docs/reports/` |

`make help` lists all targets. Other checks: `make provenance` (Jirka's R code reproduces
`BN-data.csv`), `make lint`, `make inventory` (every tracked file is documented).

## Repository map

| Path | What it is |
|---|---|
| [`data/`](data/README.md) | `raw/` Jirka's originals (read-only), `processed/` derived files, `reference/` tables from papers |
| [`src/bnjoint/`](src/bnjoint/README.md) | The Python package: all reusable code |
| [`scripts/`](scripts/README.md) | Thin command-line entry points |
| [`R/`](R/README.md) | R scripts (bnlearn) |
| [`tools/`](tools/README.md) | scoring2a source and GOBNILP settings (builds live outside the repo) |
| [`tests/`](tests/README.md) | pytest tests |
| [`results/`](results/README.md) | One folder per experiment |
| [`docs/`](docs/README.md) | Plan, setup, logs, code guides, explainers, reports, paper material |

Files in this folder:

| File | What it is |
|---|---|
| `README.md` | This file |
| `CLAUDE.md` | Working rules for Claude Code in this repo (written by Anika) |
| `Makefile` | One target per pipeline stage (`make help`) |
| `pyproject.toml` | Declares the `bnjoint` package; ruff and pytest settings |
| `requirements.txt` | Pinned Python packages for the research code (+ the package itself) |
| `requirements-dev.txt` | `requirements.txt` + pytest and ruff |
| `.gitignore` | Files git never tracks (virtual environment, builds, scratch) |
| `.gitattributes` | Line-ending rules: LF for our files, Jirka's originals untouched |

Not in git: `.venv/` (Python environment), `scratch/` (throwaway outputs such as
`make provenance`'s rebuilt data copy), `docs/tasks/` (plans for steps awaiting approval),
`papers/` (local PDF copies of papers; never commit them, citations are in
[`docs/references.md`](docs/references.md)).

Start here if you are new: [`docs/code-guide/ARCHITECTURE.md`](docs/code-guide/ARCHITECTURE.md),
then [`docs/explainers/README.md`](docs/explainers/README.md).
