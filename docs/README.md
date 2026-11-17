# docs/: project documentation

Each fact lives in one place; everything else links to it. Documents describe the current
state; git keeps old versions. The history of what changed and why is in `decision-log.md` and
`experiment-log.md` (append-only), in each report's "What we tried that didn't work" section,
and, for reported numbers that changed, in the report's History section.

**New here?** Read the [glossary](glossary.md) for terms, then
[`code-guide/ARCHITECTURE.md`](code-guide/ARCHITECTURE.md) for the map, the
[explainers](explainers/README.md) in their reading order, and the reports.

## Which document does what

| Document type | Its job | Audience | Holds result numbers? |
|---|---|---|---|
| **Report** (`reports/phase-<n>.md`) | Results of a phase, one section per step, with exact numbers and the file each comes from; what we tried that didn't work; surprises; History of changed numbers; open questions. Starts with a 3-sentence summary for Jirka. | Anika, Jirka, the paper | **Yes**, the place results are written up |
| **Infrastructure report** (`reports/infrastructure.md`) | Housekeeping: moves, tools, documentation changes, and where things went. | Anika, future maintainers | No |
| **Decision log** | Every choice and why, in two parts (Method; Repository and process). Append-only history. | Anika, Jirka, the paper's Methods | Only as history |
| **Experiment log** | Every run that produced a number: command, commit, output, headline result. Append-only history. | Anyone reproducing a result | **Yes** |
| **Paper material** (`paper-material/`) | `paper-claims.md`: each sentence for the paper, with its numbers and a link to the evidence. `methods-notes.md`: paper-style Methods paragraphs (no results). | The paper | Claims only |
| **Theory** (`theory/`) | Precise statements and proofs. | The paper, Jirka | No |
| **Reading notes** (`reading-notes/<reference key>.md`) | One page per paper: the problem, the key result in plain words, what we reuse or extend. | Anika, the paper's related work | No |
| **Explainer** (`explainers/`) | One concept, for learning: plain definition, why it matters, a worked example with our data, common confusions, questions. | Beginners, Anika | Only in worked examples |
| **Glossary** | One-line definitions, each linking to where the term is explained. | Everyone | No |
| **Code guide** (`code-guide/`) | How a part of the code works and why it is built that way; how to run and change it safely. | Anyone changing the code | Only expected outputs of check commands |
| **Docstrings and comments** (in the code) | The exact details: arguments, return values, formulas, examples. | Anyone reading the code | Only in examples |
| **Setup** (`setup.md`) | How to build the environment; the tool versions in use (the only place for them). | Anyone on a new machine | Only expected outputs of check commands |
| **References** (`references.md`, `.bib`) | Every cited paper and tool, how we use it, how the citation was verified. | The paper | No |
| **Research plan** | The step-by-step plan. Edited only by Anika. | Anika, Claude | Expected values only |

## Files and folders

| Path | What it holds |
|---|---|
| `research-plan.md` | The step-by-step research plan. The only plan; edited only by Anika. |
| `setup.md` | How to rebuild the environment, and the tool versions we use. |
| `glossary.md` | One-line definitions of every project term. |
| `decision-log.md` | Every choice: date, decision, why, alternatives, who decided; deleted files with the last commit where they existed. |
| `experiment-log.md` | Every run that produced a number: date, commit, command, inputs, output, result. |
| `references.md` | Every paper and software package we rely on: citation, DOI or link, use, verification. |
| `references.bib` | The same references as BibTeX (same keys), for the paper. |
| `paper-material/paper-claims.md` | Claims for the paper, each with its numbers and a link to the evidence. |
| `paper-material/methods-notes.md` | Paper-style paragraphs on what was done (data, settings, software). |
| `code-guide/ARCHITECTURE.md` | Map of how modules, scripts, Make targets and data connect. Start here. |
| `code-guide/phase-1-pipeline.md` | Guide to the Phase 1 pipeline (`make phase-1`). |
| `code-guide/cpt-scoring.md` | Guide to STD/MLR/OLR scoring, the tie rule and the Table 2 comparison (`make phase-1.5`). |
| `code-guide/scoring2a.md` | What de Campos's `scoring2a.c` does, including its pruning. |
| [`explainers/`](explainers/README.md) | Beginner concept guides; reading order in the README. |
| `reports/phase-1.md` | Phase 1: the two-stage baseline (exact and hill-climbing structures, CPT types). |
| `reports/phase-1.5.md` | Phase 1.5: data and reproducibility checks, tie rule, reproducing Table 2. |
| `reports/infrastructure.md` | Repository, tools and documentation work. |
| [`theory/`](theory/README.md) | Statements and proofs. |
| [`reading-notes/`](reading-notes/README.md) | One-page notes on the key papers. |
| `tasks/` | Not in git: scratch plans, written only for steps that need approval. |

Paper PDFs are kept locally in `papers/` at the repo root, which is git-ignored (never commit
them: the repo is public and most are copyrighted).
