# Reading note: Vomlel 2026, Kybernetika

**Citation:** [vomlel2026](../references.md#vomlel2026). "Enhancing Bayesian networks through
logistic regression: a case study of Czech society divisions", *Kybernetika* 62(3), 400–426.
Read from the PDF in `papers/` (2026-11-16).

## The problem

A standard CPT needs (k−1)·k^n parameters for a node with n parents, which is exponential in n.
BIC penalizes every parameter, so structure learning with standard tables keeps parent sets
small, even when the data support more parents. The paper asks whether cheaper CPT forms,
multinomial logistic regression (MLR) and ordinal logistic regression (OLR), give better BNs
on real survey data.

## Key result in plain words

- **Two CPT alternatives with linear parameter counts** (Sec. 3.1–3.2): MLR has (k−1)(1 + n(k−1))
  parameters (eq. 12), OLR has (k−1) + n (eq. 17). Table 1 (p. 411) lists the counts for 0–3
  parents.
- **The two-stage method** (Algorithm 1, Sec. 3.3): learn the structure with standard CPTs by
  maximizing BIC, then, for each node, keep whichever of STD, MLR or OLR has the highest local
  BIC (eq. 9). The BIC of the result can't be worse than the table-only model (footnote 3).
- **Application** (Sec. 4): 1661 respondents, 44 opinion variables (a1–a30, d1–d14), answers 1–7
  mapped to −1/0/+1 (k = 3). The structure comes from bnlearn hill-climbing (confirmed by Jirka;
  decision 19). The result is Table 2 (p. 411): 19 STD, 22 MLR, 3 OLR. Every node with 2 parents
  uses MLR or OLR. Figure 4 (10-fold cross-validation) shows a better BIC with about 60 % of the
  parameters and similar prediction accuracy.
- **The text says "all 17 standard CPTs"** (Sec. 4.3, p. 410) while Table 2 lists 19. That is an
  inconsistency in the paper (see [phase-1.md](../reports/phase-1.md#comparison-with-the-paper)).

## What our project reuses or extends

- **Reuses:** the data, the three CPT types and their parameter counts, BIC with natural log
  (eq. 7/9), and the two-stage method as our baseline. Our code reproduces Table 2 exactly on
  the hill-climbing structure ([phase-1.5.md](../reports/phase-1.5.md#152-hc-structure-vs-table-2)).
- **Extends:** Sec. 3.3 names the next step itself. Integrating the CPT-type choice into structure
  learning "would require developing efficient search space methods, likely incorporating
  parent set pruning techniques similar to those proposed by de Campos [4]", and is "deferred to
  future research". That is this project: score every parent set with max(BIC_STD, BIC_MLR,
  BIC_OLR), find the optimum with GOBNILP, and develop safe pruning for that score.
- **Detail worth knowing:** the OLR example (Example 3.2) puts the parent *values* directly into
  the linear term, α₁·a + α₂·b. That matches our coding (decision 8). The paper's example uses
  values 1, 2, 3 and we use −1, 0, +1; a shift of the values is absorbed by the cut-points ζ,
  so the fitted model and its likelihood are the same. The paper also states (Sec. 4.2) that it
  does not assume the *variables* are ordinal, which is why STD and MLR are offered too.
