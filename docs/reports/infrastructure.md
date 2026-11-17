# Infrastructure report: repository, tools and documentation

**Summary for Jirka.** No research result here: this records how the repository was organized
so that every result can be rebuilt with one command and traced to its code, data and decision.
The original data is kept read-only with checksums, all code lives in one tested Python package
driven by a Makefile, and external programs (SCIP, GOBNILP) are built outside the repository.
The research checks made along the way (data provenance, full rebuild) are in
[phase-1.5.md §1.5.0](phase-1.5.md#150-data-and-reproducibility).

Work done in Phase 1.5 (2026-11-15/16). The reasons for each choice are in
`docs/decision-log.md`, part "Repository and process"; this report says what was done and where
things went.

## Documentation audit (step 1.5.0a, 2026-11-15)

Every old Markdown file was checked section by section against the code, results, git history
and research plan. What was still correct was moved to one place; the rest was deleted.

| Old file | Outcome |
|---|---|
| `project-task-list.md` | Deleted. Python-first reasoning and Jirka's file list → decision log; the `scoring2a.c` code map → `docs/code-guide/scoring2a.md`. |
| `phase-0-detailed-steps.md` | Deleted. Correct parts → `docs/setup.md`, with the GOBNILP build rewritten from what actually worked (shell history, `CMakeCache.txt`). |
| `phase-1-detailed-steps.md` | Deleted. Eight Phase 1 decisions → decision log (entries 2, 3, 5–10). |
| `docs/bnsl_header.md` | Deleted. → `docs/setup.md` §8, with an annotated example and the reason for the header. |
| `docs/prompts/phase-1.5-prompts.md` | Deleted (Anika's personal file). |
| `docs/baseline_reproduction_notes.md` | Moved to `docs/reports/phase-1.md`. The audit found seven errors in it (repo name, Figure 4 interpretation, the tie bug behind 10/30/4, an unfinished sentence on parameter counts, "STD can never beat MLR", "STD winners have 0 or 1 parent", the discrepancy list); the rewritten report states the correct facts. |

The five deleted files last existed at commit **`6a38593`** (`git show 6a38593:<file>`).

## Repository layout (step 1.5.0b, 2026-11-15)

All moves used `git mv` (history kept) and were checked to be pure renames (same git blob).

| From | To |
|---|---|
| `data/BN-data.csv`, `data/preprocessed-data.csv`, `data/data24-training-1.dat`, `data/data24-training-1-bic.scores` | `data/raw/` |
| `data/bn-data-44.*`, `…-varnames.txt`, `…-bic-fixed.bnsl`, `data/data24-training-1-bic-fixed.bnsl` | `data/processed/` |
| `src/scoring2a.c` | `tools/scoring2a/` (with `scoring-how-to-use-it.txt` and `script-data24-1` from Jirka's Jul 8 zip, newly tracked) |
| `src/gobnilp.set` | `tools/gobnilp/` |
| `results/gobnilp-std-run.log`, `cpt-type-summary.csv`, `bnlearn-hc-dag.csv` | `results/phase1/` (now `results/phase-1/`) |
| `results/adjmat.*`, `results/pdagadjmat.*` (23-variable test) | `results/test-data24/` |
| `scripts/bnlearn_hc.R` | `R/` |

- **Removed from git** (last at commit `a183df9`): `data/data24-training-1-bic.jkl` (a duplicate),
  `scripts/run_gobnilp_pipeline.sh` (replaced by the Makefile), `src/scoring2a` (a binary),
  `src/gobnilp` (a broken gitlink). Untracked duplicates in `data/raw/` were byte-identical
  (SHA-256) to the tracked copies and were deleted. Jirka's compiled `scoring2a` differed from
  ours (`3dc618b6…` vs `2be2f069…`); its checksum is kept in `data/raw/README.md`.
- **GOBNILP** moved to `~/tools/gobnilp/`, with `~/.local/bin/gobnilp` re-pointed and `make` re-run
  there. Its `scip` link is absolute and still valid ([setup.md §7](../setup.md#7-scip-and-gobnilp-exact-structure-search)).
- **New code:** the package `src/bnjoint/`, thin argparse scripts, `scripts/check_inventory.py`,
  `R/convert_jirka_aug5.R`, tests, `Makefile`, `pyproject.toml`, `requirements*.txt`,
  `.gitattributes`, `.gitignore` (decisions 40–46).
- **Checks:** every derived file rebuilt byte-identical
  ([phase-1.5.md §1.5.0](phase-1.5.md#rebuild-from-the-raw-data)); `make scoring2a` rebuilds the
  binary with the same SHA-256 as the one committed before (`2be2f069…`), so the compile is
  deterministic on this machine; tests, lint and inventory pass.

## Documentation policy (2026-11-16)

Documents describe the current state; git keeps old versions; the decision and experiment logs
are the append-only history; each report has "What we tried that didn't work" and, for changed
reported numbers, a History line (decision 63). Applied repo-wide: `phase-1.md` was rewritten,
dated notes were removed everywhere, and the superseded `results/phase1/cpt-type-summary.csv`
was deleted (last at commit `9d80757`; the regression tests read it from git, decision 64).

## Documentation reorganization (2026-11-16)

Documents organized by phase and audience (decisions 65–68). All moves with `git mv`:

| From | To |
|---|---|
| `results/phase1/`, `results/phase1.5/` | `results/phase-1/`, `results/phase-1.5/` |
| `docs/reports/1.5.1-1.5.2.md` | `docs/reports/phase-1.5.md` (one section per step) |
| `docs/reports/1.5.0b.md` + `1.5.0a.md` | this file (research checks → `phase-1.5.md` §1.5.0); `1.5.0a.md` deleted, last at `fe269d3` |
| `docs/explainers/00-repo-tools.md`, `03-cpt-types.md`, `04-one-parent-mlr-equals-std.md` | `repo-tools.md`, `cpt-types.md`, `one-parent-mlr-equals-std.md` |
| `docs/paper-claims.md` | `docs/paper-material/paper-claims.md` |
| `docs/code-guide/phase1-pipeline.md` | `docs/code-guide/phase-1-pipeline.md` |
| `tests/test_phase1_regression.py` | `tests/test_regression.py` |
| Make targets `phase1`, `phase1.5` | `phase-1`, `phase-1.5` |

Git does not detect `phase-1.5.md` and `infrastructure.md` as renames (their content was
rewritten), so `git log --follow` stops at this reorganization; the earlier history is under the
old paths: `git log -- docs/reports/1.5.1-1.5.2.md docs/reports/1.5.0b.md docs/reports/1.5.0a.md`.

New: `docs/glossary.md`, `docs/theory/one-parent-mlr-equals-std.md`, four reading notes in
`docs/reading-notes/`. The decision log was regrouped into "Method" and "Repository and process"
with a heading per entry (no entry changed or removed). `make -B phase-1.5` after the renames:
both CSVs byte-identical, only the paths printed in the logs changed.

## What we tried that didn't work

- **GOBNILP inside the repository** (`src/gobnilp/`): git stored it as a broken "submodule"
  pointer, because it is someone else's git repository. Moved to `~/tools/gobnilp/` (decisions 16, 39).
- **A Bash pipeline script** (`run_gobnilp_pipeline.sh`): it always re-ran everything and needed
  `cd src`. Replaced by the Makefile (decision 35).
- **Committing compiled binaries** (`src/scoring2a`, Jirka's `scoring2a`): they can't be read or
  diffed and depend on the machine. Removed; we build from source (decisions 29, 36).
- **Dated correction notes inside documents** (the first documentation rule): after two steps the
  Phase 1 report had 14 of them and was hard to read. Replaced by the current-state policy
  (decision 63).
- **Reports per prompt** (`1.5.0a.md`, `1.5.0b.md`, `1.5.1-1.5.2.md`): finding a result required
  knowing which prompt produced it. Replaced by one report per phase (decision 65).
- **Numbered explainer filenames:** adding two explainers forced a renumbering. Order now lives
  only in the explainers README (decision 66).

## Surprises

- **Jirka's files have Windows (CRLF) line endings** (`BN-data.csv`, `preprocessed-data.csv`,
  `data24-training-1.dat`, `scoring2a.c`, `gobnilp.set`). Harmless for every program we use, but
  it is why `.gitattributes` exempts the originals from line-ending conversion.
- **The 44-variable DAG/CPDAG files existed before:** committed as `src/adjmat.*` in `fd2b479`
  and removed in `c97da60`; the regenerated files are byte-identical to them.
- The `gobnilp.set` warning goes to stderr, so `tee` doesn't save it; SCIP's static libraries are
  built by GOBNILP's own `make` (`make -C scip libs`); both are in `setup.md` §7.

## Open questions

- Our copy of [de Campos et al. 2018](../references.md#decampos2018) is the **arXiv preprint v1**.
  Before quoting its theorem, lemma or algorithm numbers in the paper, check them against the
  journal version.
