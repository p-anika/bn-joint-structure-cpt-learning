# Phase 1.5 — Claude Code prompts

Use one prompt per step, in order. Wait for Claude Code to stop, review, then approve or ask for
changes. Type `/clear` between steps to give Claude Code a fresh context (everything it needs is in
CLAUDE.md, the plan, and the docs it writes). Press Shift+Tab to switch into plan mode if it starts
coding before showing you a plan.

---

## P0 — Orientation (changes nothing)

```
Read CLAUDE.md and docs/research-plan.md, then explore the whole repo. Do not change anything yet.
Tell me, in plain language and in under one page:
1. Your understanding of the project and of Phase 1.5.
2. The current state of the repo and anything messy or risky you notice (for example, git reports
   src/gobnilp as modified with untracked content).
3. Any questions you have before we start.
```

## P1a — Step 1.5.0a: audit the old Markdown files

```
Let's do step 1.5.0a from docs/research-plan.md: audit every old Markdown file in the repo
(project-task-list.md, phase-0-detailed-steps.md, phase-1-detailed-steps.md, docs/bnsl_header.md,
docs/baseline_reproduction_notes.md, README.md, and any others you find outside the GOBNILP source
folder).

Do not delete or edit anything yet. For each file, check it section by section against the actual
code, results, git history and docs/research-plan.md, and write docs/tasks/1.5.0a.md with a table:
file | section | accurate / outdated / wrong (and why) | action (merge into which file / correct
with a dated note / delete). The plan lists suggested actions for each file; tell me if you
disagree with any of them. Then stop for my approval.

After I approve: carry out the actions, record every deletion in docs/decision-log.md with the
last commit hash where the file existed, and write docs/reports/1.5.0a.md.
```

## P1b — Step 1.5.0b: reorganize the repo and set up documentation

```
Let's do step 1.5.0b from docs/research-plan.md. Plan first: write docs/tasks/1.5.0b.md with every
file move, every new file, and how you will prove nothing broke. Then stop for my approval.

Constraints:
- Use `git mv` so file history is kept. Do not change any numbers or results.
- Move Jirka's original files to data/raw/ and derived files to data/processed/.
- Create the src/bnjoint/ package, R/, tools/, tests/, and the docs/ structure from CLAUDE.md.
- Take the GOBNILP source folder out of the repo (git rm --cached src/gobnilp, add it to .gitignore).
  Keep the build itself outside the repo and document how to build SCIP, SoPlex, GOBNILP and
  scoring2a in docs/setup.md, including the .bnsl header fix and the `-f` flag.
- Move the 23-variable test outputs (adjmat*, pdagadjmat*) to results/test-data24/.
- Add requirements.txt (pinned), a Makefile (at least `make phase1` and `make test`),
  .gitattributes (LF line endings), and README files for each folder.
- Backfill docs/decision-log.md, docs/experiment-log.md, docs/paper-claims.md, and
  docs/paper-material/methods-notes.md from docs/baseline_reproduction_notes.md and the git history.
- Write a code guide for every existing script.
- Before merging, run `make phase1` and confirm the GOBNILP objective is still -64837.74 and
  results/.../cpt-type-summary.csv is identical to the old one.
```

## P2 — Step 1.5.1: fix CPT-type tie-breaking

```
Let's do step 1.5.1. Plan first in docs/tasks/1.5.1.md, then stop.

Use the tie rule from CLAUDE.md (scores within 1e-6 are tied; STD, then OLR, then MLR). Also check
and log whether every MLR and OLR fit converged. Write the tests first: MLR equals STD for 0- and
1-parent families, and the tie rule picks STD.

Expected new split on the GOBNILP structure: 16 STD / 24 MLR / 4 OLR. If you get anything else,
stop and explain why before changing anything.

Do the full documentation checklist, including an explainer on why one-parent MLR and STD are
the same model, with a worked example from our data.
```

## P3 — Step 1.5.2: verify CPT fitting against the published model

```
Let's do step 1.5.2. Plan first, then stop.

Run the CPT-type fitting on the bnlearn hill-climbing structure (results from scripts/bnlearn_hc.R)
and compare node by node with Table 2 of the Kybernetika paper. Encode Table 2 (all 44 families
and their CPT types) in data/reference/kybernetika-table2.csv and show it to me so I can check it
against the paper before you use it.

Expected: 19 STD, 22 MLR, 3 OLR, with the same type for every node. If anything differs, stop and
investigate possible causes (OLR parent coding, fitting method, convergence, ties) and report
before changing code. Note in the report that the paper's text says "17 standard CPTs" while
Table 2 lists 19.

Full documentation checklist. Add the reproduction result to paper-claims.md.
```

## P4 — Step 1.5.3: compare CPDAGs

```
Let's do step 1.5.3. Plan first, then stop.

In R (R/compare_structures.R), build both networks (GOBNILP and hill-climbing), compute their
CPDAGs, and report shd(), hamming() and compare() results. Produce a table classifying every edge
as: same; reversed but equivalent (undirected in both CPDAGs); reversed and compelled; only in
GOBNILP; only in hill-climbing. Make a side-by-side figure of the two CPDAGs with differences
highlighted.

Write an explainer on Markov equivalence and CPDAGs using a real edge from our data
(for example a3-a4) as the worked example. Full documentation checklist.
```

## P5 — Step 1.5.4: compare BICs

```
Let's do step 1.5.4. Plan first, then stop.

Compute the four BIC numbers: table-only and two-stage, for GOBNILP and for hill-climbing.
Cross-check the table-only BIC two ways (bnlearn score() and our Python code) and explain any
difference. Confirm GOBNILP's table-only BIC is at least hill-climbing's; if not, stop.

Put the four numbers in a results table, plus how much each method gains from the two-stage
CPT selection. Full documentation checklist, including results-notes.md and paper-claims.md.
```

## P6 — Step 1.5.5: CPT-type differences between the two structures

```
Let's do step 1.5.5. Plan first, then stop.

Build results/.../cpt-type-diff.csv with: variable, parents (GOBNILP), parents (hill-climbing),
CPT type in each, and whether the parent sets are the same. Write a short analysis: do CPT-type
differences happen only where parent sets differ? Highlight any interesting families.
Full documentation checklist.
```

## P7 — Steps 1.5.6–1.5.7: cleanup and documentation audit

```
Let's do steps 1.5.6 and 1.5.7. Plan first, then stop.

1. Write the root README: project summary, setup, repo map, and how to reproduce each phase with make.
2. Fix stale or unfinished text in older notes.
3. Make sure explainers exist for: Bayesian networks, BIC, the three CPT types, GOBNILP and exact
   search, CPDAGs, and the whole Phase 1/1.5 pipeline end to end. Order them for a beginner in
   docs/explainers/README.md.
4. Audit the entire repo against the CLAUDE.md documentation checklist and fill every gap.
5. Run `make test` and `make phase1` at the end and report the results.
```

## P8 — Wrap-up for Email #3

```
Write docs/reports/phase-1.5-summary.md for my email to Jirka. Include:
- the hill-climbing reproduction result (does it match Table 2?);
- the corrected CPT split and why it changed;
- the CPDAG comparison (SHD and the real differences);
- the four BIC numbers;
- the CPT-type difference table;
- open questions;
- links to every evidence file.
Then tag the commit `email-3` and push.
```

Then bring `phase-1.5-summary.md` to the chat to draft the email.

---

## Helper prompts (use any time)

- `Explain what you just did as if I'm a beginner, then quiz me with 3 questions.`
- `Before I approve: what could be wrong with this result, and how did you rule it out?`
- `Show me step by step how to hand-check <number> myself.`
- `Which files did you change, and why each one?`
- `Is anything in this step not yet documented according to the CLAUDE.md checklist?`
