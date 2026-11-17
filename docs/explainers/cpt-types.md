# The three CPT types: STD, MLR, OLR

Prerequisites: what a [Bayesian network](../glossary.md#bayesian-network) is and what
[BIC](../glossary.md#bic) is (explainers planned). Short versions: in a Bayesian network every variable (node) has a set of
*parents*, and the network stores, for each node, the probabilities of its states given every
combination of its parents' states. BIC = log-likelihood − (log N / 2) × (number of free
parameters); higher is better.

Terms used here (one-line definitions in the glossary): [CPT](../glossary.md#cpt), [STD](../glossary.md#std), [MLR](../glossary.md#mlr), [OLR](../glossary.md#olr), [parent configuration](../glossary.md#parent-configuration), [dummy coding](../glossary.md#dummy-coding), [reference state](../glossary.md#reference-state), [cut-point](../glossary.md#cut-point), [free parameter](../glossary.md#free-parameter), [log-likelihood](../glossary.md#log-likelihood), [two-stage learning](../glossary.md#two-stage-learning), [joint learning](../glossary.md#joint-learning).

## 1. Plain-words definition

A **CPT** (conditional probability table) is the part of a Bayesian network that says "if the
parents have these values, the child takes each of its values with these probabilities". In
our data every variable has 3 states (−1, 0, +1), so a CPT gives 3 probabilities (summing to 1)
for each parent configuration. There are several ways to *write* such a table, and they differ
in how many numbers (parameters) they need:

| Type | Name | Idea | Free parameters (k = 3 states, n parents) |
|---|---|---|---|
| **STD** | standard (general) table | A separate, unrestricted distribution for every parent configuration. | (k−1)·k^n: 2, 6, 18, 54 for n = 0, 1, 2, 3 |
| **MLR** | multinomial logistic regression | The log-odds of each child state (against a reference state, −1) is a *sum* of one number per parent state. Parents are "dummy-coded": parent state 0 and parent state +1 each get their own coefficient. | (k−1)·(1 + n(k−1)): 2, 6, 10, 14 |
| **OLR** | ordinal logistic regression | The child's states are treated as **ordered** (−1 < 0 < +1). One "latent score" = sum of slope × parent value; two cut-points split it into the three states. | (k−1) + n: –, 3, 4, 5 |

Words used above:

- **Parent configuration**: one combination of parent values, e.g. (a19 = −1, a27 = +1). With
  n parents of 3 states there are 3^n configurations.
- **Log-odds** of state j vs state −1: log( P(state j) / P(state −1) ).
- **Dummy coding**: replacing a 3-state parent by two 0/1 columns ("is it 0?", "is it +1?"); the
  state −1 is the *reference*, represented by both columns being 0.
- **Cut-points** (thresholds): two numbers θ₁ < θ₂. OLR says P(child ≤ −1) = σ(θ₁ − score) and
  P(child ≤ 0) = σ(θ₂ − score), where σ is the logistic function 1/(1+e^(−x)).

STD is the most flexible: any CPT can be written as an STD table. MLR can only express effects
that *add up* across parents (no interactions). OLR is the most restricted: each parent pushes
the child up or down the ordered scale with one slope. Fewer parameters means a smaller BIC
penalty, so a restricted type wins when the data does not need the extra flexibility.

## 2. Why it matters in this project

The Kybernetika paper's two-stage method learns the structure assuming STD, then picks the
type with the best BIC per node. This project scores all three types for every *candidate*
parent set and keeps the best (max of the three BICs), so that the structure and the CPT types
are chosen together. Every number in Phases 1–4 comes from these three formulas, all in
`src/bnjoint/cpt_scores.py`.

## 3. Worked example from our data

Node **a1** with parents **a19, a27** (GOBNILP structure; numbers from
`results/phase-1.5/1.5.1-gobnilp-tie-fix/cpt-type-summary.csv`). N = 1661, so one parameter costs
log(1661)/2 = 3.7076.

| Type | Log-likelihood | Parameters | Penalty | BIC |
|---|---|---|---|---|
| STD | −1343.86 | 18 | 66.74 | −1410.60 |
| MLR | −1347.66 | 10 | 37.08 | **−1384.74** ← winner |
| OLR | −1376.45 | 4 | 14.83 | −1391.28 |

STD fits best (highest log-likelihood, as it always must), but MLR loses only 3.80 in fit while
saving 8 parameters (29.66 in penalty). OLR saves even more parameters but loses too much fit.

A 1-parent example where the simplest type wins: **d7 | a27**. STD and MLR both have BIC
−1473.79 (they are the same model; see the [one-parent explainer](one-parent-mlr-equals-std.md)); OLR, with 3 instead of 6 parameters, has
−1471.64 and wins. Looking at the counts, d7 moves *up* the scale as a27 increases (P(d7 = +1)
is 66/711 = 9 % when a27 = −1 and 180/638 = 28 % when a27 = +1), which is exactly the kind of
ordered effect OLR describes with one slope.

## 4. Where it appears in the code

- Parameter counts: `n_params_std`, `n_params_mlr`, `n_params_olr` in
  [`src/bnjoint/cpt_scores.py`](../../src/bnjoint/cpt_scores.py).
- Fitting: `loglik_std` (counts, closed form), `fit_mlr` (statsmodels `MNLogit`), `fit_olr`
  (statsmodels `OrderedModel`, BFGS); dummy coding in `mlr_design`.
- Choosing: `pick_winner` (tie rule, the [one-parent explainer](one-parent-mlr-equals-std.md) explains why it is needed).
- Walkthrough: [`docs/code-guide/cpt-scoring.md`](../code-guide/cpt-scoring.md).
- Coding choices (reference state, OLR with raw parent values, no OLR without parents):
  decision log entries 7–9.

## 5. Common confusions

- **"MLR is logistic regression, so it's an approximation."** For 0 or 1 parents it is not: it
  is exactly the STD model written differently (explainer [one-parent MLR = STD](one-parent-mlr-equals-std.md)). It only becomes restrictive at
  2+ parents.
- **"OLR treats the *parents* as ordered too."** In our coding, yes: parents enter as the numbers
  −1, 0, +1 with one slope, so "0 is halfway between −1 and +1" is assumed. The paper's
  parameter count (k−1)+n implies this coding, but it is still to be confirmed with Jirka
  (decision 8; Email #3).
- **"STD can never win with 2 parents."** It can, if the parents interact strongly. In our data
  it never did (in Table 2 neither), but that is a property of the data, not a rule.
- **"OLR without parents."** It would equal STD; we don't fit it (score −∞, decision 9).
- **"Higher BIC is worse."** In this project BIC is the log-likelihood *minus* a penalty, so all
  values are negative and the one closest to zero wins.

## 6. Check your understanding

1. How many free parameters does each type have for a node with 3 parents?
2. Why does STD always have the highest log-likelihood of the three for the same parent set?
3. For a1 | a19, a27, by how much would MLR's log-likelihood have to drop before OLR wins?
4. What does the "reference state" of MLR mean, and which state is it here?
5. Why can OLR win for d7 | a27 even though it fits worse than STD?

---

**Answers.**
1. STD 2·27 = 54, MLR 2·(1 + 3·2) = 14, OLR 2 + 3 = 5.
2. Every MLR or OLR table is also a possible STD table, and STD's log-likelihood is the maximum
   over *all* tables, so it can only be at least as high.
3. OLR's BIC is −1391.28; MLR's is −1384.74. MLR's log-likelihood would have to drop by more than
   6.54 (to below −1354.20).
4. The child state whose log-odds are fixed at 0; the other states are compared with it. Here it
   is −1 (for child and for dummy-coded parents).
5. It loses 8.97 in log-likelihood (−1460.52 vs −1451.55) but saves 3 parameters = 11.12 in
   penalty, a net gain of 2.15.
