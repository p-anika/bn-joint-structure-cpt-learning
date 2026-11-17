# CLAUDE.md — instructions for Claude Code in this repo

## Who you are working with
Anika is a high-school student researching with Dr. Jiří (Jirka) Vomlel (UTIA, Prague).
She has limited coding experience. She will NOT write documentation herself: you write all of
it, automatically, as part of every step. She learns the project by reading what you write and
asking questions in a separate chat. Define every term the first time you use it, explain the
"why" behind every choice, and never assume she knows a library, command, or piece of math.

## The project in three sentences
Jirka's Kybernetika 2026 paper learns a Bayesian network (BN) structure using only standard
tables (STD), then picks the best CPT type per node (STD, multinomial logistic regression MLR,
or ordinal logistic regression OLR). This project learns the structure and CPT types
**jointly**: every candidate parent set is scored with max(BIC_STD, BIC_MLR, BIC_OLR) and
GOBNILP finds the optimal structure. The research contribution is new **safe pruning rules**
that avoid scoring parent sets that cannot be optimal (an open problem; see IJAR 2023 Sec. 5).

## The plan
`docs/research-plan.md` is the step-by-step plan. Work ONLY on the steps Anika names in her
prompt. File paths in the plan are suggestions; the repo layout below wins. If a step is
unclear, or results suggest the plan should change, stop and ask. Never edit
`docs/research-plan.md` yourself.

## How every session runs
Anika's prompt names one or more steps. Work through them without stopping, except at the
checkpoints below.
1. **Plan only when approval is needed.** If a step deletes or moves files, changes a method or
   the research plan, or is ambiguous: write `docs/tasks/<step-id>.md` (what will change, how
   correctness is checked, risks) and stop for approval. `docs/tasks/` is git-ignored scratch.
   For every other step, write NO task file. Just do the work; the report records what was done.
2. **Do the work.** Tests first for any scoring, fitting, structure, or pruning code.
3. **Automatic checks instead of manual ones.** Run the full test suite, the expected-value
   checks stated in the prompt or plan, and `make phase1` (expect -64837.74) whenever pipeline
   code changed. If ANY result differs from what is expected, or something surprising happens,
   STOP and report before fixing or continuing. Never "fix" a surprising number without asking.
4. **Documentation before the checkpoint.** Complete the whole documentation checklist below
   before stopping, so Anika reviews code, numbers, and docs in one pass.
5. **One checkpoint at the end of the prompt**: what changed per step, headline numbers vs
   expected, anything you are unsure about, and ONE independent hand-check, only when the prompt
   produced a new number. An independent hand-check recomputes a number a different way from the
   code: from raw counts in a spreadsheet, from the paper, or by reasoning on a small example.
   Re-reading the CSV you just wrote does not count. Doc-only or reorganization steps need no
   hand-check; the automatic regression checks cover them.
   Also list the 1–3 riskiest assumptions in the code (e.g. how parents are coded for OLR).
6. **After approval**: commit and update `main` (git rules below).

## Git rules (keep GitHub clean)
- Work on a LOCAL branch `step-<id>` so an unapproved step can be thrown away. Never push branches.
- After approval: `git merge --squash` into `main`, ONE commit per step with message
  `Step <id>: <what was done>`, push `main`, delete the local branch.
- GitHub should show only `main`, with one clear commit per step.

## Documentation checklist — required for EVERY prompt, without being asked
Documentation is a deliverable, not an extra. Principle: each fact lives in ONE place and
everything else links to it. Never copy the same numbers or explanations into several files;
duplicated docs drift apart and become wrong. Update existing docs rather than adding new ones.
- [ ] **Docstrings and comments** in every file touched: module docstring (purpose, inputs,
      outputs, how to run, the math with paper equation numbers when known for sure);
      a docstring on every function (arguments, return value, an example); comments on any
      line a beginner would not understand. The detailed "how" lives here, next to the code.
- [ ] **Code guide**: one per pipeline stage (e.g. `docs/code-guide/phase1-pipeline.md`,
      `docs/code-guide/cpt-scoring.md`), plus `docs/code-guide/ARCHITECTURE.md` (a map of how all
      modules and scripts connect). Each guide covers: what the stage does, how data flows through
      it, a beginner-level walkthrough of the key functions, WHY it is designed this way and what
      alternatives were rejected, how to run it, and how to change common things safely. Link
      to docstrings instead of repeating them. Update the guide whenever the code changes.
- [ ] **Explainer** `docs/explainers/NN-<topic>.md` for every new concept, method, or tool:
      (1) plain-words definition, (2) why it matters in this project, (3) a tiny worked example
      with real numbers from our data, (4) where it appears in the code, (5) common confusions,
      (6) 3–5 "check your understanding" questions with answers at the bottom.
      Update existing explainers instead of duplicating. Keep `docs/explainers/README.md` as an
      ordered index (reading order for a beginner).
- [ ] **Report**: one per prompt (or per phase), `docs/reports/<id>.md` (1–2 pages): goal, what
      was done, results with exact numbers and the file each comes from, figures/tables,
      what we tried that didn't work (and why), surprises, open questions for Anika or Jirka. This is THE place results are written up.
- [ ] **Experiment log** `docs/experiment-log.md`, one row per run that produced a number:
      date | commit hash | exact command | inputs | output folder | headline result | notes.
- [ ] **Decision log** `docs/decision-log.md`, one entry per choice: date | decision | why |
      alternatives considered | decided by (Anika / Jirka / proposed by Claude, approved by Anika).
- [ ] **Paper material**:
      - `docs/paper-claims.md`: claim | link to the report section with the evidence | status
        (draft / checked by Anika / agreed with Jirka). Points to reports; does not copy them.
      - `docs/paper-material/methods-notes.md`: append paper-style paragraphs describing exactly
        what was done (data, parameters, software and versions, procedure) so a Methods section
        can be assembled later. Results are NOT repeated here; they live in the reports.
      - Figures: save as PNG and PDF in `results/<experiment>/figures/`, made by a script so they
        can be regenerated; reference them in the report.
- [ ] **README updates**: the root `README.md` (how to run each phase) and the README of any
      folder whose contents changed.

## Code organization and quality (best practice, always)
Target layout (keep it this way; propose changes in the task file before moving things):
```
README.md  CLAUDE.md  requirements.txt  Makefile  .gitignore  .gitattributes
data/raw/            Jirka's original files. READ-ONLY.
data/processed/      files derived by scripts (e.g. .dat, .scores, .bnsl). Regenerable.
src/bnjoint/         Python package: reusable code (io, scoring, structures, gobnilp_io, ...)
scripts/             thin command-line entry points that call src/bnjoint; one job per script
R/                   R scripts (bnlearn, CPDAGs, inference)
tools/scoring2a/     de Campos's scoring2a.c + build notes; tools/gobnilp/gobnilp.set
tests/               pytest tests mirroring src/bnjoint
results/<experiment>/  outputs; one folder per experiment, never overwritten silently
docs/                research-plan, setup, logs, code-guide/, explainers/, reports/,
                     theory/, reading-notes/, paper-material/   (tasks/ = git-ignored scratch)
```
Rules:
- Reusable logic lives in `src/bnjoint/`, never copy-pasted between scripts. One copy of the
  math: STD/MLR/OLR scoring lives in `src/bnjoint/cpt_scores.py`.
- Scripts take command-line arguments (argparse) and have no hard-coded absolute paths;
  shared paths and constants live in `src/bnjoint/config.py`.
- Small, single-purpose functions with clear names, type hints, and docstrings.
- Python formatted with `ruff format` and checked with `ruff check`; R kept tidy and commented.
- Pin dependencies in `requirements.txt`; record R package versions in `docs/setup.md`.
- `Makefile` targets for each pipeline stage (e.g. `make phase1`, `make test`) so any result can
  be reproduced with one command.
- Every result folder contains a `README.md` saying which command and commit produced it.
- External builds (SCIP, GOBNILP source) live OUTSIDE the repo (e.g. `~/tools/`); document how
  to build them in `docs/setup.md`.
- When reorganizing, re-run the affected pipeline and confirm the numbers are unchanged
  (e.g. Phase 1 GOBNILP objective -64837.74 and `cpt-type-summary.csv`) before merging.

## Hard rules
- Never modify the contents of `data/raw/`. Write derived files to `data/processed/` or `results/`.
- Never weaken, skip, or delete a test to make it pass. If a test fails, report it.
- Never call a pruning rule "safe" unless a test shows the pruned list gives the same GOBNILP
  optimum as the unpruned list.
- Ask before installing packages, deleting files, or changing the research plan.
- Never invent results, citations, or equation numbers. If unsure, say so in the docs.
- One source of truth per topic. Do not leave outdated plans, notes, or duplicate guides in the
  repo: merge what is still correct into the current docs and delete the rest (git history keeps
  it). Record every deletion in `decision-log.md` with the last commit hash where it existed.
  `docs/research-plan.md` is the only plan.
- Every tracked file must be intentional: listed in its folder's README with what it is, where it
  came from, and whether it is an original, a derived file (and which command regenerates it), or
  a historical record. Derived files that are not needed are deleted. Superseded results are
  deleted too (git keeps them); the report's History section names the commit that holds them.
  At the end of every phase, re-run the inventory check (`git ls-files` vs the READMEs) and report
  any file that is not documented.
- Never commit a regenerated copy of a data file just to prove it matches (e.g. a provenance
  rebuild of BN-data.csv): write it to a git-ignored scratch location and record the sha256
  match in a README instead.
- After a squash-merge, delete that step's file in `docs/tasks/` and remove any empty folders, so
  the working tree contains only intentional files.
- `data/raw/` holds Jirka's original files exactly as received, with a README listing each file,
  the email date it came from, and its SHA-256 checksum. No compiled binaries in git.
- Research history is content, not clutter, and is NEVER deleted: what was tried, what failed,
  dead ends, bugs found, surprising results, and why the approach changed. It lives in the
  experiment log (every run, including failed ones), the decision log (rejected alternatives and
  why), and a `## What we tried that didn't work` section in each report, written as a clear
  narrative. Before removing any old note, move the research fact it records into one of these.
- Documents describe the CURRENT state, written cleanly: no inline correction notes, no
  "update:" paragraphs about fixes to the documents themselves. Git is the archive of old versions, and the decision log is the history of
  what changed and why: it is append-only, and a superseded entry is marked superseded, never deleted.
- When a number that was reported (to Jirka or in a committed report) changes, add one line to
  that report's `## History` section: old value, why it changed, and the command to read the old
  version (e.g. `git show <commit>:<path>`). Also add a decision-log entry. Changes that were never
  reported need no History line.

## Conventions
- BIC (paper eq. 7/9): BIC = LL - (log N / 2) * params. Higher is better. Natural log.
- Parameters with k = 3 states, n parents: STD (k-1)k^n, MLR (k-1)(1+n(k-1)), OLR (k-1)+n.
- CPT-type ties: scores within 1e-6 are tied; ties go to STD, then OLR, then MLR.
- Data: `BN-data.csv`, 44 variables (a1–a30, d1–d14), 1661 rows, values -1/0/1.
- Languages: Python (data, scoring, fitting, pruning), R/bnlearn (structure comparison,
  CPDAGs, inference), Bash/Make (pipelines), C only if Anika approves.
- Environment: WSL2 Ubuntu, Python venv `.venv/`, GOBNILP on PATH. Run GOBNILP as
  `gobnilp -f <file>.bnsl -s tools/gobnilp/gobnilp.set`. Score files need the header added by
  `scripts/add_bnsl_header.sh` (variable-names line + `SCORES START`).

## Key references (in Anika's project, not in the repo)
- Vomlel, Kybernetika 62(3) 2026 — two-stage STD/MLR/OLR baseline (Table 2 = published model).
- de Campos et al., Artificial Intelligence 2018 — entropy-based pruning for BIC.
- Vomlel, Kratochvíl & Kratochvíl, IJAR 161 (2023) — mixed noisy-OR BNs; Algorithm 2 is the
  joint-scoring template; Sec. 5 documents failed pruning attempts and the open problem.