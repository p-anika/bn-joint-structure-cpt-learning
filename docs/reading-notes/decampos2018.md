# Reading note: de Campos, Scanagatta, Corani & Zaffalon 2018

**Citation:** [decampos2018](../references.md#decampos2018). "Entropy-based pruning for learning
Bayesian networks using BIC", *Artificial Intelligence* 260 (2018). Read from the **arXiv
preprint v1** in `papers/` (2026-11-16). Theorem and lemma numbers below are those of the
preprint; check them in the journal version before quoting.

## The problem

Exact structure learning first builds, for each variable, a list of candidate parent sets with
their BIC scores, then optimizes over the lists (e.g. with GOBNILP). There are 2^(n−1) possible
parent sets per variable, so the lists must be pruned **safely**: without ever removing a
parent set that some optimal network uses.

## Key result in plain words

Notation: BIC(X|Π) = LL(X|Π) + Pen(X|Π), with Pen = −(log N / 2)·(|Ω_X| − 1)·|Ω_Π| (negative;
p. 3), and N·H(X|Π) = −LL(X|Π).

- **Lemma 1 (subset rule):** if a subset Π ⊂ Π* scores at least as well, Π* can be dropped.
  Safe for any decomposable score, but Π* must be scored first.
- **Lemma 2:** adding parents never lowers LL, never raises the entropy, and always makes the
  penalty worse.
- **Lemma 3 (= Theorem 4 of [de Campos & Ji 2011](decampos2011.md)):** if BIC(X|Π) ≥ Pen(X|Π*) for
  some Π ⊂ Π*, then Π* **and all its supersets** can be skipped without scoring them. Reason: LL is
  at most 0, so the best any superset can do is score its penalty, which is already beaten.
- **Theorem 1 (new):** with Π = Π* ∪ {Y}, if N·min{H(X|Π*), H(Y|Π*)} ≤ (1 − |Ω_Y|)·Pen(X|Π*),
  then Π and all its supersets can be skipped. The new ingredient is the entropy of the
  *candidate parent* Y: adding Y can raise LL by at most N·H(Y|Π*) (Lemma 4).
- **Theorem 2:** the same with entropies of any subset Π′ ⊆ Π*, e.g. single-variable entropies
  that are computed once, so pruning can happen before any score is computed.
- **Theorem 3:** an explicit bound on the number of parents in an optimal network.

## What our project reuses or extends

- **Reuses:** these are the rules for standard tables. `scoring2a.c` implements the subset filter
  and the de Campos & Ji bound, but not the entropy rules
  ([code-guide/scoring2a.md](../code-guide/scoring2a.md)). Our Phase 1 STD scores were pruned that way.
- **Extends:** every proof here uses two properties of the STD score: **LL ≤ 0** and a penalty
  that **grows with each added parent** (Lemma 2). For our joint score, max(BIC_STD, BIC_MLR,
  BIC_OLR), LL ≤ 0 still holds for each type, but the penalty that matters is the smallest one
  (OLR's, (k−1) + n), which grows only by 1 per parent. Whether, and how strongly, these rules
  carry over is the research question of Phase 3. Nothing about it is proven yet.
