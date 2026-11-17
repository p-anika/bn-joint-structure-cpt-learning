# Phase 1 report: the two-stage baseline

Phase 1 ran Aug–Sep 2026 and was reported to Jirka on Sep 7, 2026. Status: **complete**.
Decisions behind it: `docs/decision-log.md` entries 2–10 and 19–20. Runs:
`docs/experiment-log.md`. How to run it: [`docs/code-guide/phase1-pipeline.md`](../code-guide/phase1-pipeline.md).

## Goal

Reproduce the two-stage method of [Vomlel, Kybernetika 2026](../references.md#vomlel2026) on its
data, with one change: learn the structure by **exact** search instead of hill-climbing.

1. Learn one network structure, assuming every node uses a standard table (STD).
2. Keep that structure fixed. For each node, compare the BIC of STD, multinomial logistic
   regression (MLR) and ordinal logistic regression (OLR), and keep the best.

BIC = log-likelihood − (log N / 2) × (number of free parameters), natural log, higher is
better (paper eq. 7/9). This is the opposite sign of the textbook "−2·LL + k·log N"; both give
the same ranking. The three CPT types: [explainer 03](../explainers/03-cpt-types.md).

## Method

- **Data:** `data/raw/BN-data.csv`, 1661 rows × 44 variables (a1–a30, d1–d14), values −1/0/1,
  as sent by Jirka on Aug 5, 2026 (decision 2; provenance in `data/raw/README.md`).
- **Local scores:** de Campos's `scoring2a` with alpha = 1 (the true BIC penalty), at most 9
  parents, built-in pruning, score `bic` (decision 5, approved by Jirka on Sep 28). What it
  computes and prunes: [`docs/code-guide/scoring2a.md`](../code-guide/scoring2a.md).
- **Exact structure search:** GOBNILP on SCIP 10.0.3 + SoPlex 8.0.3 (decision 3; versions in
  [`docs/setup.md`](../setup.md#versions-in-use)). Parent sets are read from its console log
  (decision 6).
- **CPT types:** `bnjoint.cpt_scores` ([code guide](../code-guide/cpt-scoring.md)): STD from
  counts, MLR with statsmodels `MNLogit` (parents dummy-coded, −1 as reference), OLR with
  `OrderedModel` (logit, BFGS, parents as raw −1/0/1 values), no OLR for a node without parents
  (decisions 7–9). Winner: highest BIC, where scores within 1e-6 count as tied and a tie goes to
  STD, then OLR, then MLR (decision 55).
- **Comparison structure:** bnlearn `hc(score = "bic")` with default settings after
  `set.seed(1)` (`R/bnlearn_hc.R`, decision 10). This is the method the paper used (decision 19).

## Results

### Exact structure (GOBNILP)

File: `results/phase1/gobnilp-std-run.log` (DAG and CPDAG: `results/phase1/adjmat.*`,
`pdagadjmat.*`).

- **Optimal solution, gap 0.00 %:** this is the proven BIC-best structure for STD tables, not
  an approximation.
- **Objective (total BIC of the 44 families): −64837.738627.**
- **69 arcs**, at most 2 parents per node (26 nodes with 2 parents, 17 with 1). Exactly one
  node has no parents: **d11**.
- Deterministic: scoring2a and GOBNILP need no seed. A rebuild from the raw data reproduces
  every file byte for byte ([1.5.0b](1.5.0b.md#results), [1.5.1–1.5.2](1.5.1-1.5.2.md#phase-1-rebuild)).

### CPT types on the exact structure

File: `results/phase1.5/1.5.1-gobnilp-tie-fix/cpt-type-summary.csv` (made in step 1.5.1 with the
tie rule; [report](1.5.1-1.5.2.md#151-gobnilp-structure)).

| | STD | MLR | OLR |
|---|---|---|---|
| Our exact structure | **16** (36 %) | **24** (55 %) | **4** (9 %) |
| Paper, Table 2 (hc structure) | 19 (43 %) | 22 (50 %) | 3 (7 %) |

- STD wins only on the root d11 and on 15 of the 17 one-parent nodes. The other two one-parent
  nodes, d7 and d10, choose OLR.
- Every 2-parent node chooses MLR (24) or OLR (2: a20, d8), never STD, as in the paper. This is a
  property of the data, not a rule. STD always fits at least as well, but with 2 parents it pays
  for 18 parameters against MLR's 10. It wins only if the parents interact strongly, and here
  they don't ([explainer 03](../explainers/03-cpt-types.md#5-common-confusions)).
- With 0 or 1 parents, STD and MLR are the same model and their BICs differ only by rounding
  (≤ 4.5e-13). That is why the tie rule is needed
  ([explainer 04](../explainers/04-one-parent-mlr-equals-std.md)).
- The two-stage total, the sum of the best BIC per node, is −64249.31.

### Hill-climbing structure (bnlearn)

File: `results/phase1/bnlearn-hc-dag.csv` (adjacency matrix, row = parent, column = child).

- 44 nodes, **66 directed arcs**, 0 undirected, average branching factor 1.50 (at most 2
  parents: 23 nodes with 2, 20 with 1). Exactly one node has no parents: **a3**.
- Repeatable: two runs gave the same 66-arc model and the same penalization coefficient.
- **Same BIC everywhere:** bnlearn printed a penalization coefficient of 3.707588 = log(1661)/2.
  So bnlearn, scoring2a and our Python code all use log(N)/2 per parameter (paper eq. 7/9),
  although they were implemented independently.
- It differs from the exact structure: 66 vs 69 arcs, and some arcs point the other way. For
  example, GOBNILP has a4 → a3, while hc has a3 → a4. Hill-climbing is greedy and can stop at a
  local optimum; GOBNILP's result is proven optimal. The CPDAG comparison of the two is step 1.5.3.
- Its parent sets are **exactly those of the paper's Table 2**, and our CPT-type fitting on it
  gives the paper's types on all 44 nodes, 19/22/3 (step 1.5.2,
  [report](1.5.1-1.5.2.md#152-hc-structure-vs-table-2)). So the split difference in the table
  above comes entirely from the different structure.

bnlearn's console output:

```
  Bayesian network learned via Score-based methods
  model:
   [a3][a4|a3][a1|a4][a9|a4][a27|a1][a28|a4:a27][d7|a27][a18|a27:a28][d8|a28]
   [d12|d7][a2|a4:a18][a30|a18:a28][d10|d8][d11|a18:a27][d13|d12][a17|a18:d10]
   [a19|a1:d11][d2|d7:d13][d5|d11][a7|a19][a12|a1:a19][a15|a19:d11][a20|a17:a28]
   [a21|a17:a18][d3|a19:d5][d14|d5][a5|a19:d3][a8|a1:a7][a11|a7:a15]
   [a16|a18:a21][a26|a15:a27][a29|a15][d1|d3:d13][d9|d3][a6|a8:a20][a23|a16:a18]
   [a24|a5][a25|a26][d4|a16:d3][d6|d1][a10|a9:a24][a13|a6][a14|a25][a22|a14]
  nodes:                                 44
  arcs:                                  66
    undirected arcs:                     0
    directed arcs:                       66
  average markov blanket size:           3.64
  average neighbourhood size:            3.00
  average branching factor:              1.50
  learning algorithm:                    Hill-Climbing
  score:                                 BIC (disc.)
  penalization coefficient:              3.707588
  tests used in the learning procedure:  3870
  optimized:                             TRUE
```

### Comparison with the paper

- **Total BIC.** The paper's Figure 4 shows values of about −58,500 to −59,000, against our
  −64837.74. Jirka confirmed on Sep 28 that Figure 4 comes from 10-fold cross-validation
  (decision 20), where each fit uses about 90 % of the rows. So the numbers are not directly
  comparable (−58,500 / −64,838 ≈ 0.9 is only a rough consistency check).
- **CPT-type split.** Explained by the structure; see above.
- **The paper's text vs. its Table 2.** Section 4.3 says "all 17 standard CPTs correspond either
  to variables with no parents (A3) or to those with just one parent", but Table 2 lists 19 STD
  nodes, and our step 1.5.2 fit gives 19. The "17" is an inconsistency in the paper (checked by
  Anika in the PDF).
- **Structure shape.** Both structures have at most 2 parents per node and exactly one root,
  though a different one (d11 for GOBNILP, a3 for hc).

## What we tried that didn't work

- **Feeding scoring2a's output straight to GOBNILP.** Our GOBNILP build (current version,
  commit `5441edf`) rejected the `.scores` file. Its reader needs two extra lines first: the
  variable names and `SCORES START`. We found this in GOBNILP's example
  `scores/chest_100_1_3.bnsl`, which Jirka pointed to on Aug 12, and in its reader's source.
  The fix is `scripts/add_bnsl_header.sh`, which writes the `.bnsl` file (decision 4;
  [`setup.md` §8](../setup.md#8-the-bnsl-header-gobnilp-needs)).
- **Running GOBNILP the old way.** `gobnilp file.bnsl`, as in Jirka's `script-data24-1` for his
  GOBNILP 1.6.3, does not work on this version: the input needs `-f`. Jirka's `gobnilp.set` asks
  for an adjacency-matrix file, `bi.mat`, through a parameter this version doesn't know. So
  `bi.mat` is never written, and we read the parent sets from the console log instead
  (decision 6; [`setup.md` §7d](../setup.md#7-scip-and-gobnilp-exact-structure-search)). We did
  not rebuild Jirka's GOBNILP 1.6.3 / SCIP 3.2.1, which is from 2016 and hard to build (decision 3).
- **Choosing the CPT type with a plain "highest BIC wins" (the tie bug).** For 0-/1-parent nodes,
  STD and MLR are the same model, so their BICs differ only by about 1e-13 of rounding. The first
  version of `fit_cpt_types.py` let that noise decide: six nodes (a13, a15, d6, d11, d12, d13) got
  MLR. That gave the 10/30/4 split reported in September. It was found in the step 1.5.0a audit
  and fixed in step 1.5.1 with the 1e-6 tie rule (decision 55). The September write-up also
  explained the STD–MLR ties correctly for 0–1 parents, but wrongly concluded that STD can
  "only ever tie MLR, never beat it". That is false for 2+ parents, where STD can win when the
  parents interact.
- **Explaining the gap to the paper by exact vs. greedy search alone.** In September we put the
  whole difference from the paper's split down to GOBNILP's structure differing from the
  paper's. Part of it was the tie bug (above). The rest is indeed the structure: the paper's
  structure came from bnlearn hc (Jirka, Sep 28; decision 19), and fitting our code on the hc
  structure reproduces Table 2 exactly (step 1.5.2). Until Jirka's answer, we also didn't know
  which scoring2a settings "the paper used". In fact the paper used none, because its structure
  came from hc (decision 5).

## History

- 2026-11-16: the CPT-type split reported on Sep 7 was **10 STD / 30 MLR / 4 OLR** (23 / 68 / 9 %),
  with all 10 STD winners having one parent. That was the tie bug; with the tie rule it is
  16 / 24 / 4, and the BIC values are unchanged (decisions 55, 63). To read the old report and
  CSV: `git show 9d80757:docs/reports/phase-1.md` and
  `git show 9d80757:results/phase1/cpt-type-summary.csv`.

## Open questions

None specific to Phase 1. The open questions that affect it, how OLR codes its parents (for
Jirka) and the absolute 1e-6 tie tolerance (to watch in Phase 2), are listed once, in
[the 1.5.1–1.5.2 report](1.5.1-1.5.2.md#open-questions).
