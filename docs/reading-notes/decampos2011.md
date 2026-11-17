# Reading note: de Campos & Ji 2011, JMLR

**Citation:** [decampos2011](../references.md#decampos2011). "Efficient structure learning of
Bayesian networks using constraints", *JMLR* 12 (2011), 663–689. Read from the PDF in
`papers/` (2026-11-16), Sec. 4.1 (pp. 670–672).

## The problem

Exact structure learning needs the score of every candidate parent set of every variable, a
cache of up to n·2^(n−1) entries. The paper derives properties of decomposable scores (BIC/AIC
and BD) that let most entries be skipped **without losing global optimality**. It also gives a
branch-and-bound search with structural constraints, which we don't use.

## Key result in plain words

Notation (eq. 1, p. 667): local score s_i(Π_i) = max L_Π(θ) − t_i(Π_i)·w, with
t_i(Π_i) = r_Π·(r_i − 1) the number of free parameters and w the penalty weight (log N / 2 for
BIC).

- **Lemma 1 (p. 670):** if a subset Π_i ⊂ Π′_i has a better score, Π′_i is not the parent set in
  an optimal DAG. Because removing arcs can't create a cycle, swapping in the subset gives a
  valid, better graph.
- **Theorem 2 / Corollary 3 (p. 671–672):** once the parent configurations are numerous enough
  (r_Π > N·log r_i / (w·(r_i − 1))), no proper superset can be optimal. Hence an optimal graph has
  O(log N) parents per node.
- **Theorem 4 (p. 672), the bound `scoring2a.c` uses:** if t_i(Π′_i) + s_i(Π_i) > 0 for some
  Π_i ⊂ Π′_i, then Π′_i **and all its supersets** are not optimal. Reason: the log-likelihood is
  ≤ 0, so a superset's score is at most minus its penalty, which is already below the subset's
  score. [de Campos et al. 2018](decampos2018.md) (footnote 1) note that t_i here should include
  the weight w. Their Lemma 3 is the corrected statement, BIC(X|Π) ≥ Pen(X|Π*).

## What our project reuses or extends

- **Reuses:** Theorem 4 (with w) is the pruning that produced our Phase 1 STD scores, through
  `scoring2a` ([code-guide/scoring2a.md](../code-guide/scoring2a.md)). Lemma 1 is safe for our
  joint score as it stands: it only compares final scores, whatever CPT type produced them.
- **Extends:** Theorem 4's argument needs only "LL ≤ 0" and "the penalty of a superset is at
  least that of the subset". For a joint score that keeps the best of three CPT types, the
  smallest possible penalty of a superset is OLR's. A joint version of the bound would replace
  t_i(Π′)·w with that smallest penalty: weaker, but possibly still safe. This is a lead for
  Phase 3, **not a result**: it needs a proof and a GOBNILP same-optimum test before it is called
  safe (CLAUDE.md).
