# 04 — Why one-parent MLR and STD are the same model (and why we need a tie rule)

Prerequisite: [03 — the three CPT types](03-cpt-types.md).

## 1. Plain-words definition

For a node with **0 or 1 parent**, multinomial logistic regression (MLR) and the standard table
(STD) can describe exactly the same set of conditional distributions, with the same number of
free parameters. They are one model written two ways. Their maximized log-likelihoods are
therefore equal, their BIC penalties are equal, and so their BICs are equal. A computer gets
them to agree only up to rounding (about 1e-13 here), because it computes them along different
routes (counting vs. an iterative optimizer).

**The lemma (small result), stated carefully.** Let the child have k states and one parent with
k states, and suppose every (parent state, child state) combination occurs at least once in
the data. Then max LL_MLR = max LL_STD, and both have k(k−1) free parameters, so BIC_MLR =
BIC_STD. With 0 parents, both are the child's marginal distribution with k−1 parameters.

**Why (the argument in four lines).** Write the child's states as −1 (reference), 0, +1, and
the parent's value as x.

1. STD: for each x there is a free distribution (p₋₁(x), p₀(x), p₊₁(x)): 3 × 2 = 6 numbers.
2. MLR: for child state j ∈ {0, +1}, log( pⱼ(x) / p₋₁(x) ) = bⱼ + cⱼ₀·[x = 0] + cⱼ₁·[x = +1],
   where [x = 0] is 1 if x is 0 and 0 otherwise (the dummy columns). That is 2 × 3 = 6 numbers.
3. Take any STD table with all probabilities above 0. Choose bⱼ = log( pⱼ(−1) / p₋₁(−1) ),
   cⱼ₀ = log( pⱼ(0) / p₋₁(0) ) − bⱼ and cⱼ₁ = log( pⱼ(+1) / p₋₁(+1) ) − bⱼ. Then MLR reproduces
   that table exactly. And every MLR gives some table. So the two describe the same
   distributions, and their best fits to the data are the same.
4. The parameter counts agree: (k−1)·k¹ = 6 and (k−1)·(1 + 1·(k−1)) = 6. Same LL, same
   penalty, same BIC.

With **2 parents** this breaks: STD has (k−1)·k² = 18 parameters, MLR only 10, because MLR's
log-odds are a *sum* of one term per parent and cannot express an interaction between the two
parents. Then MLR is a genuinely smaller model.

## 2. Why it matters in this project

- **The tie bug (fixed in step 1.5.1).** In Phase 1 the winner was simply the highest BIC. For
  six 0-/1-parent nodes, MLR's number happened to be 1e-13 higher, so MLR "won" a tie that is
  really no difference at all. The reported split 10 STD / 30 MLR / 4 OLR became 16 / 24 / 4
  once scores within 1e-6 were treated as equal and ties given to the simplest type (STD, then
  OLR, then MLR). Results: [`docs/reports/1.5.1-1.5.2.md`](../reports/1.5.1-1.5.2.md).
- **Joint scoring (Phase 2).** For every candidate parent set of size 0 or 1, computing MLR is
  wasted work: its score is known to equal STD's. That is a first, trivially safe saving.
- **The paper.** It is a small lemma worth stating: it explains why the published model has
  STD (never MLR) on every 1-parent node.

## 3. Worked example from our data: a3 given a4

Counts from `data/raw/BN-data.csv` (rows = a4, columns = a3):

| a4 \ a3 | −1 | 0 | +1 | total |
|---|---|---|---|---|
| −1 | 1118 | 137 | 114 | 1369 |
| 0 | 58 | 61 | 30 | 149 |
| +1 | 68 | 16 | 59 | 143 |

**STD.** The best table is the relative frequencies, e.g. P(a3 = 0 | a4 = −1) = 137/1369 =
0.1001. LL_STD = Σ count × log(count / row total) = −1120.26278.

**MLR**, fitted by statsmodels (`fit_mlr(df, "a3", ["a4"])`), gives these coefficients:

| | child state 0 | child state +1 |
|---|---|---|
| intercept bⱼ | −2.099316 | −2.283098 |
| a4 = 0 dummy cⱼ₀ | 2.149747 | 1.623853 |
| a4 = +1 dummy cⱼ₁ | 0.652397 | 2.141128 |

Compare with step 3 of the argument, using only the counts:
b₀ = log(137/1118) = **−2.099316** and b₊₁ = log(114/1118) = **−2.283098**;
c₀₀ = log(61/58) − b₀ = **2.149747**; c₊₁,₁ = log(59/68) − b₊₁ = **2.141128**.
The optimizer found exactly the coefficients the argument predicts, so MLR's fitted
probabilities are the relative frequencies, and LL_MLR = −1120.26278 = LL_STD.

Both have 6 parameters, penalty 6 × log(1661)/2 = 22.24553, so
BIC_STD = BIC_MLR = **−1142.50831** (in `results/phase1.5/1.5.1-gobnilp-tie-fix/cpt-type-summary.csv`
both columns show −1142.5083085785432). Across all 0-/1-parent nodes the largest
|BIC_STD − BIC_MLR| is 4.5e-13 (GOBNILP structure) and 6.8e-13 (hc structure).

## 4. Where it appears in the code

- `pick_winner` in [`src/bnjoint/cpt_scores.py`](../../src/bnjoint/cpt_scores.py) treats scores
  within `config.TIE_TOLERANCE` = 1e-6 as tied and breaks ties by `config.TIE_ORDER`
  = (STD, OLR, MLR).
- Tests: `test_mlr_one_parent_equals_std_synthetic`, `test_mlr_equals_std_on_our_data` (all 18
  0-/1-parent families of the GOBNILP structure) and `test_mlr_no_parents_equals_std_no_parents`
  in `tests/test_cpt_scores.py`; the tie-rule tests are in the same file.

## 5. Common confusions

- **"If they're equal, why not compare with `==`?"** The two numbers come from different
  computations (a sum of counts × logs vs. an optimizer that stops when the gradient is tiny),
  so the last digits differ. Exact comparison of floating-point results is almost never right.
- **"Why 1e-6, not 1e-12?"** The noise here is ~1e-13, and real differences between types are
  at least 0.17 in our data. 1e-6 sits safely between the two; any value in that range gives
  the same winners.
- **"Why give the tie to STD?"** A tie means the data cannot tell the types apart, and STD is
  the simplest description (no regression machinery). The order STD, OLR, MLR is CLAUDE.md's
  convention.
- **The zero-count caveat.** If some (parent, child) combination never occurs, STD gives it
  probability exactly 0, while MLR can only approach 0 as a coefficient goes to −∞. The
  optimizer then stops at a large finite value: LL_MLR is a hair below LL_STD, and it may report
  non-convergence. This does not happen in our 1-parent families (checked: no zero cells in any
  of them, in either structure), but it can happen in Phase 2 with other parent sets.
- **"So MLR and OLR are the same for one parent too?"** No. OLR has only 3 parameters with one
  parent; it is a genuinely restricted model (it won d7 | a27, explainer 03).

## 6. Check your understanding

1. With k = 3 states and 1 parent, how many parameters do STD and MLR have? And with 2 parents?
2. In the a3 | a4 example, what is c₊₁,₀ (the a4 = 0 coefficient for child state +1), computed
   from the counts?
3. Why did MLR "win" six nodes in Phase 1, and what changed in step 1.5.1?
4. Give a situation where one-parent MLR and STD would NOT tie exactly.
5. Why can't the lemma be extended to 2 parents?

---

**Answers.**
1. 1 parent: both 6. 2 parents: STD 18, MLR 10.
2. log(30/58) − log(114/1118) = −0.659246 + 2.283098 = 1.623853, matching the fitted value.
3. Its BIC was larger by rounding noise (≤ 4.5e-13) and the old rule had no tolerance. Step 1.5.1
   treats differences below 1e-6 as ties and gives ties to STD.
4. A (parent, child) combination with zero count: MLR can't reach probability 0 with finite
   coefficients, so its LL stays slightly below STD's (and the fit may not converge).
5. With 2 parents STD has 18 parameters and MLR 10; MLR cannot represent parent interactions,
   so it describes fewer distributions and its maximized LL can be lower.
