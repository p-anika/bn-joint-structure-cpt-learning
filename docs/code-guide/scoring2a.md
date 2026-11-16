# Code guide: what `scoring2a.c` does

**What it does.** `tools/scoring2a/scoring2a.c` reads a data file and, for every variable
(the "child"), computes the score of candidate parent sets and writes those worth keeping to
a `.scores` file. GOBNILP then only chooses among these. The file is based on GOBNILP's own
scoring code (James Cussens, 2012) and carries a note that Cassio de Campos modified it in
2014. We do not modify it; this guide is from reading the source (line numbers are for the file
as committed). Running it: `docs/setup.md` §6.

## Inputs and outputs

- **Command line** (`main`, lines ~586–612): `scoring2a datafile alpha parentslimit
  [noprune|prune] [epsilon] [bdeu|min|bic|aic]`. We use `… 1 9 prune 0 bic`. Pruning is on
  unless the 4th argument is `noprune`. With `bic`, alpha multiplies the penalty, so alpha = 1
  is the standard BIC.
- **Input**: the `.dat` format (number of variables, arities, number of rows, then rows).
- **Output** (stdout): number of variables; then for each child a line `child count` followed
  by `count` lines `score nparents parent1 parent2 …` (see `docs/setup.md` §8). Messages
  starting `[info]` go to stderr.

## How the BIC is computed (`newcalc`, lines ~203–264)

For one child and one parent configuration with child counts N_1..N_k it adds
Σ N_i log(N_i / N) and subtracts alpha · (log n_rows / 2) · (k − 1). Summed over the
configurations this is LL − (log N / 2) · C with C = (k − 1) × (number of configurations),
the same STD BIC as `bnjoint.cpt_scores.bic_std`. That is why the STD scores in
`cpt-type-summary.csv` match GOBNILP's `obj` values. Contingency tables (`CONTAB`) are built
incrementally: adding a parent splits each existing cell (`extend_contab`), and on the last
layer the score is computed without storing the table (`extend_score`).

## The search over parent sets (main loop, lines ~750–1010)

Parent sets are generated **layer by layer**: first the empty set, then all sets of size 1,
then size 2, …, up to palim (9). A set of size n is made by extending a kept set of size n−1
with a parent of higher index, so each set is generated once.

## The two kinds of pruning (the `if ( pruning )` blocks)

1. **Not kept, but its supersets still explored** (lines ~886–935). After scoring a set S,
   the code looks through the already-kept sets that score at least as well. If one of them,
   T, is a **subset** of S, then S is dropped from the output (`keep = FALSE`): GOBNILP would
   always prefer T, which has fewer parents and an equal or better score, so S can never be in
   an optimal network.
2. **"Exponential" pruning: S and all its supersets** (same block, the `DO_BIC` line ~920).
   If additionally T's score is greater than −alpha · (log N / 2) · penalty(S), where
   penalty(S) = (k_child − 1) · Π(arities of S) is S's number of STD parameters, then S is
   marked `prune = TRUE`: its table is freed and it is **not** added to the subset store
   (`add_subset`). In the next layer a new set is only scored if *all* its subsets one size
   smaller are in the store (`check_subset`, lines ~837–862), so every superset of S is skipped
   without being scored.

The reason (2) is safe, in outline: a superset S′ ⊇ S has at least S's penalty, and its
log-likelihood is at most 0, so its BIC is at most −(log N / 2) · penalty(S). If T already
scores higher than that, no superset of S can beat T. This is the BIC bound of de Campos et al.;
the exact statement and theorem number should be taken from the paper (Artificial
Intelligence 2018), not from this summary. On the last layer (size = palim) no superset will
be generated anyway, so only rule (1) applies.

This is exactly the kind of rule the project needs for MLR/OLR: the STD argument uses the
fact that the penalty grows with every added parent and LL ≤ 0. The joint score
max(BIC_STD, BIC_MLR, BIC_OLR) has much smaller MLR/OLR penalties, so the same bound is far
weaker, which is the open problem of IJAR 2023 Sec. 5.

## Helper functions

- `check_subset` / `add_subset` / `delete_tree` (lines ~85–200): a tree of subsets
  (`SUBSET_TREE`) storing which sets of the previous layer survived, for fast lookup.
- `sps_sort` (line ~506): sorts scored parent sets best first, so the "kept" list is ordered
  and the dominance check can stop early.
- `skip_comment` (line ~520): skips comment lines in the input file.

## How to change it safely

We don't. If later phases need a variant (e.g. joint scoring in C), copy it to a new file
under `tools/`, keep the original byte-identical (its checksum is in `tools/scoring2a/README.md`),
and record the decision (CLAUDE.md: C only if Anika approves).
