# Code guide: what `scoring2a.c` does

**What it does.** `tools/scoring2a/scoring2a.c` reads a data file and, for every variable
(the "child"), computes the score of candidate parent sets and writes those worth keeping to
a `.scores` file. GOBNILP then only chooses among these. The file is based on GOBNILP's own
scoring code (James Cussens, 2012) and carries a note (line 28) that Cassio de Campos modified
it on 22 Sept 2014, which is before the entropy-based pruning paper appeared (arXiv 1707.06194,
2017). We do not modify it; this guide is from reading the source line by line (line numbers
are for the file as committed). Running it: `docs/setup.md` §6.

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

## Which pruning rules are implemented (checked 2026-11-15)

Two papers matter. **de Campos & Ji 2011** ("Efficient structure learning of Bayesian networks
using constraints", JMLR 12:663–689) gives the classic BIC bound (their Theorem 4). **de Campos
et al. 2018** ("Entropy-based pruning for learning Bayesian networks using BIC", Artificial
Intelligence; arXiv 1707.06194) restates that bound as its Lemma 3 and as Theorem 1 with the
H(X|Π*) term (the same rule, because N·H(X|Π) = −LL(X|Π); "Alg1" in its tables), and adds new
rules that use the *candidate parent's* entropy. The theorem and algorithm numbers here come from
Anika's reading of the 2018 paper (2026-11-15); this guide checks only which rules the code
contains.

| Rule | Paper | In `scoring2a.c`? | Where |
|---|---|---|---|
| **Subset filter**: drop S if a subset T ⊂ S scores at least as well | 2018, Lemma 1 | **Yes** | lines 897–916, output only if `keep` (929) |
| **de Campos & Ji bound**: if BIC(T) > −Pen(S) for some T ⊂ S, prune S *and all its supersets* | de Campos & Ji 2011, Thm 4 = 2018 Lemma 3 = 2018 Thm 1 with H(X\|Π*) ("Alg1") | **Yes** (BIC version) | penalty 886–893; test 920–921; effect 948–971 and 837–862 |
| **Alg2**: Theorem 1 with the candidate parent's conditional entropy H(Y\|Π*) | 2018, Thm 1 | **No** | no entropy is computed anywhere in the file |
| **Alg4**: bound using H(Y), Theorem 2 with Π′ = ∅ | 2018, Thm 2 | **No** | same |
| **Alg3** | 2018 | **Not identified**: Anika's summary doesn't describe it. The file contains only the two rules marked "Yes", so Alg3 is implemented only if it is one of those; check in the paper's tables. | — |
| **Theorem 3**: bound on the maximum number of parents | 2018, Thm 3 | **No** | the only limit is the user's palim: `npa <= min(palim, nvars-1)` (785) |

### The subset filter, in detail (lines 886–929)

After scoring a new set S (score `skore`), the code walks the list `kept` of already-kept sets
of this child, which is sorted best score first (`sps_sort`, 506–517; merged after each layer,
988 onward). It stops at the first kept set that scores *worse* than S (`if ( skore >
sps_ptr->score ) break;`, 901). Every set before that point scores at least as well as S; if
one of them, T, is a subset of S (905–915), S gets `keep = FALSE` (916) and is not written to
the output. GOBNILP would always prefer T, which has fewer parents and an equal or better
score, so S can't be in an optimal network. An exact tie is dropped, because only a strictly
higher S score stops the walk.

### The de Campos & Ji bound, in detail (line 920)

`penalty` (886–893) is (r_child − 1) × the product of the parents' arities, the STD parameter
count of S. When the subset filter fires with subset T, line 920 also tests

    BIC(T) > −alpha · (log N / 2) · penalty(S)          (DO_BIC case; alpha = 1 for us)

If it holds, S is marked `prune = TRUE`: its contingency table is freed (948) and S is **not**
added to the subset store (`add_subset`, 970–971). A set of the next layer is only scored if
*all* its subsets one size smaller are in the store (`check_subset`, 837–862), so every
superset of S is skipped without being scored.

Why it is safe: any superset S′ ⊇ S has at least S's penalty, and its log-likelihood is at most
0, so BIC(S′) ≤ −(log N / 2) · penalty(S) < BIC(T), and T ⊂ S′. Details of the code compared
with the paper's statement:
- the code uses strict `>`, the paper's statement allows equality, so the code prunes slightly
  less (never more) than the theorem permits;
- it tests only the first dominating subset it meets, which is the best-scoring one (the list
  is sorted), so it is the strongest test available;
- it is skipped on the last layer (`!last_layer`, size = palim), where no supersets would be
  generated anyway;
- lines 918 and 922 are the analogous tests for BDeu and AIC, unused by us.

This bound uses two facts about STD: the penalty grows with every added parent, and LL ≤ 0. The
joint score max(BIC_STD, BIC_MLR, BIC_OLR) has much smaller MLR/OLR penalties, so the same bound
is far weaker for it, which is the open problem of IJAR 2023 Sec. 5.

### Open question (for Email #3)

Jirka's Jul 3 email says the scoring script is "based on the pruning approach in de Campos et
al., 'Entropy-based Pruning for Learning Bayesian Networks using BIC'". The copy in his Jul 8
zip (dated 22 Sept 2014 in its header) implements only the subset filter and the de Campos & Ji
bound, which the 2018 paper restates as Lemma 3 / Alg1; none of its new entropy-based rules
(Alg2, Alg4) or Theorem 3 are in it. Is there a newer version of the script with those rules,
or did "based on" mean that the paper describes the rule this script uses?

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
