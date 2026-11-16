# Joint Structure + CPT-Type Learning: Full Research Plan

Nov 15, 2026 · @Anika

## How to use this plan

You are at the end of Phase 1. The next action is Phase 1.5, which ends with Email #3 to Jirka. Ask him about writing a paper together in Email #4, once joint learning beats the two-stage method.

Where things stand:

- Phase 1 is finished and in the repo. The exact GOBNILP structure has 69 arcs and BIC −64,837.74. The two-stage model on that structure scores −64,249.31.
- Your bnlearn hill-climbing structure matches the paper's Table 2 exactly, arc for arc (66 arcs).
- Your STD/MLR/OLR split was 10/30/4 because of a tie-breaking bug. With ties going to STD it is 16/24/4. The paper reports 19/22/3.
- Jirka's last email (Sep 28) asked for five things: a CPDAG comparison, BIC comparison, CPT-type differences, an unpruned MLR/OLR scoring run, and small-palim experiments. None are done yet. You have not replied in 7 weeks.
- The IJAR 2023 paper did exactly this for noisy-OR models and could not solve pruning. Its conclusion names logistic-regression CPTs as a future topic, which is your project.

Markers used below:

- **Goal**: what the group of steps is for and how you know it is done.
- **Files**: new or changed files, with the language each runs in.
- **Email**: send Jirka an update here.
- **Read**: do independent reading here, before the steps that need it.
- **Paper**: something that will become part of the paper. Log it in `docs/paper-claims.md`.
- **You**: a step you must do or understand yourself, not hand to Claude Code.

Languages: Python for data, scoring, fitting and pruning. R (bnlearn) for structure comparison and inference. Bash for pipelines. C only if Python is too slow in Phase 4. LaTeX for the paper.

The roadmap diagram at the end of this section shows the phases and the email points.

| Phase | Goal | Rough time | Ends with |
| --- | --- | --- | --- |
| 1.5 Close out Phase 1 | Answer everything Jirka asked on Sep 28 | 1–2 weeks | Email #3 |
| 2 Joint scoring, small palim | First proof that joint learning beats two-stage | 3–5 weeks | Email #4 + paper ask |
| 3 Pruning theory | Find and prove new safe pruning rules | 1–3 months | Email #5 |
| 4 Implement and scale | Use the rules to reach larger palim | 1–2 months | Email #6 |
| 5 Fallback (only if needed) | Heuristic search with a guarantee | 1 month | Email #6b |
| 6 Full evaluation | Second dataset, cross-validation, synthetic data | 1–2 months | Email #7 |
| 7 Paper | Write, revise, submit with Jirka | 2–3 months | Submission |

The times are rough guesses for school-year pace. The pruning theory in Phase 3 is the most uncertain, because it is an open research problem.

&#91;embedded content: research roadmap · 7 phases, 6 email checkpoints\]

Phase 5 is a detour, taken only if the Phase 3 rules cannot reach a useful palim.

## Phase 1.5: Close out Jirka's Sep 28 requests

**Goal:** a clean, verified version of the Phase 1 baseline plus everything Jirka asked for on Sep 28. It is done when you can state, with numbers, how the exact (GOBNILP) model and the hill-climbing (hc) model differ in structure, BIC and CPT types.

**Set up the documentation system first.** This takes an hour and pays back for the rest of the project. The full layout is in "Repo layout and documentation system" near the end.

- [ ] 1.5.0a Audit the old Markdown files before reorganizing. For each file, Claude Code checks every section against the actual code, results and emails, and writes a verdict table in `docs/tasks/1.5.0a.md` (accurate, outdated or wrong, and where it goes). You approve it before anything is deleted.
  - `project-task-list.md`: replaced by this plan. Delete.
  - `phase-1-detailed-steps.md`: a plan written before the work. Move any reasoning not recorded elsewhere into `decision-log.md`, then delete.
  - `phase-0-detailed-steps.md`: merge the parts that are still correct into `docs/setup.md`, correcting them with what actually worked (the `-f` flag, the `.bnsl` header fix, the PATH symlink, the SCIP 10.0.3 and SoPlex build), then delete.
  - `docs/bnsl_header.md`: merge into `docs/setup.md` and the GOBNILP explainer, then delete.
  - `docs/baseline_reproduction_notes.md`: keep it as the Phase 1 report in `docs/reports/`, because Jirka has seen it. Fix the known errors with dated correction notes rather than silent edits: the 10/30/4 split, the unfinished sentence, the old repo name, and the cross-validation guess Jirka has since confirmed.
  - Record each deletion in `decision-log.md`, with the last commit where the file existed.
- [ ] 1.5.0b Reorganize the repo into the layout in "Repo layout and documentation system", following the rules in `CLAUDE.md`.
  - Move Jirka's files to `data/raw/` (read-only) and derived files to `data/processed/`.
  - Put the reusable Python code into a `src/bnjoint/` package.
  - Move `scoring2a.c` and `gobnilp.set` to `tools/`.
  - Remove the nested GOBNILP source folder from the repo with `git rm --cached src/gobnilp`, keeping the build itself in `~/tools/`.
  - Move the 23-variable test outputs to `results/test-data24/`.
  - Add `requirements.txt`, a `Makefile` and `.gitattributes`.
- [ ] Create the logs (`decision-log.md`, `experiment-log.md`, `paper-claims.md`) and the folders `paper-material/`, `code-guide/`, `explainers/` and `reports/`. Backfill the logs with Phase 1 decisions, such as alpha=1, palim=9, and parsing the GOBNILP log instead of `bi.mat`.
- [ ] Re-run Phase 1 after the move with `make phase1`. It must reproduce BIC −64,837.74 and the same CPT CSV before you merge.

**Step 1.5.1: fix the tie-breaking bug (Python).**

- [ ] Change `scripts/fit_cpt_types.py` so that scores within 1e-6 of each other count as a tie. A tie goes to the simplest type, in the order STD, then OLR, then MLR. Record this as a decision.
- [ ] Also check that every MLR and OLR fit converged. statsmodels exposes `mle_retvals['converged']`. Log any that did not.
- [ ] Re-run it. Expected split: 16 STD, 24 MLR, 4 OLR.

* **You:** explain in your own words why 1-parent MLR and STD always tie. It is a nice small lemma for the paper.

**Step 1.5.2: run CPT fitting on the hc structure (Python).** This is the most important check in this phase.

- [ ] Add a command-line option to `fit_cpt_types.py` so it can read either structure: the GOBNILP log or `results/bnlearn-hc-dag.csv`. Example: `python scripts/fit_cpt_types.py --structure hc --out results/cpt-type-summary-hc.csv`.
- [ ] Compare per node against the paper's Table 2. If you get exactly 19/22/3 with the same type per node, your fitting code is verified. If not, find the cause before going further. It could be the OLR coding of parents, the fitting method, or ties.

* **Paper:** "our implementation reproduces the published model exactly" is a strong reproducibility statement.

**Step 1.5.3: compare CPDAGs (R).**

- [ ] Create `scripts/compare_structures.R`.
  - Read the GOBNILP parent sets. A small helper in Python or R turns the log into a bnlearn model string like `[a3|a4][a1|a18:a26]...`.
  - Build both networks with `model2network()`.
  - Compute `cpdag()` of each, then `shd()`, `hamming()` and `compare()` (true positives, false positives, false negatives).
  - Write `results/structure-comparison.md` and `results/cpdag-diff.csv`. The CSV lists each edge with its status: same, reversed-but-equivalent, reversed-and-compelled, or only in one model.

* **Read** before this step: the bnlearn docs for `cpdag`, `shd`, `compare` and `score`. Also read the CPDAG / essential-graph section of Koller and Friedman ch. 3.4, or any short tutorial on Markov equivalence.
* **You:** be able to explain why A3→A4 vs A4→A3 may not be a real difference.

**Step 1.5.4: compare BICs (R or Python).**

- [ ] Compute four numbers: table-only BIC and two-stage BIC, for each of GOBNILP and hc. GOBNILP's are −64,837.74 and −64,249.31. Use bnlearn `score(dag, data, type='bic')` for table-only and your CSVs for two-stage.
- [ ] Check that GOBNILP's table-only BIC is at least hc's. It must be, since GOBNILP is optimal. If not, something is wrong.

* **Paper:** exact learning improves table-only BIC by X over hc, and the two-stage result by Y.

**Step 1.5.5: list the CPT-type differences (Python).**

- [ ] Create `scripts/diff_cpt_types.py`, which joins the two summary CSVs into `results/cpt-type-diff.csv`. Columns: variable, parents\_gob, parents\_hc, type\_gob, type\_hc, same\_parents (yes/no).
- [ ] Write a few sentences: do type differences happen only where parent sets differ?

**Step 1.5.6: repo cleanup.**

- [ ] Write a real README covering the project, setup and how to run each phase.
- [ ] Rename or move the 23-variable `results/adjmat*` and `pdagadjmat*` files to `results/test-data24/`, since they are from the test dataset.
- [ ] Fix the unfinished sentence in `docs/baseline_reproduction_notes.md` and the stale repo-name note.
- [ ] Remove the leftover TODO in `fit_cpt_types.py`.

**Step 1.5.7: explainers (Claude Code writes them; you read them and bring questions to chat).**

- [ ] `docs/explainers/01-bayesian-networks.md`
- [ ] `02-bic.md`
- [ ] `03-cpt-types-std-mlr-olr.md`
- [ ] `04-gobnilp-and-exact-search.md`
- [ ] `05-cpdags.md`

**Email #3.** Send when 1.5.1–1.5.6 are done, aiming for 1–2 weeks from now. It should cover:

- the hc structure reproduces Table 2 exactly;
- the tie fix, the corrected split, and the result of 1.5.2;
- the CPDAG comparison: SHD and a short list of real differences;
- the four BIC numbers;
- the CPT-type differences table;
- your plan for Phase 2;
- a request for his Cussens notes.

Ask one question: "For joint scoring, should I start with palim 2 or 3, and is 3-state OLR with raw −1/0/1 parent coding what you used?" Do not ask about the paper yet.

## Phase 2: Joint scoring at small palim

**Goal:** the first real result of the project. Score every parent set with max(BIC\_STD, BIC\_MLR, BIC\_OLR), let GOBNILP pick the structure and the CPT types together, and show the result beats the two-stage model.

At palim=2 this is guaranteed to score at least −64,249.31. The two-stage model only uses parent sets of size 2 or less, so it is one of the options GOBNILP considers. Any improvement is a provable gain. This is IJAR's Algorithm 2 with MLR/OLR in place of noisy-OR.

**Read** before starting: IJAR 2023 Section 3 (Algorithm 2 and Lemma 3), and Kybernetika Sections 3.1–3.3 again (MLR/OLR formulas and parameter counts).

**Step 2.1: build one reusable scoring module (Python).**

- [ ] Create `src/cpt_scores.py`. Move the STD/MLR/OLR fitting out of `fit_cpt_types.py` into functions:
  - `ll_std(df, child, parents)`
  - `fit_mlr(...)`
  - `fit_olr(...)`
  - `bic_all(...)`, which returns all three scores and the winner

  `fit_cpt_types.py` then imports these, so there is one copy of the maths.
- [ ] Create `tests/test_cpt_scores.py` (pytest). It should check that:
  - MLR equals STD for 0 and 1 parents;
  - LL\_MLR ≤ LL\_STD and LL\_OLR ≤ LL\_STD always;
  - the 44 values in `results/cpt-type-summary.csv` are reproduced;
  - one family you computed by hand in a spreadsheet matches.

* **You:** hand-compute one 1-parent STD log-likelihood from counts. Do it once, and you will understand BIC for good.

**Step 2.2: make fitting fast (Python).**

- [ ] Compress the data. A child with n parents has at most 3^(n+1) distinct value combinations: 27 for 2 parents, 81 for 3. So fit on a table of counts with weights instead of 1661 rows. IJAR footnote 4 uses the same trick.
- [ ] Use weighted fitting, through scikit-learn `LogisticRegression(penalty=None)` with `sample_weight`, or a small Newton solver. Check that it matches statsmodels to about 1e-6 on 20 random families.
- [ ] Time it. Record the milliseconds per family for MLR and OLR in the experiment log. Those numbers become the cost model in the paper.

**Step 2.3: write the joint scorer (Python).**

- [ ] Create `scripts/joint_score.py --palim K`. For each variable and each parent set of size K or less, compute the three BICs and keep the max.
- [ ] Output:
  - `data/joint-palimK.scores`, in the same format `scoring2a` writes: a first line with the variable count, then per variable `index count`, then `score nparents p1 p2 ...`;
  - `results/joint-palimK-types.csv`, recording the winning type for every (variable, parent set). GOBNILP only sees the number, so you need this to recover the types.
- [ ] Run the existing `add_bnsl_header.sh` on the output.

* Sizes for 44 variables: palim 1 is 1,936 sets, palim 2 is 41,668, palim 3 is about 585,000, palim 4 is about 6 million. Start with 1 and 2.

**Step 2.4: apply the always-safe filter after scoring (Python).**

- [ ] Create `scripts/prune_dominated.py`. It drops any parent set whose score is worse than one of its subsets. This is Lemma 1 in de Campos and Lemma 3 in IJAR.
- [ ] Log the count before and after per palim. **Paper:** a table of list size before and after the filter.

**Step 2.5: run GOBNILP (Bash).**

- [ ] Create `scripts/run_joint_pipeline.sh K`. It runs scoring, the filter, the header step and GOBNILP, saving `results/joint-palimK/gobnilp.log` and the wall-clock time.
- [ ] Extend the parent-set parser so it also attaches the winning type from the types CSV. Output: `results/joint-palimK/model-summary.csv`.

**Step 2.6: sanity checks.**

- [ ] Joint palim 2 BIC ≥ −64,249.31. If it is lower, there is a bug.
- [ ] Joint palim 1 ≥ the STD-only palim 1 optimum, which you get by running `scoring2a` with palim 1.
- [ ] Re-fit every chosen family with `bic_all` and check that the scores add up to GOBNILP's objective.

**Step 2.7: analyze (R and Python).**

- [ ] Compare joint palim 2 with the two-stage GOBNILP model, reusing `compare_structures.R`. Cover BIC gain, arc count, CPDAG SHD, which families changed, and the CPT split.
- [ ] Look for the headline example: a parent set that only exists because MLR/OLR made it worth it. For instance, a variable whose joint parent set is larger or different and is scored by MLR. This is exactly the limitation the Kybernetika paper's future-work section describes.
- [ ] Write `docs/phase-2-notes.md`.

**Step 2.8: the blow-up experiment Jirka asked for (Python and Bash).**

- [ ] For palim 3 (and palim 4 if you can), score everything with no pre-pruning. Measure:
  - fitting time;
  - list size before and after the filter;
  - GOBNILP time, with a time limit such as 12–24 hours, recording the optimality gap if it stops early.
- [ ] Make one figure: parent sets and time against palim. **Paper:** this is the motivation figure for Phase 3.
- [ ] Also run the joint palim 3 result if GOBNILP finishes. Does BIC keep improving as palim grows? Jirka predicted that regression CPTs need more parents.

**Email #4** after 2.7, with 2.8 optional.

- Report the joint vs two-stage BIC gain, a structural comparison, the headline example, and the timing table.
- **Ask about the paper in this email.** Suggested wording is in "Email schedule and when to ask about the paper".

If 2.2 turns out very slow, send a short check-in mid-phase instead of going quiet.

## Phase 3: Pruning theory

**Goal:** find at least one new rule that safely skips MLR/OLR fits, or whole groups of parent sets, before they are scored. Prove it, and measure how much it prunes on the Phase 2 data.

This is the core contribution and an open problem. IJAR 2023 ends by saying efficient pruning for noisy-OR is unsolved. It also tells you which ideas failed:

- the post-scoring filter (their Lemma 3) works but needs every set scored first;
- Sharma et al.'s rules pruned almost nothing;
- a size-based conjecture had a counterexample in 27 of about 42 million sets.

This phase is mostly paper, pencil and Markdown, plus small experiments on data you already have from Phase 2.

**Read** at the start of this phase:

1. IJAR 2023, Section 5 "Parent sets pruning", line by line. Note the generalized Sharma rule and the counterexample in Tables 4–5.
2. de Campos et al. 2018 again, Lemmas 2–4 and Theorems 1–3. Re-derive each proof yourself in `docs/theory/00-de-campos-proofs.md`.
3. de Campos and Ji 2011, "Efficient structure learning of Bayesian networks using constraints" (JMLR). This is where the original bounds come from.
4. Sharma, Liao, Cussens and van Beek 2020 (PGM), the noisy-OR score-and-search paper.
5. Agresti, Categorical Data Analysis, the chapters on baseline-category (multinomial) logit and cumulative (ordinal) logit. Focus on likelihood equations and concavity.
6. For the idea in 3.4: the "safe screening" literature for sparse logistic regression. Start with El Ghaoui et al. 2012 "Safe feature elimination" and Ndiaye et al. 2017 "Gap safe screening rules". I am suggesting this as a possible direction, not a known fit, so check it with Jirka.

**Step 3.1: define exactly what "safe" means (Markdown and LaTeX).**

- [ ] Create `docs/theory/01-problem-statement.md`. Define the joint local score:

```latex
s(X \mid U) = \max\{\mathrm{BIC}_{STD}(X \mid U),\ \mathrm{BIC}_{MLR}(X \mid U),\ \mathrm{BIC}_{OLR}(X \mid U)\}
```

- [ ] Separate two kinds of pruning. Post-scoring means dropping a set after it is scored; that is solved (Lemma 1). Pre-scoring means skipping work; that is the goal. Pre-scoring itself comes in two kinds:
  - (a) skip one expensive fit;
  - (b) skip a whole set and all its supersets.
- [ ] Write down why this is non-monotone, using Jirka's {B} / {B,C} / {B,C,D} example from his Jul 8 email.

**Step 3.2: the nested-model bound (likely your first provable rule).**

The idea: MLR and OLR describe some of the possible conditional distributions over the parents U, while the full table can describe all of them. So their best log-likelihood can never beat the table's, and the table's comes cheaply from counts.

```latex
LL_{MLR}(X \mid U) \le LL_{STD}(X \mid U), \qquad LL_{OLR}(X \mid U) \le LL_{STD}(X \mid U)
```

- [ ] Prove it in `docs/theory/02-nested-bound.md`.
- [ ] Turn it into a rule. Skip the MLR fit for U if LL\_STD(U) − w·C\_MLR(U) ≤ the best joint score among the subsets of U, and the same for OLR.
- [ ] Measure it with `scripts/eval_rule_nested.py` on the palim 2 and 3 scores. How many fits are skipped, and does the filtered list give the same GOBNILP optimum? **Paper:** a fits-skipped table.

* **You:** expect this rule to work well for small U and badly for large U. A table with many parents fits the data almost perfectly (LL\_STD near 0), so the bound gets loose. Explain why in the notes; it shows where a stronger rule is needed.

**Step 3.3: show why the simple superset rules fail (a "why it's hard" result).**

- [ ] Write out the general rule from IJAR (the generalized Sharma rule) for your score. Since LL ≤ 0, any superset U' scores at most −w·C\_OLR(U'). OLR has the smallest penalty: w(k−1+|U|), about 3.7 per parent here.
- [ ] Compute what it implies on your data. Scores are around −1,400, so it only prunes parent sets with hundreds of parents, which is useless. Do the same for an analogue of de Campos's Theorem 3 (maximum number of parents).
- [ ] Write `docs/theory/03-why-simple-bounds-fail.md`. **Paper:** this is a useful negative result for the method section.

**Step 3.4: look for regression-specific superset bounds (the open part).** Candidate directions, roughly easiest first:

- **Entropy chaining.** Combine 3.2 with de Campos's Lemma 4. Adding Y raises LL\_STD by at most N·min{H(X|U), H(Y|U)}. Test how tight this is on your data; it may be too loose with 1661 rows.
- **Duality bounds.** MLR and OLR log-likelihoods are concave, like Lemma 1 for noisy-OR in IJAR, so any dual-feasible point gives an upper bound on the best log-likelihood of a bigger model. That is the idea behind the safe-screening rules above. If a cheap upper bound for "U plus any extra parents" exists, it could prune whole supersets.
- **Additivity.** MLR has no interaction terms, so its gain from adding Y may be bounded by the gain from Y on its own, given the other parents. Look for a counterexample first.
- **Data-driven conjectures.** Mine the complete palim 3 scores for patterns, as IJAR did, and try hard to break each one with `scripts/search_counterexamples.py`.

For each direction, create one file `docs/theory/04-<name>.md` with:

- the claim;
- a proof, or the counterexample that kills it;
- the measured pruning power.

**Step 3.5: package the results.**

- [ ] Write each proven rule as a numbered Lemma or Theorem with its proof, in de Campos's style.
- [ ] Make a table with one row per rule: what it skips, its cost, and the % pruned at palim 2 and 3.

* **You:** be able to present every proof to Jirka without notes. Claude can check a proof, but cannot be the reason you believe it.

**Email #5** once one rule is proven and measured, or after about 6 weeks, whichever comes first. Send `docs/theory/` and the table, and ask him to check the proofs and pick which rules to build in Phase 4. If nothing strong has turned up after about 2 months, ask whether to switch to Phase 5.

## Phase 4: Implement pruning and scale up

**Goal:** a scorer that uses the Phase 3 rules while it enumerates parent sets, so that larger palim becomes tractable with exact optimality kept. It is done when you have a table of palim against sets evaluated, fits skipped, runtime and optimal BIC.

**Step 4.1: pruned enumeration (Python).**

- [ ] Create `src/pruned_search.py`. Enumerate parent sets by size, smallest first, the way `scoring2a.c` does.
- [ ] Keep a cache of scores by subset. Apply the rules in order, cheapest first, and count how many sets or fits each rule removes.
- [ ] Output the same `.scores` and `types.csv` files as Phase 2, plus `results/joint-pruned-palimK/rule-stats.csv`.

* **Read:** the `subset_tree`, `check_subset` and `prune` logic in `src/scoring2a.c`. It is a working example of this exact loop for STD.

**Step 4.2: prove the code is safe (Python tests).**

- [ ] Create `tests/test_pruning_safety.py`. For palim 2 and 3, the pruned list must give exactly the same GOBNILP optimum as the complete list.
- [ ] Also test small synthetic datasets with 6–8 variables, where every parent set can be checked by brute force.

* This is the most important test in the project. A pruning rule that silently drops the optimum would invalidate the paper.

**Step 4.3: speed, only if needed (Python with numba, or C).**

- [ ] Profile first, using Python's `cProfile`. If fitting dominates and is too slow, options are: numba for the Newton solver, caching sufficient statistics, or multiprocessing across variables (44 variables give 44 independent jobs).
- [ ] Porting to C inside `scoring2a.c` is a last resort. Claude Code can do it, but you must keep the Python version as the reference and test that both match.

**Step 4.4: scaling runs (Bash).**

- [ ] Run palim = 2, 3, 4, 5, ... until runtime exceeds your budget, for example 24 hours. Record the numbers in `results/scaling.csv`.
- [ ] Note where the optimum stops changing. If palim 4 and 5 give the same structure, that is evidence palim 4 is enough for this data.

* **Paper:** the main results table and the scaling figure.

**Email #6:** the scaling table, the rule statistics, the best BIC, and how many more parents the regression CPTs actually use.

## Phase 5: Fallback, a heuristic with a guarantee (only if needed)

**Goal:** if Phase 3 rules are too weak to reach useful palim, still deliver a method with theory behind it, as Jirka asked on Jul 3. Do this only after discussing it in Email #5 or #6.

**Option A: certified candidate lists (Python and GOBNILP).** This is an idea to check with Jirka.

- [ ] Score only a restricted list, for example the best sets found by a cheap screen, and run GOBNILP on it. That gives a feasible model with score L.
- [ ] For every parent set that was left out, use a Phase 3 upper bound. Add one "ceiling" entry per variable and size class, then run GOBNILP again. The result U is an upper bound on the true optimum.
- [ ] Report the gap U − L as the guarantee. This is a certificate of how far you can be from optimal.

**Option B: hill climbing with the joint score (Python or R).**

- [ ] Create `src/hill_climb.py`, or use bnlearn with a custom score. Each move adds, removes or reverses an arc and re-scores only the changed families with `bic_all`.
- [ ] Use random restarts. Compare against the exact palim 2 and 3 results, where you know the optimum.

**Option C: cheap screening score (Python).**

- [ ] Use one Newton–Raphson step from a warm start, your Jul 7 idea, as a proxy. Run the exact fit only for the top candidates.
- [ ] Measure how often the proxy ranks the true winner in its top k.

**Email #6b:** which option, its guarantee, and its results against the exact small-palim optimum.

## Phase 6: Second dataset and full evaluation

**Goal:** evidence that holds beyond one dataset. Reviewers will ask three things:

- Does it generalize?
- Does a higher BIC mean better predictions?
- Does it recover the true structure when you know it?

**Step 6.1: synthetic data with a known answer (Python).**

- [ ] Create `scripts/generate_synthetic.py`. Build random networks with 10–20 three-state variables whose CPTs are a known mix of STD, MLR and OLR. Sample datasets of 100, 316, 1000 and 3162 rows, the same sizes IJAR used.
- [ ] Learn the network with the two-stage method and with the joint method. Measure SHD to the true CPDAG and the accuracy of the chosen CPT types, averaged over 5 datasets per size.

* **Read:** IJAR Section 4 (the BN2O experiments) as your template. Its figures 4–7 are exactly this design.

**Step 6.2: a second real dataset (Python and R).**

- [ ] The European conspiracy-belief data Jirka linked on Jul 3 (Harvard Dataverse, doi:10.7910/DVN/BJOCX5) is the obvious choice. Ask Jirka in Email #6 which variables and which coding to use, so it matches his own analysis.
- [ ] Create `scripts/preprocess_conspiracy.py`, then run the Phase 4 pipeline on it.

**Step 6.3: 10-fold cross-validation, as in Kybernetika Figure 4 (R and Python).**

- [ ] For each fold, learn the structure on 9 folds with the STD-only, two-stage and joint methods. Report BIC, number of parameters and log-likelihood.
- [ ] For prediction accuracy, convert MLR/OLR CPTs to full tables (the paper notes this is always possible). Then use bnlearn `custom.fit` and gRain for inference, in a new script `scripts/cv_predict.R`. Use the same evidence ratios as the paper (1/2 to 1/8).

* **Paper:** the final comparison figures.

**Step 6.4: interpret the new edges (with Jirka).**

- [ ] For each family that differs from the Kybernetika model, write one line on what it means sociologically, in the style of the paper's Tables 5–7. Jirka knows this domain well, so draft these and let him correct them.

**Email #7:** all results. Propose a paper outline and how to split the writing.

## Phase 7: Writing the paper

**Goal:** a submitted paper co-authored with Jirka. Writing actually starts earlier: draft Background and Method once Phase 2 works, and Results once Phase 4 or 6 is done.

**Step 7.1: agree on the basics with Jirka.**

- [ ] Venue: his recent papers appeared in IJAR, Kybernetika and the PGM conference. A strong Phase 3 result suits IJAR or PGM.
- [ ] Author order, and who is the corresponding author (usually Jirka).
- [ ] Who writes which section, and the timeline.
- [ ] Check the venue's deadline and template yourself on its website, closer to the time.

**Step 7.2: outline.** Each section maps to files you will already have:

| Section | Built from |
| --- | --- |
| Introduction | Project Overview, Kybernetika future work, IJAR open problem |
| Background: BNs, BIC, STD/MLR/OLR, GOBNILP, pruning | `docs/explainers/` 01–05 |
| Method: joint score, safe pruning rules, proofs | `docs/theory/`, `docs/decision-log.md` |
| Why simple bounds fail | `docs/theory/03-why-simple-bounds-fail.md` |
| Experiments: Czech data, scaling, synthetic, second dataset, CV | `results/`, `docs/experiment-log.md`, `docs/phase-N-notes.md` |
| Discussion and limitations | `docs/paper-claims.md` (open questions) |
| Reproducibility statement | README, tagged release |

**Step 7.3: tools.**

- [ ] Write in LaTeX on Overleaf, shared with Jirka, using the venue's template (Elsevier for IJAR, PMLR for PGM).
- [ ] Keep figures generated by scripts in `scripts/figures/` so they can be rebuilt.

**Step 7.4: drafting order.** Method, then Experiments, then Background, then Introduction, then Abstract. Write a paragraph from `paper-claims.md` before polishing anything.

**Step 7.5: reproducibility.**

- [ ] Tag the release with `git tag v1.0-paper`.
- [ ] Make sure one command reproduces each table.
- [ ] Optionally archive the repo on Zenodo to get a DOI.

**Step 7.6: revision loop.** Send drafts to Jirka section by section. After submission, expect reviewer comments and a revision round.

## Email schedule and when to ask about the paper

Ask about co-authoring in Email #4, the one reporting that joint learning beats two-stage. Start writing once Phase 4 (or 5) gives a scaling result.

It is about one email per phase. Never go more than about 4 weeks without a short update, even if it just says what you are stuck on.

| # | When | Contents | Ask |
| --- | --- | --- | --- |
| 3 | End of Phase 1.5 (1–2 weeks) | hc reproduces Table 2; tie fix and new split; CPDAG/SHD; 4 BICs; CPT-type diffs | palim to start with; Cussens notes |
| 4 | End of Phase 2 | Joint vs two-stage BIC gain; headline family; timing and blow-up table | **Paper ask** |
| 5 | Phase 3: first proven rule, or about 6 weeks | `docs/theory/` notes, rules table, proofs to check | Which rules to build; switch to Phase 5? |
| 6 / 6b | End of Phase 4 or 5 | Scaling table, rule statistics, best BIC (or fallback with guarantee) | Second dataset choice and coding; venue |
| 7 | End of Phase 6 | Synthetic, second dataset, CV results | Outline and writing split |
| 8+ | Phase 7 | Draft sections | Feedback |

**Why Email #4 for the paper ask.** By then you will have something no one has shown: a provably better model on his data, from his own future-work idea. He has already called your exact GOBNILP experiments "novel and valuable" (Sep 28). Asking earlier means asking on a promise. Asking later wastes his chance to shape the work toward a venue he likes.

Suggested wording: "These first results seem promising. Would you be open to writing a paper together once the pruning part is done? I would be very glad to work toward that with you, and I would love your advice on what it would need and where it might fit."

**When you have enough to start writing:**

- **Minimum:** a short conference paper. This needs Phase 2 plus at least one proven Phase 3 rule with measured pruning, all on the Czech data.
- **Stronger:** a journal paper. This adds Phase 4 scaling, the synthetic experiments, the second dataset and cross-validation.
- Drafting Background and Method can start right after Email #4, whichever version you end up writing.

**Every email should:**

- open with one line of status;
- show numbers in a short list;
- link the exact files in the repo;
- ask at most 2 questions;
- end with your next step.

Draft it with Claude, then rewrite it in your own words before sending.

## Reading list and when to read

Read each item just before the step that needs it, not all at the start. For each paper, write a one-page note in `docs/reading-notes/` covering: what problem it solves, the key result in your own words, and what you will reuse.

| When | Read | Why |
| --- | --- | --- |
| Now (1.5.3) | bnlearn docs: `cpdag`, `shd`, `compare`, `score`; Koller and Friedman ch. 3.4 on Markov equivalence | CPDAG comparison |
| Now | IJAR 2023 in full (you have it) | Closest precedent; its open problem is yours |
| Phase 2 start | Kybernetika Sec. 3; IJAR Sec. 3 (Algorithm 2) | Joint scorer design |
| Phase 2 start | Cussens 2011, "Bayesian network learning with cutting planes" (UAI); GOBNILP manual | What GOBNILP does with your scores |
| Phase 3 start | de Campos et al. 2018 (re-derive the proofs); de Campos and Ji 2011 (JMLR) | The pruning bounds you extend |
| Phase 3 start | Sharma, Liao, Cussens and van Beek 2020 (PGM) | Noisy-OR pruning attempts |
| Phase 3 | Agresti, Categorical Data Analysis: multinomial and cumulative logit chapters | MLR/OLR likelihood maths |
| Phase 3 (3.4) | El Ghaoui et al. 2012; Ndiaye et al. 2017 (gap safe screening) | Possible duality-based bounds |
| Phase 5, if used | Chickering 2002 (greedy equivalence search); bnlearn hc docs | Heuristic search with theory |
| Phase 6 | Kybernetika Sec. 4–5; IJAR Sec. 4; Vomlel et al. PGM 2024 (conspiracy theories) | Evaluation design; second dataset |
| Phase 7 | 2–3 recent papers from the target venue | House style and expected length |

Background to fill gaps whenever you need it: Koller and Friedman, Probabilistic Graphical Models, ch. 3 (representation) and ch. 18 (structure learning).

## Repo layout and documentation system

Every decision, run and result should be findable in the repo. If it is not written down, it cannot go in the paper. Set this up in Step 1.5.0.

```
bn-joint-structure-cpt-learning/
  README.md  CLAUDE.md  requirements.txt  Makefile  .gitignore  .gitattributes
  data/raw/              Jirka's original files (read-only)
  data/processed/        files derived by scripts (.dat, .scores, .bnsl)
  src/bnjoint/           Python package: io, cpt_scores, structures, gobnilp_io, ...
  scripts/               thin command-line entry points, one job each
  R/                     R scripts: compare_structures.R, cv_predict.R, ...
  tools/                 scoring2a.c + build notes, gobnilp.set
  tests/                 pytest tests mirroring src/bnjoint
  results/<experiment>/  outputs + README saying which command and commit made them
  docs/
    research-plan.md     this plan, exported as Markdown
    setup.md             how to build SCIP, GOBNILP, scoring2a; package versions
    decision-log.md  experiment-log.md  paper-claims.md
    paper-material/      methods-notes.md, results-notes.md (paper-style paragraphs)
    code-guide/          one walkthrough per module or script: what, how, why
    explainers/          beginner concept guides + README index
    reports/             one report per step
    tasks/               one plan per step, approved before coding
    theory/  reading-notes/  archive/
```

The four logs, and what one entry looks like:

| File | One entry contains | Example |
| --- | --- | --- |
| `decision-log.md` | Date, decision, why, alternatives considered, who decided | 2026-11-20 · Ties go to STD within 1e-6 · matches paper; avoids noise · prefer MLR · me |
| `experiment-log.md` | Date, commit hash, exact command, inputs, output folder, headline number, notes | 2026-12-02 · a1b2c3d · `run_joint_pipeline.sh 2` · BIC = ... |
| `paper-claims.md` | Claim, evidence file, status (draft, checked, Jirka-agreed) | Joint palim 2 beats two-stage by X · `results/joint-palim2/` · checked |
| `phase-N-notes.md` | What you tried, what happened, what surprised you, open questions | Written at the end of each phase |

Explainers: write one per concept, in plain language for a beginner. Each covers what it is, why it matters here, a tiny worked example, and how it appears in the code. Planned set:

1. Bayesian networks
2. BIC
3. CPT types (STD, MLR, OLR)
4. GOBNILP and exact search
5. CPDAGs
6. Pruning: post-scoring vs pre-scoring
7. Why the joint score is non-monotone
8. Your pruning rules
9. Running the whole pipeline

They are for future you and for any beginner, and they double as the Background section of the paper.

Git habits:

- one branch per task;
- small commits with clear messages;
- tag the commit behind every number you email Jirka (for example `email-3`), so any number can be traced back to exact code.

## Workflow: Claude chat, Claude Code, GitHub and Jirka

Yes, Claude Code can do most of the implementation. It can read your repo, write Python, R and Bash, run scripts and tests in your WSL terminal where GOBNILP is installed, and commit to git.

What it cannot do is be responsible for the research. You decide what to build. You check that the numbers make sense. You understand and stand behind every proof and every number you send Jirka.

Split of roles:

| Tool | Use it for | Do not use it for |
| --- | --- | --- |
| Claude chat (this Project) | Understanding concepts, planning the next step, checking proofs, interpreting results, drafting emails and explainers | Running code or editing the repo |
| Claude Code (on your laptop, in the repo) | Writing and running code, tests, refactors, profiling, keeping logs updated | Deciding research direction; inventing theory you have not checked |
| GitHub | The single source of truth: code, results, logs, docs; Jirka sees it | Large raw outputs (keep them out with `.gitignore`) |
| Jirka | Direction, checking theory, domain meaning, paper decisions | Debugging help unless you are truly stuck |
| You | Every decision, every hand-check, the final words of every email and explainer |  |

**The loop for every step in this plan:**

1. **Start (Claude Code).** Open a session for the next group of steps, usually everything up to the next email, using the prompt in "Handing the plan to Claude Code".
2. **Plan (Claude Code, approved by you).** It writes `docs/tasks/<step>.md`: goal, inputs, outputs, files, and how it will check the work. You read the plan and approve it before any code is written.
3. **Build (Claude Code).** One step at a time, on a branch, tests first. It stops after each step for you to review.
4. **Review (you, 10–20 minutes per step).** Run the tests yourself and hand-check one number. Skim the diff and ask "why" about anything surprising.
5. **Record and explain (Claude Code).** It updates the four logs, writes or updates the beginner explainer for anything new, and writes a short step report in `docs/reports/`. Then it commits, pushes and merges.
6. **Understand (you, with chat).** Read the explainer and the step report. Bring every question to this chat. The repo syncs to this Project, so chat can read the same files.
7. **Report (chat).** At an email point, bring the reports here to sanity-check the results and draft the email. Rewrite it in your voice, then send.

**Rules to put in `CLAUDE.md`,** which Claude Code reads automatically:

- Never modify files in `data/`.
- Work only on the steps you were asked to do, from `docs/research-plan.md`. Stop after each step for review.
- Every new script gets a docstring explaining its inputs, outputs and the maths it implements, with paper equation numbers.
- Every change that produces a number adds an `experiment-log.md` entry with the commit hash and command.
- Write or update tests for any scoring or pruning code. Never weaken a test to make it pass.
- After each step, write or update the matching beginner explainer in `docs/explainers/` and a step report in `docs/reports/`.
- Ask before installing packages, deleting files, or changing the research plan.
- Do not claim a pruning rule is safe without a test against the unpruned optimum.

**Learning your way up with limited coding skills:**

- Aim to read every line of Python, not to write it all.
- Ask Claude Code to add comments to anything dense.
- After each phase, re-implement one small function yourself without help, such as `ll_std`. This is the fastest way to really own the code.

## Handing the plan to Claude Code

Yes, give Claude Code this plan directly, but as a file inside the repo, one phase-chunk at a time. Claude Code runs on your laptop and cannot open this doc. It also should not run the whole plan in one go: each step's results can change the next step, and Jirka's replies will change it too.

**One-time setup:**

1. Export this doc as Markdown (download menu) and save it as `docs/research-plan.md` in the repo.
2. Save the provided `CLAUDE.md` in the repo root. Claude Code reads it automatically at the start of every session.
3. Commit both. Whenever this plan changes after a Jirka email, re-export it and commit again, so the repo copy stays current.

**Session prompt** (change the step range each time):

```
Read CLAUDE.md and docs/research-plan.md. Today we are doing steps 1.5.0 to 1.5.2.
Start in plan mode: write docs/tasks/ files for these steps and stop for my approval.
Then do one step at a time and stop after each one so I can review.
```

**Chunks, one session each:**

| Session | Steps | Ends with |
| --- | --- | --- |
| A | 1.5.0–1.5.2 (setup, tie fix, hc check) | Report: does hc give 19/22/3? |
| B | 1.5.3–1.5.7 (CPDAG, BICs, diffs, cleanup, explainers 01–05) | Email #3 draft in chat |
| C | 2.1–2.3 (scoring module, fast fitting, joint scorer) | Timing numbers |
| D | 2.4–2.8 (filter, GOBNILP runs, checks, analysis, blow-up) | Email #4 draft + paper ask |
| Later | Phase 3 onward, planned again here in chat after Email #4 |  |

**Two things only you can do,** whatever Claude Code builds:

- Run the tests and hand-check one number per step.
- Bring anything you do not understand to chat before it goes into an email to Jirka.

Phase 3 is mostly maths. Do it mainly here in chat, with Claude Code only running the small experiments.
