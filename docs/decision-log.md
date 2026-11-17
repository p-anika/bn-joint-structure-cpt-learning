# Decision log

Every choice made in this project: what was decided, why, what else was considered, and who
decided. This log is the project's **history** and is append-only: entries are never edited away
or deleted, and numbers are never reused. A replaced entry gets a **Status** line saying which
entry supersedes it. Entries record the paths, file names and numbers of their time.

Two parts, each in number order:

- [**Method**](#method): data, scoring, CPT fitting, structure learning, and Jirka's
  confirmations. These are the choices the paper's Methods section rests on.
- [**Repository and process**](#repository-and-process): files, tools, tests, git and
  documentation.

Conventions:

- **Decided by** is *Anika*, *Jirka*, or *proposed by Claude, approved by Anika*.
- **Backfilled** entries were written after the fact, from the old plan files deleted in step
  1.5.0a (readable in git at commit `6a38593`).
- **Deleted files**: to read one, `git show <commit>:<path>`. Last commits: entries 23–27 →
  `6a38593`; entries 34–38 and the files removed in step 1.5.0b → `a183df9`; entry 63 (old Phase 1
  report, old CPT-type CSV) → `9d80757`; entry 65 (`docs/reports/1.5.0a.md`) → `fe269d3`.

## Method

### 2. Use BN-data.csv exactly as sent

- **Date:** Aug 5, 2026 (backfilled)
- **Decision:** Use `BN-data.csv` as sent; don't re-derive it from `preprocessed-data.csv`.
- **Why:** Jirka asked for it, so both of us work from identical data.
- **Alternatives considered:** Re-run his R conversion ourselves (kept only as an optional check, entry 13).
- **Decided by:** Jirka

### 3. Our own GOBNILP build on SCIP 10.0.3

- **Date:** Aug 2026 (backfilled)
- **Decision:** Use our own GOBNILP build (commit `5441edf`) on SCIP 10.0.3 + SoPlex 8.0.3.
- **Why:** It works once the `.bnsl` header is added, and it is the current version.
- **Alternatives considered:** Jirka's GOBNILP 1.6.3 / SCIP 3.2.1 (2016-era; hard to rebuild).
- **Decided by:** Anika

### 5. scoring2a settings: alpha 1, palim 9, prune, bic

- **Date:** Sep 6, 2026 (backfilled)
- **Decision:** scoring2a settings: alpha = 1, palim = 9, `prune`, score `bic`.
- **Why:** alpha = 1 gives the true BIC (de Campos's note `scoring-how-to-use-it.txt`). `1 9 prune 0 bic` is exactly Jirka's example `script-data24-1`. The resulting network has at most 2 parents per node, like Table 2. The paper's structure came from hc, so no scoring2a setting "from the paper" exists (entry 19). **Later approved by Jirka (Sep 28, 2026; entry 52).**
- **Alternatives considered:** Smaller palim (faster, but might cut off the optimum).
- **Decided by:** Anika; approved by Jirka Sep 28

### 6. Read parent sets from the GOBNILP console log

- **Date:** Sep 6, 2026 (backfilled)
- **Decision:** Read learned parent sets from the GOBNILP console log (`child:-{...}` lines), not from `bi.mat`.
- **Why:** This GOBNILP ignores the `adjacencymatrix` setting in `gobnilp.set`, so `bi.mat` is never written. The log lists every family unambiguously.
- **Alternatives considered:** Fix `gobnilp.set` for the new parameter names (possible later).
- **Decided by:** Anika

### 7. STD parameter count includes unobserved configurations

- **Date:** Sep 6, 2026 (backfilled)
- **Decision:** STD parameter count uses all k^n parent configurations, even unobserved ones: (k−1)·k^n.
- **Why:** Paper eq. 6; scoring2a counts the same way, so our BIC matches GOBNILP's scores.
- **Alternatives considered:** Count only observed configurations (gives different BIC numbers).
- **Decided by:** Anika (following the paper)

### 8. MLR dummy coding; OLR with raw parent values

- **Date:** Sep 6, 2026 (backfilled)
- **Decision:** MLR: dummy-code each parent, state −1 as reference. OLR: use raw parent values −1/0/1, one coefficient per parent.
- **Why:** Paper eq. 11 (MLR dummies) and eq. 16 (OLR uses parent values directly). **Still to confirm with Jirka**; it is the planned Email #3 question.
- **Alternatives considered:** Dummy-code OLR parents too (more parameters; not the paper's eq. 17 count).
- **Decided by:** Anika (following the paper)

### 9. No OLR for nodes without parents

- **Date:** Sep 6, 2026 (backfilled)
- **Decision:** No OLR for a node with 0 parents (score −∞, never chosen).
- **Why:** OLR with no parents is the same as STD/MLR; the paper only uses OLR with parents.
- **Alternatives considered:** Fit an intercept-only OLR (equals STD; adds nothing).
- **Decided by:** Anika (following the paper)

### 10. bnlearn hc with default settings and a fixed seed

- **Date:** Sep 7, 2026 (backfilled)
- **Decision:** Run bnlearn `hc(d, score = "bic")` with all other settings default, after `set.seed(1)`.
- **Why:** Matches how Jirka learned the paper's structure (entry 19). The seed makes the run repeatable.
- **Alternatives considered:** Other scores or restarts (not what the paper did).
- **Decided by:** Anika

### 11. Prototype joint scoring in Python

- **Date:** Sep 2026 (backfilled)
- **Decision:** Prototype joint scoring in Python first; C only if Python is too slow.
- **Why:** Much faster to write and debug. Already in the research plan ("C only if Python is too slow in Phase 4").
- **Alternatives considered:** Modify `scoring2a.c` directly.
- **Decided by:** Anika

### 12. Data provenance: Jirka's originals in data/raw/

- **Date:** 2026-11-15
- **Decision:** **Data provenance.** Jirka's original files go in `data/raw/` (read-only): `preprocessed-data.csv` (Jul 8: his preprocessed survey on the original 1–7 scale, all columns); `BN-data.csv` (Aug 5: the exact 44-variable data of the Kybernetika paper, made from `preprocessed-data.csv` by his R code: keep columns 29–72 = a1–a30, d1–d14; map 1–3 → −1, 4 → 0, 5–7 → +1); `data24-training-1.dat` and `data24-training-1-bic.scores` (Jul 8, "unix files.zip": his 23-variable GOBNILP test example). Everything else in `data/` (`bn-data-44.*`, `*-fixed.bnsl`, `*.jkl`, the varnames file) was made by us and goes to `data/processed/` or is regenerated.
- **Why:** Keep originals separate from anything we derive, so nothing we do can change them.
- **Alternatives considered:** Mixing raw and derived files (current state).
- **Decided by:** Anika

### 13. Check that Jirka's R conversion reproduces BN-data.csv

- **Date:** 2026-11-15
- **Decision:** Optional check in 1.5.0b: apply Jirka's R conversion to `preprocessed-data.csv` and check it reproduces `BN-data.csv` exactly. Results go to `results/`, never `data/raw/`.
- **Why:** Confirms we understand where the data came from.
- **Alternatives considered:** Skip the check.
- **Decided by:** Anika

### 15. Table 2 as a read-only reference table

- **Date:** 2026-11-15
- **Decision:** Table 2 of the Kybernetika paper (p. 411) lives in `data/reference/kybernetika-table2.csv` (columns: variable, n_parents, parents separated by ";", cpt_type) and is read-only. Anika typed it in. Folder added to the layout in 1.5.0b.
- **Why:** Step 1.5.2 compares our fitting to it node by node.
- **Alternatives considered:** Put it in `data/raw/` (it isn't a file Jirka sent).
- **Decided by:** Anika

### 19. The paper's structure came from bnlearn hc

- **Date:** Sep 28, 2026
- **Decision / fact:** The paper's structure was learned with bnlearn hc: "The model structure in the Kybernetika paper was learnt using the hc procedure from the R package bnlearn." So `scripts/bnlearn_hc.R` is the paper-matching structure, and GOBNILP gives the exact optimum. His Jul 3 email had described the paper's procedure as "first learn a BIC-optimal DAG assuming STD CPTs throughout"; we follow the later, more specific Sep 28 statement.
- **Source:** Jirka's email, Sep 28, 2026
- **Decided by:** Jirka

### 20. Figure 4 numbers are cross-validated

- **Date:** Sep 28, 2026
- **Decision / fact:** Figure 4's numbers are cross-validated: "I can confirm that the BIC, number of parameters and log-likelihood in Figure 4 come from the 10-fold cross-validation." So they can't be compared directly with our full-data BIC.
- **Source:** Jirka's email, Sep 28, 2026
- **Decided by:** Jirka

### 21. Jirka: exact GOBNILP experiments are novel

- **Date:** Sep 28, 2026
- **Decision / fact:** Jirka called our exact GOBNILP experiments "novel and valuable". Recorded because the research plan relies on it when deciding when to ask about a paper.
- **Source:** Jirka's email, Sep 28, 2026
- **Decided by:** Jirka

### 45. Jirka's R conversion code kept verbatim

- **Date:** 2026-11-15
- **Decision:** `R/convert_jirka_aug5.R` holds Jirka's Aug 5 conversion code **verbatim** (given by Anika from the email), replacing a reconstruction from its description. Its output goes to the git-ignored `scratch/provenance/` (a regenerated data copy is never committed, CLAUDE.md); `results/data-provenance/README.md` records the matching SHA-256. Still, all analysis uses `BN-data.csv` directly (entry 2).
- **Why:** Provenance with his exact code, not our paraphrase.
- **Alternatives considered:** Keep the reconstruction.
- **Decided by:** Anika

### 52. Jirka approves the scoring2a settings

- **Date:** Sep 28, 2026 (recorded 2026-11-15)
- **Decision / fact:** **scoring2a settings approved.** "You used alpha = 1, palim = 9, prune and BIC, which is OK; the only parameter that could be different is palim, the maximal number of parents." With STD there will in practice never be more than nine parents, and a large palim is slow, "therefore, it is OK to keep it as it is." **Warning, relevant to Phase 2:** structure learning based on OLR or MLR "will have to consider more parents than with the STD option", so palim = 9 is not automatically safe for joint scoring. Updates entry 5.
- **Source:** Jirka's email, Sep 28, 2026
- **Decided by:** Jirka

### 53. a1–a30 and d1–d14 form one variable set

- **Date:** Jul 29, 2026 (recorded 2026-11-15)
- **Decision / fact:** **a1–a30 and d1–d14 form one combined variable set** for structure search: "We did the same in our experiments. In this way we give the BN learning algorithm freedom to group the studied variables." No restrictions between the groups are imposed (none are in our code).
- **Source:** Jirka's email, Jul 29, 2026
- **Decided by:** Jirka

### 55. CPT-type tie rule

- **Date:** 2026-11-16
- **Decision:** **CPT-type tie rule:** BICs within 1e-6 (absolute) of the best are tied; ties go to STD, then OLR, then MLR (`config.TIE_TOLERANCE`, `config.TIE_ORDER`, `cpt_scores.pick_winner`). Replaces the Phase 1 rule (plain `max`, exact ties to STD, MLR, OLR).
- **Why:** With 0–1 parents MLR and STD are the same model (explainer 04); their BICs differ by ~1e-13 of rounding, which decided six nodes in Phase 1. Real differences in our data are ≥ 0.17, so 1e-6 separates noise from signal safely. Simplest type first.
- **Alternatives considered:** Rounding scores before comparing (can still split near-equal numbers); a relative tolerance (unnecessary at these magnitudes).
- **Decided by:** Anika (CLAUDE.md, research plan 1.5.1)

### 56. Convergence check of MLR and OLR fits

- **Date:** 2026-11-16
- **Decision:** **Convergence check:** every MLR and OLR fit records statsmodels' `mle_retvals["converged"]`; the output CSV gets columns `mlr_converged`, `olr_converged` (empty = not fitted) and `parents`; `fit_cpt_types.py` prints counts and every non-converged fit; a test fails if any fit on either structure stops converging. A fit that raises an error counts as not converged (BIC −∞).
- **Why:** A fit stopped early has a too-low log-likelihood, so its BIC and the winner would be unreliable. Keeping the flag next to the number makes it impossible to miss. `parents` lets the CSV be compared with Table 2 and later with other structures.
- **Alternatives considered:** Print a warning only; raise the iteration limit blindly.
- **Decided by:** Anika (research plan 1.5.1); columns proposed by Claude, approved by Anika

### 58. Regression tests rewritten for the tie rule

- **Date:** 2026-11-16
- **Status:** Superseded in part by entry 64 (the reported CSV is now read from git).
- **Decision:** **Regression tests rewritten** for the intended rule change. Was: the new code's CSV byte-identical to `results/phase1/cpt-type-summary.csv`, plus a test asserting the no-tolerance bug. Now: (a) the three BIC columns equal the Phase 1 CSV exactly; (b) exactly the six nodes a13, a15, d6, d11, d12, d13 change, all MLR → STD; (c) split 16/24/4; (d) all fits converged; (e) the 1.5.1 and 1.5.2 CSVs are reproduced byte for byte; (f) the hc result matches Table 2 on all 44 nodes. The bug test was replaced by tie-rule tests, as its docstring planned.
- **Why:** The old byte-for-byte test *had* to fail once the winner rule changed on purpose. The new tests are stricter about what may change: the scores stay pinned to the reported numbers, and the winner changes are pinned to exactly the expected six. Not a weakening.
- **Alternatives considered:** Delete the regression test (forbidden); compare the new CSV only with itself (would no longer pin the reported scores).
- **Decided by:** Proposed by Claude, approved by Anika

## Repository and process

### 1. Work in WSL2 Ubuntu

- **Date:** Aug 2026 (backfilled)
- **Decision:** Work in WSL2 Ubuntu on Windows.
- **Why:** scoring2a and GOBNILP/SCIP are documented and tested on Linux.
- **Alternatives considered:** Native Windows build (poorly documented, fiddly).
- **Decided by:** Anika

### 4. Add the .bnsl header to score files

- **Date:** Aug 18, 2026 (backfilled)
- **Decision:** Add a variable-names line and `SCORES START` to every scores file (`scripts/add_bnsl_header.sh`).
- **Why:** This GOBNILP's reader requires them. Jirka's Aug 12 pointer to `chest_100_1_3.bnsl` confirmed the format.
- **Alternatives considered:** Edit files by hand (error-prone).
- **Decided by:** Anika, confirmed by Jirka

### 14. Jirka's program files go in tools/

- **Date:** 2026-11-15
- **Decision:** Jirka's program files go in `tools/`, not `data/raw/`: `scoring2a.c`, `scoring-how-to-use-it.txt`, `script-data24-1` in `tools/scoring2a/`; `gobnilp.set` in `tools/gobnilp/` (Jul 8 zip). Moved in 1.5.0b.
- **Why:** They are tools, not data. CLAUDE.md layout.
- **Alternatives considered:** Keep them in `src/` (meant for our Python package).
- **Decided by:** Anika

### 16. GOBNILP source out of the repository

- **Date:** 2026-11-15
- **Decision:** Take the GOBNILP source out of the repo (`git rm --cached src/gobnilp`). Move the build to `~/tools/gobnilp/`, redirect `~/.local/bin/gobnilp`, check its internal `scip` link. Prove it works on the data24 test file and with `make phase1` (−64837.74). Document it in `docs/setup.md`. Done in 1.5.0b.
- **Why:** It is someone else's repo nested inside ours (a broken submodule pointer). CLAUDE.md keeps external builds outside the repo.
- **Alternatives considered:** Make it a proper git submodule (more complex, not needed).
- **Decided by:** Anika

### 17. pytest and ruff in requirements-dev.txt

- **Date:** 2026-11-15
- **Decision:** Install pytest and ruff into `.venv`, pinned in a separate `requirements-dev.txt`. Done in 1.5.0b.
- **Why:** Needed for tests and formatting (CLAUDE.md). A separate file keeps the tools apart from the packages the research code needs.
- **Alternatives considered:** Put them in `requirements.txt`.
- **Decided by:** Anika

### 18. setup.md is the only setup guide

- **Date:** 2026-11-15
- **Decision:** Install guide: `docs/setup.md` is the only setup guide. It is written from what actually worked, with placeholders instead of personal names and emails.
- **Why:** One source of truth. Old guides had commands that don't work with this GOBNILP (no `-f`, no header, `bi.mat`).
- **Alternatives considered:** Keep the old Phase 0 guide alongside.
- **Decided by:** Proposed by Claude, approved by Anika

### 22. Move the baseline notes to docs/reports/phase-1.md

- **Date:** 2026-11-15
- **Status:** Superseded by entry 63 (the "dated correction notes" part; the move itself stands).
- **Decision:** Move `docs/baseline_reproduction_notes.md` to `docs/reports/phase-1.md` (with `git mv`, keeping its history). Fix errors only with dated correction notes.
- **Why:** Jirka has seen it, so it must not be silently rewritten. Reports live in `docs/reports/`.
- **Alternatives considered:** Delete it, or edit in place without notes.
- **Decided by:** Plan; Anika approved

### 23. Delete project-task-list.md

- **Date:** 2026-11-15
- **Decision:** **Delete `project-task-list.md`.** Kept elsewhere: the Python-first reasoning (entry 11), the Jirka file list (entries 12, 14). The `scoring2a.c` code map (`subset_tree`, `check_subset`, `add_subset`, the `if ( pruning )` block) moves to `docs/code-guide/scoring2a.md` in 1.5.0b.
- **Why:** Replaced by `docs/research-plan.md`; its phases and email numbers no longer match.
- **Alternatives considered:** Archive it in `docs/archive/` (CLAUDE.md says delete outdated plans).
- **Decided by:** Plan; Anika approved

### 24. Delete phase-0-detailed-steps.md

- **Date:** 2026-11-15
- **Decision:** **Delete `phase-0-detailed-steps.md`.** Correct parts merged into `docs/setup.md`, with the GOBNILP part rewritten (entry 18).
- **Why:** Superseded by `setup.md`; its GOBNILP commands were wrong for this build.
- **Alternatives considered:** Keep it as a second guide.
- **Decided by:** Plan; Anika approved

### 25. Delete phase-1-detailed-steps.md

- **Date:** 2026-11-15
- **Decision:** **Delete `phase-1-detailed-steps.md`.** Reasoning moved to entries 2, 3, 5–10; the CRLF gotcha to `setup.md`; the paper's possible "19 vs 17" inconsistency to `docs/reports/phase-1.md` (open questions).
- **Why:** A plan written before the work; the scripts and the Phase 1 report replace it.
- **Alternatives considered:** Keep it.
- **Decided by:** Plan; Anika approved

### 26. Delete docs/bnsl_header.md

- **Date:** 2026-11-15
- **Decision:** **Delete `docs/bnsl_header.md`.** Merged into `docs/setup.md` §8 (with the why). The GOBNILP explainer (step 1.5.7) will link there.
- **Why:** One source of truth.
- **Alternatives considered:** Keep as a separate note.
- **Decided by:** Plan; Anika approved

### 27. Delete docs/prompts/

- **Date:** 2026-11-15
- **Decision:** **Delete `docs/prompts/` (`phase-1.5-prompts.md`).**
- **Why:** Anika's personal working file, kept outside the repo; not project documentation.
- **Alternatives considered:** Keep it in `docs/`.
- **Decided by:** Anika

### 28. Git: local step branches, squash-merge to main

- **Date:** 2026-11-15
- **Decision:** Git: work on local `step-<id>` branches; after approval squash-merge into `main` as one commit per step and push `main`. Branches are never pushed.
- **Why:** GitHub shows only `main`, with one clear commit per step; an unapproved step can be thrown away locally.
- **Alternatives considered:** Push every branch; merge without squashing.
- **Decided by:** Anika (CLAUDE.md)

### 29. No compiled binaries in git

- **Date:** 2026-11-15
- **Decision:** No compiled binaries in git. Jirka's compiled `scoring2a` (from his Jul 8 "unix files.zip") is not kept. In 1.5.0b, `data/raw/README.md` records that the zip contained it, with its SHA-256, and that the original zip is still in that email. We always build our own from `scoring2a.c`. Our committed `src/scoring2a` binary is also removed from git in 1.5.0b.
- **Why:** Binaries can't be read or diffed, and depend on the machine. The source is enough to rebuild.
- **Alternatives considered:** Keep Jirka's binary in `tools/scoring2a/` for reference.
- **Decided by:** Anika (CLAUDE.md)

### 30. Every tracked file listed in a README

- **Date:** 2026-11-15
- **Decision:** Every tracked file must be listed in its folder's README (what it is, where it came from, original / derived + regenerating command / historical record). An inventory check runs at the end of every phase.
- **Why:** Every file in the repo is intentional and explained.
- **Alternatives considered:** No inventory.
- **Decided by:** Anika (CLAUDE.md)

### 31. Repository moved to the CLAUDE.md layout

- **Date:** 2026-11-15
- **Decision:** Repo moved to the CLAUDE.md layout with `git mv` (history kept): Jirka's data → `data/raw/`, derived data → `data/processed/`, tools → `tools/`, R scripts → `R/`. Full table: `docs/reports/1.5.0b.md`.
- **Why:** Originals can't be confused with derived files; one place per kind of file.
- **Alternatives considered:** Leave files where they were.
- **Decided by:** Plan; Anika approved

### 32. One results folder per experiment

- **Date:** 2026-11-15
- **Status:** Superseded in part by entry 63 (the dated note in the Phase 1 report was replaced by the rewrite).
- **Decision:** One results folder per experiment: Phase 1 outputs in `results/phase1/`, the 23-variable test outputs in `results/test-data24/`. The Phase 1 report got a dated note with the new paths.
- **Why:** CLAUDE.md layout; later steps add their own folders instead of mixing files.
- **Alternatives considered:** Keep loose files in `results/`.
- **Decided by:** Anika

### 33. Keep GOBNILP's DAG and CPDAG files

- **Date:** 2026-11-15
- **Decision:** Keep GOBNILP's DAG and CPDAG for the 44-variable model (`adjmat.*`, `pdagadjmat.*`) in `results/phase1/`. GOBNILP runs inside the results folder so they land there.
- **Why:** Needed for the CPDAG comparison in 1.5.3. They were committed once as `src/adjmat.*` (`fd2b479`) and removed as clutter in `c97da60`.
- **Alternatives considered:** Keep discarding them.
- **Decided by:** Anika

### 34. Delete the duplicate .jkl file

- **Date:** 2026-11-15
- **Decision:** **Delete `data/data24-training-1-bic.jkl`.**
- **Why:** Byte-identical copy of `data24-training-1-bic.scores`, made Aug 10 to try GOBNILP's `.jkl` reader; nothing uses it.
- **Alternatives considered:** Keep.
- **Decided by:** Plan; Anika approved

### 35. Delete run_gobnilp_pipeline.sh

- **Date:** 2026-11-15
- **Decision:** **Delete `scripts/run_gobnilp_pipeline.sh`**, replaced by `make phase1`.
- **Why:** The Makefile does the same steps with dependencies and without `cd src`.
- **Alternatives considered:** Keep both (two ways to run the same thing drift apart).
- **Decided by:** Plan; Anika approved

### 36. Remove the scoring2a binaries

- **Date:** 2026-11-15
- **Decision:** **Remove `src/scoring2a` (our binary) from git** and delete Jirka's binary (untracked `data/raw/scoring2a`; SHA-256 kept in `data/raw/README.md`). Build with `make scoring2a`.
- **Why:** Entry 29. Our rebuild from source has the same SHA-256 as the old committed binary (`2be2f069…`), so nothing is lost.
- **Alternatives considered:** —
- **Decided by:** Anika (entry 29)

### 37. Delete untracked duplicates in data/raw/

- **Date:** 2026-11-15
- **Decision:** **Delete the untracked duplicates in `data/raw/`** (`scoring2a.c`, `gobnilp.set`, `data24-training-1.dat`, `data24-training-1-bic.scores`): each was byte-identical (SHA-256) to the tracked copy, which was moved to its target place. `scoring-how-to-use-it.txt` and `script-data24-1` moved to `tools/scoring2a/` and are now tracked.
- **Why:** Exactly one copy of each file.
- **Alternatives considered:** —
- **Decided by:** Plan; Anika approved

### 38. Untrack docs/tasks/

- **Date:** 2026-11-15
- **Decision:** **Untrack `docs/tasks/1.5.0a.md`** and git-ignore `docs/tasks/`. The 1.5.0a verdicts it held are already in `docs/reports/1.5.0a.md` and entries 22–27.
- **Why:** CLAUDE.md: task files are scratch, written only when a step needs approval.
- **Alternatives considered:** Keep committing task files.
- **Decided by:** Anika (CLAUDE.md)

### 39. GOBNILP build moved to ~/tools/gobnilp/

- **Date:** 2026-11-15
- **Decision:** GOBNILP build moved from `src/gobnilp/` to `~/tools/gobnilp/` (gitlink removed with `git rm --cached`); `~/.local/bin/gobnilp` re-pointed; SCIP stays in `~/scipoptsuite-10.0.3/`.
- **Why:** Entry 16.
- **Alternatives considered:** Also move SCIP to `~/tools/` (not needed; GOBNILP's `scip` link is absolute).
- **Decided by:** Anika (entry 16)

### 40. Python package src/bnjoint/ plus thin scripts

- **Date:** 2026-11-15
- **Status:** Superseded in part: the winner rule by entry 55, the byte-identical regression test by entry 58.
- **Decision:** Python code split into the package `src/bnjoint/` (`config`, `io`, `gobnilp_io`, `cpt_scores`) plus thin argparse scripts. The Phase 1 winner rule is kept **unchanged** (fixed in 1.5.1); the STD summation order is kept so results are bit-identical.
- **Why:** CLAUDE.md; one tested copy of the math. Checked by `tests/test_phase1_regression.py` (byte-identical CSV).
- **Alternatives considered:** Keep the single script.
- **Decided by:** Plan; Anika approved

### 41. Editable install of the package

- **Date:** 2026-11-15
- **Decision:** The package is installed in editable mode (`-e .` in `requirements.txt`, settings in `pyproject.toml`).
- **Why:** `import bnjoint` works in scripts, tests and notebooks with no path tricks.
- **Alternatives considered:** Setting `PYTHONPATH=src` in the Makefile (scripts would fail when run by hand).
- **Decided by:** Proposed by Claude, approved by Anika

### 42. Pin only imported packages

- **Date:** 2026-11-15
- **Decision:** Pin only the packages the code imports (numpy, pandas, scipy, statsmodels, patsy, matplotlib); pytest and ruff in `requirements-dev.txt`. Versions: `docs/setup.md`.
- **Why:** A full `pip freeze` would pin ~100 Jupyter packages we don't use.
- **Alternatives considered:** Pin the full freeze.
- **Decided by:** Proposed by Claude, approved by Anika

### 43. .gitattributes line-ending rules

- **Date:** 2026-11-15
- **Decision:** `.gitattributes`: LF for our text files, but `-text` (bytes never changed) for `data/raw/**` and Jirka's files in `tools/`.
- **Why:** Jirka's originals are CRLF; converting them would change them and their checksums.
- **Alternatives considered:** `* text eol=lf` for everything (would rewrite the originals).
- **Decided by:** Proposed by Claude, approved by Anika

### 44. Redirectable Makefile output folders

- **Date:** 2026-11-15
- **Decision:** The Makefile's output folders can be redirected (`PROCESSED=…`, `OUT=…`). Verification rebuilds write to a scratch folder and are compared with the committed files; the reported `gobnilp-std-run.log` is not overwritten by a run whose only change is timings.
- **Why:** CLAUDE.md: never overwrite a reported result silently.
- **Alternatives considered:** Rebuild in place and rely on `git diff`.
- **Decided by:** Proposed by Claude, approved by Anika

### 46. Inventory check script

- **Date:** 2026-11-15
- **Decision:** `scripts/check_inventory.py` (`make inventory`) checks that every tracked file is named in its folder's (or nearest parent's) README.
- **Why:** CLAUDE.md inventory rule, as one command.
- **Alternatives considered:** Check by hand each phase.
- **Decided by:** Proposed by Claude, approved by Anika

### 47. Docs not created: archive/ and results-notes.md

- **Date:** 2026-11-15
- **Decision:** Docs not created: `docs/archive/` (in the research plan's layout, not in CLAUDE.md's; CLAUDE.md says delete, not archive) and `docs/paper-material/results-notes.md` (removed from CLAUDE.md: results live only in reports).
- **Why:** One source of truth.
- **Alternatives considered:** Create them.
- **Decided by:** Proposed by Claude, approved by Anika

### 48. Phase 1 report: duplicated setup sections replaced by pointers

- **Date:** 2026-11-15
- **Status:** Superseded by entry 63 (the Phase 1 report was rewritten without the pointer notes).
- **Decision:** In `docs/reports/phase-1.md`, the sections "Reproducibility details" (versions, build details), "How to reproduce these results from scratch" and "Environment gotchas" were replaced by pointers to `docs/setup.md` and `docs/code-guide/phase1-pipeline.md`, with dated notes. The determinism finding was kept. Old text: `git show a183df9:docs/reports/phase-1.md`.
- **Why:** One source of truth: setup facts live in `setup.md`. No Phase 1 result or finding changed.
- **Alternatives considered:** Keep the duplicated sections as a historical record.
- **Decided by:** Anika

### 49. Software versions only in setup.md

- **Date:** 2026-11-15
- **Decision:** Software versions live only in `docs/setup.md`; `methods-notes.md` links there instead of repeating them.
- **Why:** One source of truth.
- **Alternatives considered:** Repeat versions in the methods text.
- **Decided by:** Anika

### 50. make provenance writes to scratch/

- **Date:** 2026-11-15
- **Decision:** `make provenance` writes its rebuilt `BN-data.csv` copy to the git-ignored `scratch/provenance/`; `results/data-provenance/README.md` records the matching SHA-256. (The copy was never committed.)
- **Why:** CLAUDE.md: never commit a regenerated copy of a data file.
- **Alternatives considered:** Keep it in `results/` (git-ignored).
- **Decided by:** Anika

### 51. Remove the empty notebooks/ folder

- **Date:** 2026-11-15
- **Decision:** Removed the empty, untracked `notebooks/` folder (created Aug 7, never used, never in git).
- **Why:** No empty or unused folders in the working tree.
- **Alternatives considered:** Keep it for future notebooks.
- **Decided by:** Anika

### 54. References: references.md, papers/ never committed

- **Date:** 2026-11-15
- **Decision:** **References.** Paper PDFs live in `papers/` (repo root), git-ignored, never committed. Citations live once in `docs/references.md` (with how each was verified) and `docs/references.bib` (same keys); every doc that cites a paper links to its entry there. Unverifiable details are marked **Unverified**. Update 2026-11-16: de Campos & Ji 2011 verified from its PDF; Cussens et al. 2017 verified from IJAR 2023 ref. [6] (no DOI); the Cussens 2011 DOI printed in the Kybernetika paper is left out because it looks wrong.
- **Why:** The repo is public and most PDFs are copyrighted; one source of truth for citations.
- **Alternatives considered:** Commit the PDFs; cite inline in each doc.
- **Decided by:** Anika

### 57. Results layout for Phase 1.5

- **Date:** 2026-11-16
- **Status:** Superseded in part by entry 63 (the old CSV is deleted instead of marked superseded; `results/phase1/` now holds only the structures).
- **Decision:** **Results layout for Phase 1.5:** `results/phase1.5/<step>-<experiment>/` (`1.5.1-gobnilp-tie-fix/`, `1.5.2-hc-vs-table2/`). `results/phase1/` is the record of what was reported to Jirka on Sep 7 and is never overwritten; its `cpt-type-summary.csv` is marked "superseded by results/phase1.5/1.5.1-gobnilp-tie-fix/cpt-type-summary.csv, 2026-11-16". `make phase1` no longer has the CPT-type stage (it would regenerate the reported file); the stage is now `make phase1.5`. One report for the prompt: `docs/reports/1.5.1-1.5.2.md`.
- **Why:** CLAUDE.md: never silently rewrite a reported result; superseded results are kept and marked.
- **Alternatives considered:** Overwrite `results/phase1/cpt-type-summary.csv` and rely on git history.
- **Decided by:** Anika (prompt)

### 59. bnjoint.structures and --structure option

- **Date:** 2026-11-16
- **Decision:** Non-GOBNILP structures are read by a new module `bnjoint.structures` (adjacency matrix, reference table, per-node comparison). `fit_cpt_types.py` gets `--structure gobnilp|hc` (plus `--structure-file`; the old `--log` became `--structure-file`). Comparison with Table 2 is its own script, `compare_with_table2.py`.
- **Why:** Research plan 1.5.2 asks for the `--structure` option. One fitting script for any structure means one code path to test; reading and comparing are reusable for 1.5.5. Parent sets are compared as sets because parent order has no meaning.
- **Alternatives considered:** A separate `fit_cpt_types_hc.py` (duplicated code).
- **Decided by:** Research plan; details proposed by Claude, approved by Anika

### 60. phase-1.5 reads Phase 1 structures without prerequisites

- **Date:** 2026-11-16
- **Decision:** In the Makefile, the `phase1.5` rules read the Phase 1 structures (`gobnilp-std-run.log`, `bnlearn-hc-dag.csv`) **without listing them as prerequisites**.
- **Why:** Listed as prerequisites, make would rebuild them whenever a file further up the chain looked newer (after a fresh checkout, always: the scoring2a binary isn't in git), and that would rewrite the reported `results/phase1/` files. The cost: changing those files doesn't trigger a re-fit, but they are frozen records.
- **Alternatives considered:** Order-only prerequisites (make still rebuilds them if out of date).
- **Decided by:** Proposed by Claude, approved by Anika

### 61. Explainers for CPT types and one-parent MLR = STD

- **Date:** 2026-11-16
- **Decision:** Explainers 03 (CPT types) and 04 (one-parent MLR = STD) written now; the planned GOBNILP explainer moves from 04 to 05, the later planned ones to 06–10.
- **Why:** Anika asked for both in this prompt; the index keeps the reading order.
- **Alternatives considered:** Number them 10–11 (would break the beginner reading order).
- **Decided by:** Proposed by Claude, approved by Anika

### 62. Exception: one commit for steps 1.5.1–1.5.2

- **Date:** 2026-11-16
- **Decision:** **Exception to one commit per step:** steps 1.5.1 and 1.5.2 are merged into `main` as ONE squash commit, "Steps 1.5.1-1.5.2: tie rule, convergence check, hc structure reproduces Table 2".
- **Why:** The two steps share code (`fit_cpt_types.py`, `cpt_scores.py`) and tests (`test_phase1_regression.py` checks both result folders), so a 1.5.1-only commit would fail its own tests. The rule (entry 28) stays in force for later steps.
- **Alternatives considered:** Two commits (the first would not pass `make test`).
- **Decided by:** Anika

### 63. Documents describe the current state

- **Date:** 2026-11-16
- **Decision:** **Documents describe the current state** (CLAUDE.md rule changed by Anika). No inline correction or update notes; git is the archive of old versions; this log (append-only, superseded entries marked) and the experiment log are the history; each report has a "What we tried that didn't work" section; when a reported number changes, the report gets one line in its `## History` section (old value, why, `git show` command) plus a decision-log entry. Applied repo-wide: `docs/reports/phase-1.md` **rewritten** (goal, method, results, what didn't work, History, open questions; every research fact from its 14 notes kept, in the report or in this log); dated notes removed from `setup.md`, the code guides, explainers, other reports and READMEs. **`results/phase1/cpt-type-summary.csv` deleted** (10/30/4, superseded by `results/phase1.5/1.5.1-gobnilp-tie-fix/cpt-type-summary.csv`); the Phase 1 report's History names commit `9d80757`. Replaces entries 22, 48 and parts of 32 and 57.
- **Why:** Documents full of correction notes are hard to read and easy to misread; the reader wants the correct facts. Git keeps every old version, so nothing is lost, and the History line keeps reported-number changes visible. Anika: Jirka did not look closely at the September version and would not mind it being edited.
- **Alternatives considered:** (a) A one-off exception for `phase-1.md` only; keep dated notes elsewhere. (b) Keep dated notes everywhere (the old rule).
- **Decided by:** Anika

### 64. Regression tests read the reported CSV from git

- **Date:** 2026-11-16
- **Decision:** The regression tests read the reported Phase 1 CSV from git (`git show 9d80757:results/phase1/cpt-type-summary.csv`, `config.PHASE1_CPT_SUMMARY_GIT`) instead of from the deleted file. Same assertions as before.
- **Why:** Keeps the check that the BIC values never change from the numbers reported to Jirka, without keeping a superseded file in the working tree.
- **Alternatives considered:** Delete the two tests (forbidden: never delete a test); keep the CSV (contradicts entry 63).
- **Decided by:** Proposed by Claude (follows from entry 63)

### 65. One report per phase, plus an infrastructure report

- **Date:** 2026-11-16
- **Decision:** Reports are organized by phase: `docs/reports/phase-<n>.md`, one section per step, each starting with a 3-sentence summary for Jirka. Housekeeping (moves, tools, documentation) goes to `docs/reports/infrastructure.md` and this log. Done with `git mv`: `1.5.1-1.5.2.md` → `phase-1.5.md`; `1.5.0b.md` → `infrastructure.md`, with `1.5.0a.md` merged in and deleted (last at `fe269d3`). The research checks of 1.5.0a/b (data provenance, rebuild from raw data) became `phase-1.5.md` §1.5.0.
- **Why:** With reports per prompt, finding a result required knowing which prompt made it, and names like `1.5.1-1.5.2` only made sense to whoever was there. Research and housekeeping were mixed; Jirka and the paper need only the research.
- **Alternatives considered:** Keep reports per prompt; put everything from 1.5.0a/b in `infrastructure.md` (would hide paper claims 5–6 among housekeeping).
- **Decided by:** Anika

### 66. Naming: phase-1 / phase-1.5; explainers and reading notes without numbers

- **Date:** 2026-11-16
- **Decision:** One spelling for phases everywhere: `results/phase-1/`, `results/phase-1.5/`, `docs/reports/phase-1.md`, `docs/code-guide/phase-1-pipeline.md`, Make targets `phase-1` and `phase-1.5` (no aliases for the old names). Explainers have no numbers in their file names (`cpt-types.md`, …); their reading order lives only in `docs/explainers/README.md`. Reading notes are named by their `docs/references.md` key. `tests/test_phase1_regression.py` → `tests/test_regression.py` (it checks Phase 1 and 1.5; a hyphen isn't allowed in a Python module name). Python identifiers such as `PHASE1_DIR` keep their names; only their values changed.
- **Why:** `phase1`, `phase1.5` and `phase-1` were mixed; numbered explainer files forced a renumbering when two were added. A reading note and its citation should share one name.
- **Alternatives considered:** Keep the old names; keep aliases for the old Make targets (two names for one thing drift apart).
- **Decided by:** Anika

### 67. Decision log in two parts with a heading per entry

- **Date:** 2026-11-16
- **Decision:** This log is split into "Method" and "Repository and process", each entry a `###` heading with labelled lines instead of a table row. Every entry kept its number and text (checked by script: identical words before and after, apart from the italic markers moved to the Status line). Superseded entries get a Status line.
- **Why:** The method decisions are the paper's Methods choices and were buried among about 40 housekeeping entries; long paragraphs in table cells were hard to read, and a `|` inside code broke one table row.
- **Alternatives considered:** A topic column in one table; two separate files (would split the numbering).
- **Decided by:** Anika

### 68. Where numbers live, document jobs, glossary, theory, reading notes, volume rule

- **Date:** 2026-11-16
- **Decision:** (a) Result numbers appear only in reports, the experiment log, tests, `paper-material/paper-claims.md` (inside each claim, with its link), explainers' worked examples, and as the expected output next to a check command (README, `setup.md`, code guides, CLAUDE.md); everywhere else a link. This log is exempt (history). (b) `docs/README.md` states the job of each document type. (c) New: `docs/glossary.md` (explainers link terms to it); `docs/theory/` for statements and proofs (first: the one-parent MLR = STD lemma, with the explainer linking to it); one-page reading notes for vomlel2026, vomlel2023, decampos2018, decampos2011; `paper-claims.md` moved into `docs/paper-material/`. (d) Volume rule: skip explainer, methods-notes and paper-claims updates when a step adds no new concept or claim. All written into CLAUDE.md.
- **Why:** The same split was in about eight files, each a chance to drift. Overlapping document types need written boundaries. The paper's introduction, related work and lemma need homes before they are written. Documentation nobody reads lowers the signal.
- **Alternatives considered:** Numbers wherever useful (drift); no expected values next to commands (a check without its expected value is useless).
- **Decided by:** Anika
