# Reading note: Vomlel, Kratochvíl & Kratochvíl 2023, IJAR

**Citation:** [vomlel2023](../references.md#vomlel2023). "Structural learning of mixed noisy-OR
Bayesian networks", *International Journal of Approximate Reasoning* 161, 108990. Read from the
PDF in `papers/` (2026-11-16), focusing on Sec. 3 and the pruning part of Sec. 5.

## The problem

Binary networks where each CPT is either a general table or a (leaky) noisy-OR model. A
noisy-OR needs only |pa(v)| + 1 parameters (eq. 14), against 2^|pa(v)| for a table (eq. 13). The
paper learns the structure **and** the CPT type of every node **together**, optimally.

## Key result in plain words

- **Algorithm 2 (Sec. 3, p. 7), the joint-scoring template:** for every node v and every
  candidate parent set U, compute the BIC of the general table (closed form) and of the
  noisy-OR (EM algorithm, Algorithm 1), keep the **higher** of the two, and add (v, U, BIC) to the
  list L. GOBNILP then picks the optimal acyclic network from L. Because each list entry carries
  its best type, structure and types are optimal together.
- **Lemma 3 (p. 8), the pruning that is safe for any CPT type:** drop (v, U, BIC) if some
  subset U′ ⊂ U already has a better score. This is the classic subset rule (Lemma 1 of
  [de Campos et al. 2018](decampos2018.md)). It needs U's score to be computed first, so it
  shortens the list but saves no scoring time.
- **Lemmas 1–2:** the noisy-OR log-likelihood is strictly concave, so it has a unique maximum.
- **Sec. 5, "Parent sets pruning" (pp. 13–14): the open problem.**
  - Sharma et al.'s two noisy-OR rules hardly pruned anything on the loanword data.
  - Pruning all supersets of a parent set that is worse than one of its subsets is fast but
    *not* safe (used only as a heuristic).
  - A conjectured rule, "prune U if no subset one element smaller beats its subsets", is
    **false**. Table 4/5 give a counterexample from the data (found in 27 of about 42 million
    sets).
  - Conclusion (p. 14): "It remains an open problem whether there are pruning rules that
    efficiently prune the space of parent sets for mixed Noisy-OR BNs to a similar extent as for
    standard BNs."
- **Sec. 6 (pp. 16–17)** names as future work exactly our setting: mixed BNs whose CPTs are
  either standard tables or logistic regression models.

## What our project reuses or extends

- **Reuses:** Algorithm 2 with {STD, MLR, OLR} in place of {table, noisy-OR}. That is our Phase 2
  joint scoring (score = max of three BICs per parent set, then GOBNILP). Lemma 3 is safe for us
  too, since it only compares final scores.
- **Extends:** the open problem of Sec. 5, for MLR/OLR. Its two lessons shape our pruning work:
  a rule must be **proven** (the cardinality conjecture failed only on 27 of about 42 million
  sets), and "safe" must be tested by comparing the GOBNILP optimum with and without pruning
  (CLAUDE.md).
- **Why it is hard for both:** a cheap CPT type has a small penalty, so large parent sets can win.
  The bounds for tables rely on the table's large penalty growing fast, and that is what
  fails for noisy-OR and for MLR/OLR.
