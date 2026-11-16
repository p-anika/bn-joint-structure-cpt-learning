# Decision log

One entry per choice made in this project: what was decided, why, what else was considered,
and who decided. Entries are never deleted. If a decision is reversed, add a new entry that
points to the old one.

- **Who decided** uses: *Anika*, *Jirka*, or *proposed by Claude, approved by Anika*.
- **Backfilled** entries were made before this log existed. Their reasoning comes from the old
  plan files deleted in step 1.5.0a, which can still be read in git at commit `6a38593`.
- **Deletions** say which commit last contained the file. To see a deleted file:
  `git show <commit>:<path>`, e.g. `git show 6a38593:project-task-list.md`.

## Setup and data

| # | Date | Decision | Why | Alternatives considered | Decided by |
|---|---|---|---|---|---|
| 1 | Aug 2026 (backfilled) | Work in WSL2 Ubuntu on Windows. | scoring2a and GOBNILP/SCIP are documented and tested on Linux. | Native Windows build (poorly documented, fiddly). | Anika |
| 2 | Aug 5, 2026 (backfilled) | Use `BN-data.csv` as sent; don't re-derive it from `preprocessed-data.csv`. | Jirka asked for it, so both of us work from identical data. | Re-run his R conversion ourselves (kept only as an optional check, entry 13). | Jirka |
| 3 | Aug 2026 (backfilled) | Use our own GOBNILP build (commit `5441edf`) on SCIP 10.0.3 + SoPlex 8.0.3. | It works once the `.bnsl` header is added, and it is the current version. | Jirka's GOBNILP 1.6.3 / SCIP 3.2.1 (2016-era; hard to rebuild). | Anika |
| 4 | Aug 18, 2026 (backfilled) | Add a variable-names line and `SCORES START` to every scores file (`scripts/add_bnsl_header.sh`). | This GOBNILP's reader requires them. Jirka's Aug 12 pointer to `chest_100_1_3.bnsl` confirmed the format. | Edit files by hand (error-prone). | Anika, confirmed by Jirka |
| 5 | Sep 6, 2026 (backfilled) | scoring2a settings: alpha = 1, palim = 9, `prune`, score `bic`. | alpha = 1 gives the true BIC (de Campos's note `scoring-how-to-use-it.txt`). `1 9 prune 0 bic` is exactly Jirka's example `script-data24-1`. The resulting network has at most 2 parents per node, like Table 2. The paper's structure came from hc, so no scoring2a setting "from the paper" exists (entry 19). | Smaller palim (faster, but might cut off the optimum). | Anika |
| 6 | Sep 6, 2026 (backfilled) | Read learned parent sets from the GOBNILP console log (`child:-{...}` lines), not from `bi.mat`. | This GOBNILP ignores the `adjacencymatrix` setting in `gobnilp.set`, so `bi.mat` is never written. The log lists every family unambiguously. | Fix `gobnilp.set` for the new parameter names (possible later). | Anika |
| 7 | Sep 6, 2026 (backfilled) | STD parameter count uses all k^n parent configurations, even unobserved ones: (k−1)·k^n. | Paper eq. 6; scoring2a counts the same way, so our BIC matches GOBNILP's scores. | Count only observed configurations (gives different BIC numbers). | Anika (following the paper) |
| 8 | Sep 6, 2026 (backfilled) | MLR: dummy-code each parent, state −1 as reference. OLR: use raw parent values −1/0/1, one coefficient per parent. | Paper eq. 11 (MLR dummies) and eq. 16 (OLR uses parent values directly). **Still to confirm with Jirka**; it is the planned Email #3 question. | Dummy-code OLR parents too (more parameters; not the paper's eq. 17 count). | Anika (following the paper) |
| 9 | Sep 6, 2026 (backfilled) | No OLR for a node with 0 parents (score −∞, never chosen). | OLR with no parents is the same as STD/MLR; the paper only uses OLR with parents. | Fit an intercept-only OLR (equals STD; adds nothing). | Anika (following the paper) |
| 10 | Sep 7, 2026 (backfilled) | Run bnlearn `hc(d, score = "bic")` with all other settings default, after `set.seed(1)`. | Matches how Jirka learned the paper's structure (entry 19). The seed makes the run repeatable. | Other scores or restarts (not what the paper did). | Anika |
| 11 | Sep 2026 (backfilled) | Prototype joint scoring in Python first; C only if Python is too slow. | Much faster to write and debug. Already in the research plan ("C only if Python is too slow in Phase 4"). | Modify `scoring2a.c` directly. | Anika |
| 12 | 2026-11-15 | **Data provenance.** Jirka's original files go in `data/raw/` (read-only): `preprocessed-data.csv` (Jul 8: his preprocessed survey on the original 1–7 scale, all columns); `BN-data.csv` (Aug 5: the exact 44-variable data of the Kybernetika paper, made from `preprocessed-data.csv` by his R code: keep columns 29–72 = a1–a30, d1–d14; map 1–3 → −1, 4 → 0, 5–7 → +1); `data24-training-1.dat` and `data24-training-1-bic.scores` (Jul 8, "unix files.zip": his 23-variable GOBNILP test example). Everything else in `data/` (`bn-data-44.*`, `*-fixed.bnsl`, `*.jkl`, the varnames file) was made by us and goes to `data/processed/` or is regenerated. | Keep originals separate from anything we derive, so nothing we do can change them. | Mixing raw and derived files (current state). | Anika |
| 13 | 2026-11-15 | Optional check in 1.5.0b: apply Jirka's R conversion to `preprocessed-data.csv` and check it reproduces `BN-data.csv` exactly. Results go to `results/`, never `data/raw/`. | Confirms we understand where the data came from. | Skip the check. | Anika |
| 14 | 2026-11-15 | Jirka's program files go in `tools/`, not `data/raw/`: `scoring2a.c`, `scoring-how-to-use-it.txt`, `script-data24-1` in `tools/scoring2a/`; `gobnilp.set` in `tools/gobnilp/` (Jul 8 zip). Moved in 1.5.0b. | They are tools, not data. CLAUDE.md layout. | Keep them in `src/` (meant for our Python package). | Anika |
| 15 | 2026-11-15 | Table 2 of the Kybernetika paper (p. 411) lives in `data/reference/kybernetika-table2.csv` (columns: variable, n_parents, parents separated by ";", cpt_type) and is read-only. Anika typed it in. Folder added to the layout in 1.5.0b. | Step 1.5.2 compares our fitting to it node by node. | Put it in `data/raw/` (it isn't a file Jirka sent). | Anika |
| 16 | 2026-11-15 | Take the GOBNILP source out of the repo (`git rm --cached src/gobnilp`). Move the build to `~/tools/gobnilp/`, redirect `~/.local/bin/gobnilp`, check its internal `scip` link. Prove it works on the data24 test file and with `make phase1` (−64837.74). Document it in `docs/setup.md`. Done in 1.5.0b. | It is someone else's repo nested inside ours (a broken submodule pointer). CLAUDE.md keeps external builds outside the repo. | Make it a proper git submodule (more complex, not needed). | Anika |
| 17 | 2026-11-15 | Install pytest and ruff into `.venv`, pinned in a separate `requirements-dev.txt`. Done in 1.5.0b. | Needed for tests and formatting (CLAUDE.md). A separate file keeps the tools apart from the packages the research code needs. | Put them in `requirements.txt`. | Anika |
| 18 | 2026-11-15 | Install guide: `docs/setup.md` is the only setup guide. It is written from what actually worked, with placeholders instead of personal names and emails. | One source of truth. Old guides had commands that don't work with this GOBNILP (no `-f`, no header, `bi.mat`). | Keep the old Phase 0 guide alongside. | Proposed by Claude, approved by Anika |

## Confirmations from Jirka

| # | Date | Decision / fact | Source | Decided by |
|---|---|---|---|---|
| 19 | Sep 28, 2026 | The paper's structure was learned with bnlearn hc: "The model structure in the Kybernetika paper was learnt using the hc procedure from the R package bnlearn." So `scripts/bnlearn_hc.R` is the paper-matching structure, and GOBNILP gives the exact optimum. | Jirka's email, Sep 28, 2026 | Jirka |
| 20 | Sep 28, 2026 | Figure 4's numbers are cross-validated: "I can confirm that the BIC, number of parameters and log-likelihood in Figure 4 come from the 10-fold cross-validation." So they can't be compared directly with our full-data BIC. | Jirka's email, Sep 28, 2026 | Jirka |
| 21 | Sep 28, 2026 | Jirka called our exact GOBNILP experiments "novel and valuable". Recorded because the research plan relies on it when deciding when to ask about a paper. | Jirka's email, Sep 28, 2026 | Jirka |

## Documentation and deletions (step 1.5.0a)

All five deleted files exist for the last time at commit **`6a38593`**.

| # | Date | Decision | Why | Alternatives considered | Decided by |
|---|---|---|---|---|---|
| 22 | 2026-11-15 | Move `docs/baseline_reproduction_notes.md` to `docs/reports/phase-1.md` (with `git mv`, keeping its history). Fix errors only with dated correction notes. | Jirka has seen it, so it must not be silently rewritten. Reports live in `docs/reports/`. | Delete it, or edit in place without notes. | Plan; Anika approved |
| 23 | 2026-11-15 | **Delete `project-task-list.md`.** Kept elsewhere: the Python-first reasoning (entry 11), the Jirka file list (entries 12, 14). The `scoring2a.c` code map (`subset_tree`, `check_subset`, `add_subset`, the `if ( pruning )` block) moves to `docs/code-guide/scoring2a.md` in 1.5.0b. | Replaced by `docs/research-plan.md`; its phases and email numbers no longer match. | Archive it in `docs/archive/` (CLAUDE.md says delete outdated plans). | Plan; Anika approved |
| 24 | 2026-11-15 | **Delete `phase-0-detailed-steps.md`.** Correct parts merged into `docs/setup.md`, with the GOBNILP part rewritten (entry 18). | Superseded by `setup.md`; its GOBNILP commands were wrong for this build. | Keep it as a second guide. | Plan; Anika approved |
| 25 | 2026-11-15 | **Delete `phase-1-detailed-steps.md`.** Reasoning moved to entries 2, 3, 5–10; the CRLF gotcha to `setup.md`; the paper's possible "19 vs 17" inconsistency to `docs/reports/phase-1.md` (open questions). | A plan written before the work; the scripts and the Phase 1 report replace it. | Keep it. | Plan; Anika approved |
| 26 | 2026-11-15 | **Delete `docs/bnsl_header.md`.** Merged into `docs/setup.md` §8 (with the why). The GOBNILP explainer (step 1.5.7) will link there. | One source of truth. | Keep as a separate note. | Plan; Anika approved |
| 27 | 2026-11-15 | **Delete `docs/prompts/` (`phase-1.5-prompts.md`).** | Anika's personal working file, kept outside the repo; not project documentation. | Keep it in `docs/`. | Anika |

## Repository rules (2026-11-15)

| # | Date | Decision | Why | Alternatives considered | Decided by |
|---|---|---|---|---|---|
| 28 | 2026-11-15 | Git: work on local `step-<id>` branches; after approval squash-merge into `main` as one commit per step and push `main`. Branches are never pushed. | GitHub shows only `main`, with one clear commit per step; an unapproved step can be thrown away locally. | Push every branch; merge without squashing. | Anika (CLAUDE.md) |
| 29 | 2026-11-15 | No compiled binaries in git. Jirka's compiled `scoring2a` (from his Jul 8 "unix files.zip") is not kept. In 1.5.0b, `data/raw/README.md` records that the zip contained it, with its SHA-256, and that the original zip is still in that email. We always build our own from `scoring2a.c`. Our committed `src/scoring2a` binary is also removed from git in 1.5.0b. | Binaries can't be read or diffed, and depend on the machine. The source is enough to rebuild. | Keep Jirka's binary in `tools/scoring2a/` for reference. | Anika (CLAUDE.md) |
| 30 | 2026-11-15 | Every tracked file must be listed in its folder's README (what it is, where it came from, original / derived + regenerating command / historical record). An inventory check runs at the end of every phase. | Every file in the repo is intentional and explained. | No inventory. | Anika (CLAUDE.md) |
