# Code guide: the Phase 1 pipeline (`make phase-1`)

**What it does.** Reproduces the Phase 1 two-stage baseline from `data/raw/BN-data.csv`:
(1) the exact BIC-optimal structure with STD tables (scoring2a + GOBNILP), (2) the best CPT
type per node on that structure, (3) the bnlearn hill-climbing structure for comparison.
`make phase-1` runs stages 1–4 and 6; stage 5 is `make phase-1.5`, which writes to
`results/phase-1.5/`.
Results and their interpretation: [`docs/reports/phase-1.md`](../reports/phase-1.md).

## Data flow, stage by stage

The Make rules are in the `Makefile` under "Phase 1"; their numbers match these.

1. **Convert** — `scripts/convert_data.py` → `bnjoint.io.convert_bn_data`.
   Checks every value is −1/0/1, shifts them to 0/1/2 and writes `data/processed/bn-data-44.dat`
   (format in the `io` module docstring) and `bn-data-44-varnames.txt`.
2. **Score** — `tools/scoring2a/scoring2a bn-data-44.dat 1 9 prune 0 bic`. For each variable,
   computes the BIC of every parent set up to 9 parents that survives pruning, and writes them
   to `bn-data-44-bic.scores`. About 15 minutes; by far the slowest stage. How it works:
   [scoring2a.md](scoring2a.md). Argument meanings: `docs/setup.md` §6.
3. **Header** — `scripts/add_bnsl_header.sh` puts the variable names and `SCORES START` in
   front, giving `bn-data-44-bic-fixed.bnsl` (why: `docs/setup.md` §8).
4. **Search** — `gobnilp -f …bnsl -s tools/gobnilp/gobnilp.set`, run inside `results/phase-1/`.
   GOBNILP turns "pick one parent set per variable, total score as high as possible, no
   cycles" into an integer linear program and solves it exactly with SCIP. The console output
   is saved as `gobnilp-std-run.log` (via `tee`, which shows output on screen and writes it to
   a file at once). GOBNILP also writes `adjmat.txt`/`.dot` (the DAG) and `pdagadjmat.txt`/`.dot`
   (its CPDAG) into the folder it runs in; in the matrices, row = parent and column = child.
5. **CPT types** — now `make phase-1.5`: `scripts/fit_cpt_types.py` reads the parent sets from
   the log (`bnjoint.gobnilp_io.parse_parent_sets`), fits STD, MLR and OLR per node with the
   tie rule (`bnjoint.cpt_scores.fit_cpt_types`; guide: [cpt-scoring.md](cpt-scoring.md)) and
   writes `results/phase-1.5/1.5.1-gobnilp-tie-fix/cpt-type-summary.csv`.
6. **hc** — `Rscript R/bnlearn_hc.R`: bnlearn `hc(score = "bic")` with `set.seed(1)`; writes the
   adjacency matrix `bnlearn-hc-dag.csv`.

The final line `make phase-1` prints is GOBNILP's `objective value`; for Phase 1 it is
−64837.738627.

## Why it is designed this way

- **scoring2a + GOBNILP** rather than bnlearn alone: GOBNILP gives the *proven* optimum for
  the scores it is given; hill-climbing can stop at a local optimum. This exactness is what
  the project's joint learning builds on.
- **Parent sets read from the log**, not `bi.mat`: this GOBNILP never writes `bi.mat`
  (decision log entry 6). The parser checks that every variable appears exactly once.
- **Settings `1 9 prune 0 bic`**: decision log entry 5.
- **Run GOBNILP inside the output folder** so its automatic `adjmat.*` files land next to the
  log instead of cluttering the repo root.

## How to run

```bash
source .venv/bin/activate
make phase-1                       # does only what is out of date
make phase-1.5                     # CPT types (stage 5) on both structures + Table 2 check
make -B phase-1                    # force everything (~20 min)
make phase-1 PROCESSED=/tmp/p OUT=/tmp/r   # rebuild elsewhere, leaving committed files alone
make test-data24                  # 5-second GOBNILP check on Jirka's small example
```

A forced run rewrites `results/phase-1/gobnilp-std-run.log`. Its timing numbers always differ
from run to run; check that the objective and the `child:-{…}` lines are unchanged
(`git diff`), and don't commit a log whose only change is timings.

## How to change common things safely

- **Different palim or alpha**: change `PALIM`/`ALPHA` in the `Makefile` *and* write to a new
  results folder (`OUT=results/<new-experiment>` and a new `PROCESSED`), so the Phase 1 files
  are not overwritten. Keep `config.py` in step.
- **A different data file**: pass `--csv`/`--dat` to `convert_data.py`; all variables must have
  3 states, or `K_STATES` and the `.dat` writer need generalizing.
- **A different GOBNILP build**: set `GOBNILP=/path/to/gobnilp` on the make command line.
