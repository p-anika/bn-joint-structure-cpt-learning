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
1. **Plan first.** For each requested step write `docs/tasks/<step-id>.md`: goal, inputs,
   outputs, files to create/change, language, how correctness will be checked, risks.
   Stop and wait for Anika's approval.
2. **One step at a time** on a branch `step-<id>` (e.g. `step-1.5.1`). Tests first for any
   scoring, fitting, structure, or pruning code.
3. **Stop after each step** with: what changed, headline numbers, and ONE number for Anika to
   hand-check with exact instructions for checking it.
4. After approval: complete ALL documentation in the checklist below, run the full test suite,
   commit (clear message), push, merge to `main`, delete the branch.

## Documentation checklist — required for EVERY step, without being asked
Documentation is a deliverable, not an extra. A step is not done until all of these are done.
- [ ] **Docstrings and comments** in every file touched: module docstring (purpose, inputs,
      outputs, how to run, the math with paper equation numbers when known for sure);
      a docstring on every function (arguments, return value, an example); comments on any
      line a beginner would not understand.
- [ ] **Code guide** `docs/code-guide/<module-or-script>.md` for every new or changed module or
      script: (1) what it does in one paragraph, (2) where it fits in the pipeline (inputs come
      from, outputs go to), (3) a walkthrough of how it works, function by function, in plain
      language, (4) WHY it is designed this way and what alternatives were rejected,
      (5) how to run it and what the output looks like, (6) how to change common things safely,
      (7) links to the relevant explainers.
- [ ] **Explainer** `docs/explainers/NN-<topic>.md` for every new concept, method, or tool:
      (1) plain-words definition, (2) why it matters in this project, (3) a tiny worked example
      with real numbers from our data, (4) where it appears in the code, (5) common confusions,
      (6) 3–5 "check your understanding" questions with answers at the bottom.
      Update existing explainers instead of duplicating. Keep `docs/explainers/README.md` as an
      ordered index (reading order for a beginner).
- [ ] **Step report** `docs/reports/<step-id>.md` (1–2 pages): goal, what was done, results with
      exact numbers, figures/tables produced, surprises, open questions for Anika or Jirka.
- [ ] **Experiment log** `docs/experiment-log.md`, one row per run that produced a number:
      date | commit hash | exact command | inputs | output folder | headline result | notes.
- [ ] **Decision log** `docs/decision-log.md`, one entry per choice: date | decision | why |
      alternatives considered | decided by (Anika / Jirka / proposed by Claude, approved by Anika).
- [ ] **Paper material**:
      - `docs/paper-claims.md`: claim | evidence file | status (draft / checked by Anika / agreed with Jirka).
      - `docs/paper-material/methods-notes.md`: append paper-style paragraphs describing exactly
        what was done (data, parameters, software and versions, procedure) so a Methods section
        can be assembled later.
      - `docs/paper-material/results-notes.md`: append paper-style paragraphs and tables of
        results with the file each number came from.
      - Figures: save as PNG and PDF in `results/<experiment>/figures/`, made by a script so they
        can be regenerated; record them in the step report.
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
docs/                research-plan, setup, logs, code-guide/, explainers/, reports/, tasks/,
                     theory/, reading-notes/, paper-material/, archive/
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
- Never silently rewrite a result that was already reported (to Jirka or in a report). Correct it
  with a dated note, e.g. "Correction (2026-11-20): the split was 10/30/4 because of a tie-breaking
  bug; corrected to 16/24/4, see docs/reports/1.5.1.md."

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
