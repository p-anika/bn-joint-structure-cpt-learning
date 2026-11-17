# Lemma: with at most one parent, MLR and STD have the same BIC

Status: **draft** (written by Claude, 2026-11-16; to be checked by Anika, then Jirka). Intuition
and a worked example from our data: [explainer](../explainers/one-parent-mlr-equals-std.md).
Notation follows [vomlel2026](../references.md#vomlel2026), Sec. 2–3.

## Novelty: a known fact, not a new result

This is a special case of a standard result in statistics: a *saturated* model, one with a free
parameter for every probability it must estimate, reproduces the observed relative
frequencies. Multinomial logistic regression with one fully dummy-coded categorical predictor
is saturated in this sense, so its maximum-likelihood fit equals the STD table. The statement
and proof below were written for this project (first noticed by Anika in Phase 1, written out
by Claude), not taken from a source, but the fact itself is not new.

- **In the paper:** present it as a remark or observation with a textbook reference, not as a
  contribution. It explains why Table 2 has STD on every 1-parent node, why CPT types need a tie
  rule, and why joint scoring can skip fitting MLR for parent sets of size 0 or 1.
- **Reference to be found and verified:** textbooks on categorical data analysis treat saturated
  logit and log-linear models (e.g. Agresti, *Categorical Data Analysis*), but no specific
  passage has been checked yet. Find it before citing, and add it to `docs/references.md`.
  Jirka may know a standard reference.

## Setting

Let X_v be a child variable with k ≥ 2 states {1, …, k}, state 1 being the reference state. Let it
have either no parent or one parent X_p, also with k states. Data D has N = |D| complete rows.
N(x_p, x_v) is the count of rows with parent value x_p and child value x_v, and N(x_p) the row
count for parent value x_p.

- **STD:** an unrestricted conditional distribution θ(· | x_p) for each parent value: (k−1)·k
  free parameters (paper eq. 6 with n = 1).
- **MLR** (paper eqs. 10–13): for child states j = 2, …, k,
  log [ P(X_v = j | x_p) / P(X_v = 1 | x_p) ] = β_{0,j} + Σ_{r=2..k} β_{r,j}·δ(x_p = r),
  where δ(x_p = r) is 1 if x_p = r and 0 otherwise. That is (k−1)·(1 + (k−1)) = (k−1)·k free
  parameters (paper eq. 12 with n = 1).

BIC = LL − (log N / 2)·C (paper eq. 9), where LL is the maximized log-likelihood and C the number
of free parameters.

## Statement

**Lemma.** Suppose every parent value that occurs in the data occurs together with every child
value: N(x_p, x_v) > 0 whenever N(x_p) > 0. (With no parent: every child value occurs.) Then

1. max LL_MLR = max LL_STD, and the MLR maximum is attained;
2. C_MLR = C_STD; hence
3. BIC_MLR = BIC_STD.

The same holds with no parent, with C = k − 1 for both.

## Proof

*(1, the "≤" direction.)* Every MLR model defines, for each parent value, a distribution over
the child with all probabilities positive; that is a valid STD table. So the MLR models are a
subset of the STD models, and max LL_MLR ≤ max LL_STD.

*(1, the "≥" direction.)* The STD maximum is the table of relative frequencies,
θ*(j | x_p) = N(x_p, j) / N(x_p) (paper eq. 5; standard result). By the assumption, every θ* is
strictly positive, so its logarithms are finite. Set

- β_{0,j} = log [ θ*(j | 1) / θ*(1 | 1) ],
- β_{r,j} = log [ θ*(j | r) / θ*(1 | r) ] − β_{0,j} for r = 2, …, k.

For parent value x_p = 1 all dummies are 0, so the log-odds is β_{0,j} = log [θ*(j|1)/θ*(1|1)].
For x_p = r ≥ 2 exactly one dummy is 1, so the log-odds is β_{0,j} + β_{r,j}
= log [θ*(j|r)/θ*(1|r)]. Log-odds against the reference state determine a distribution
uniquely (paper eqs. 14–15), so this MLR model equals θ* for every parent value. Hence
max LL_MLR ≥ LL(θ*) = max LL_STD. (Parent values that never occur contribute nothing to either
likelihood; their coefficients can be set to anything.)

*(2.)* (k−1)·k¹ = (k−1)·k = (k−1)·(1 + 1·(k−1)).

*(3.)* follows from (1), (2) and the BIC formula.

*No parent:* MLR has only the intercepts β_{0,j}, and choosing β_{0,j} = log [θ*(j)/θ*(1)] gives
the marginal frequencies. Both have k − 1 parameters. ∎

## Remarks

- **Zero counts.** If some N(x_p, j) = 0 while N(x_p) > 0, the STD maximum has θ*(j | x_p) = 0,
  which MLR can only approach as a coefficient tends to −∞. The *supremum* of LL_MLR still equals
  LL_STD, but no finite maximizer exists. An optimizer then stops at a large finite coefficient,
  with an LL slightly below LL_STD, and may report non-convergence. None of our 0-/1-parent
  families in Phases 1–1.5 has a zero cell (explainer, §5).
- **Two or more parents.** The equality breaks: with n = 2, STD has (k−1)·k² = 18 parameters and
  MLR (k−1)·(1 + 2(k−1)) = 10 (k = 3). MLR's log-odds are a sum of one term per parent, so it
  cannot represent interactions; it is a proper sub-model and LL_MLR ≤ LL_STD, usually strictly.
- **Numerically,** the two BICs differ only by floating-point error (sizes on our data:
  [phase-1.5.md](../reports/phase-1.5.md#151-gobnilp-structure)). That is why CPT types are
  compared with a tolerance (decision 55).
- **Use for joint scoring.** For parent sets of size 0 or 1, BIC_MLR need not be computed: it
  equals BIC_STD, and the tie rule picks STD anyway. Only BIC_STD and (for one parent) BIC_OLR are
  needed.
- **OLR is different.** With one parent OLR has (k−1) + 1 = k parameters, fewer than (k−1)·k for
  k ≥ 3, so it is a genuine restriction and can win (d7 and d10 in our data).
