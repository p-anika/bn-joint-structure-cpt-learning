# docs/: project documentation

Each fact lives in one place; everything else links to it. Documents describe the current
state; git keeps old versions. The history of what changed and why is in `decision-log.md` and
`experiment-log.md` (append-only), in each report's "What we tried that didn't work" section,
and, for reported numbers that changed, in the report's History section.

| Path | What it holds |
|---|---|
| `research-plan.md` | The step-by-step research plan. The only plan; edited only by Anika. |
| `setup.md` | How to rebuild the environment, and the tool versions we use. |
| `decision-log.md` | Every choice: date, decision, why, alternatives, who decided. Also every deleted file, with the last commit where it existed. |
| `experiment-log.md` | Every run that produced a number: date, commit, command, inputs, output, result. |
| `references.md` | Every paper and software package we rely on: full citation, DOI or link, how this project uses it, how it was verified. Other docs link to its entries. |
| `references.bib` | The same references as BibTeX (same keys), for the paper. |
| `paper-claims.md` | Claims for the paper, each linked to the report section with the evidence. |
| `paper-material/methods-notes.md` | Paper-style paragraphs on what was done (data, settings, software), for the Methods section. |
| `code-guide/ARCHITECTURE.md` | Map of how modules, scripts, Make targets and data connect. Start here. |
| `code-guide/phase1-pipeline.md` | Guide to the Phase 1 pipeline (`make phase1`). |
| `code-guide/cpt-scoring.md` | Guide to STD/MLR/OLR scoring, the tie rule and the Table 2 comparison (`cpt_scores.py`, `structures.py`, `make phase1.5`). |
| `code-guide/scoring2a.md` | What de Campos's `scoring2a.c` does, including its pruning. |
| [`explainers/`](explainers/README.md) | Beginner concept guides, with an index in reading order. |
| `reports/phase-1.md` | Phase 1 report: the two-stage baseline (exact and hill-climbing structures, CPT types). |
| `reports/1.5.0a.md` | Step 1.5.0a: audit of the old Markdown files. |
| `reports/1.5.0b.md` | Step 1.5.0b: repo reorganization and data verification. |
| `reports/1.5.1-1.5.2.md` | Steps 1.5.1–1.5.2: tie rule and convergence check; reproducing Table 2 on the hc structure. |
| [`theory/`](theory/README.md) | Proofs and derivations (from Phase 3). |
| [`reading-notes/`](reading-notes/README.md) | Notes on papers. |
| `tasks/` | Not in git: scratch plans, written only for steps that need approval. |

Paper PDFs are kept locally in `papers/` at the repo root, which is git-ignored (never commit
them: the repo is public and most are copyrighted).
