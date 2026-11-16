# References

One entry per paper or software package the project relies on. Other docs link to these
entries (e.g. `docs/references.md#decampos2018`) instead of repeating citations. BibTeX
versions with the same keys are in [`references.bib`](references.bib).

Local PDF copies live in `papers/` at the repo root. That folder is git-ignored and must never be
committed: the repo is public and most papers are copyrighted.

**How each entry was verified** (2026-11-15/16; no internet access was available, so only
local sources were used). Anything not checked against one of these sources is marked
**Unverified**.

## Papers

### vomlel2026

Jiří Vomlel. Enhancing Bayesian networks through logistic regression: a case study of Czech
society divisions. *Kybernetika* 62(3), 2026, pp. 400–426. DOI
[10.14736/kyb-2026-3-0400](https://doi.org/10.14736/kyb-2026-3-0400).

- **Use here:** the baseline we reproduce and extend. It defines the STD/MLR/OLR CPT types and
  their BIC (the equations cited in `src/bnjoint/cpt_scores.py`), uses the data set in
  `data/raw/BN-data.csv`, and its Table 2 is `data/reference/kybernetika-table2.csv`.
- **Verified from:** the PDF in `papers/` (title page: journal, volume, year, number, pages, DOI).
  Jirka sent it on Jul 3, 2026.

### vomlel2023

Jiří Vomlel, Václav Kratochvíl, František Kratochvíl. Structural learning of mixed noisy-OR
Bayesian networks. *International Journal of Approximate Reasoning* 161, 2023, article 108990.
DOI [10.1016/j.ijar.2023.108990](https://doi.org/10.1016/j.ijar.2023.108990).

- **Use here:** the template for joint learning: its Algorithm 2 scores each parent set with the
  better of two CPT types and passes the list to GOBNILP. Its Section 5 documents the failed
  pruning attempts that make our pruning problem open; Jirka also pointed us to its Lemma 3.
- **Verified from:** the PDF's embedded metadata (title, authors, journal, volume, article
  number, DOI). Jirka sent it on Jul 8, 2026.

### decampos2018

Cassio P. de Campos, Mauro Scanagatta, Giorgio Corani, Marco Zaffalon. Entropy-based pruning
for learning Bayesian networks using BIC. *Artificial Intelligence* 260, 2018, pp. 42–50.
DOI [10.1016/j.artint.2018.04.002](https://doi.org/10.1016/j.artint.2018.04.002).
Preprint: [arXiv:1707.06194](https://arxiv.org/abs/1707.06194).

- **Use here:** the BIC pruning rules for STD parent sets that our project must extend to
  MLR/OLR. What `scoring2a.c` implements from it is in
  [`code-guide/scoring2a.md`](code-guide/scoring2a.md).
- **Verified from:** the arXiv PDF in `papers/` (title, four authors, arXiv:1707.06194v1, dated
  19 Jul 2017). The journal volume, pages and DOI come from the reference lists of
  [vomlel2026](#vomlel2026) (ref. 4) and [vomlel2023](#vomlel2023) (ref. 7). The local copy is
  the **arXiv preprint v1**, not the published version, so theorem numbers could differ
  between the two.

### decampos2011

Cassio P. de Campos, Qiang Ji. Efficient structure learning of Bayesian networks using
constraints. *Journal of Machine Learning Research* 12, 2011, pp. 663–689.

- **Use here:** the classic BIC pruning bound (its Theorem 4), which is the rule `scoring2a.c`
  actually implements ([`code-guide/scoring2a.md`](code-guide/scoring2a.md)).
- **Verified from:** the JMLR PDF in `papers/` (2026-11-16; first page: "Journal of Machine
  Learning Research 12 (2011) 663-689", title, authors Cassio P. de Campos and Qiang Ji). The
  details also match reference [7] of [decampos2018](#decampos2018) (checked by Anika). No DOI is
  printed on the paper, so none is given. That the bound is its *Theorem 4* comes from
  [decampos2018](#decampos2018); the theorem itself has not yet been read in the 2011 PDF.

### cussens2011

James Cussens. Bayesian network learning with cutting planes. In: F. G. Cozman, A. Pfeffer
(eds.), *Proceedings of the 27th Conference on Uncertainty in Artificial Intelligence (UAI
2011)*, AUAI Press, 2011, pp. 153–160.

- **Use here:** the integer-programming method behind GOBNILP; the paper the Kybernetika paper
  cites for GOBNILP.
- **Verified from:** `manual/manual.bib` in the GOBNILP source (`~/tools/gobnilp/`), which
  agrees with [vomlel2026](#vomlel2026) ref. 3.
- **DOI deliberately left out:** the Kybernetika reference list gives DOI
  10.5771/9780810873834-153 for it, but that prefix is not AUAI Press's and looks wrong
  (decided with Anika, 2026-11-16).

### cussens2017

James Cussens, Matti Järvisalo, Janne H. Korhonen, Mark Bartlett. Bayesian network structure
learning with integer programming: polytopes, facets and complexity. *Journal of Artificial
Intelligence Research* 58, 2017, pp. 185–229.

- **Use here:** the fuller description of GOBNILP's method; cited for GOBNILP in
  [vomlel2023](#vomlel2023) (ref. 6).
- **Verified from:** reference [6] of [vomlel2023](#vomlel2023) (authors, title, journal,
  volume, pages, year; confirmed by Anika 2026-11-16). The DOI is deliberately left out (not
  given there, not checked).

## Software

### gobnilp

James Cussens, Mark Bartlett. GOBNILP: learning Bayesian network structure with integer
programming (C implementation, uses SCIP).
<https://bitbucket.org/jamescussens/gobnilp>. We use git commit `5441edf`; versions and build
details are in [`setup.md`](setup.md).

- **Use here:** finds the BIC-optimal network from the local scores (`make phase1`).
- **Verified from:** the GOBNILP `README.md` ("GOBNILP was written by James Cussens and Mark
  Bartlett"). Jirka's own runs used GOBNILP 1.6.3, which [vomlel2023](#vomlel2023) cites as
  "J. Cussens, M. Bartlett, GOBNILP, Version 1.6.3, https://www.cs.york.ac.uk/aig/sw/gobnilp/,
  2018". The README asks for no specific citation; for the method, cite
  [cussens2011](#cussens2011) and/or [cussens2017](#cussens2017).

### scutari2010

Marco Scutari. Learning Bayesian networks with the bnlearn R package. *Journal of Statistical
Software* 35(3), 2010, pp. 1–22. DOI
[10.18637/jss.v035.i03](https://doi.org/10.18637/jss.v035.i03).

- **Use here:** bnlearn's hill-climbing `hc()` (how the Kybernetika structure was learned), and
  later CPDAG comparison (step 1.5.3). Version: see [`setup.md`](setup.md).
- **Verified from:** `citation("bnlearn")` in R, which names this as the paper to cite "for
  general use of bnlearn".

### scoring2a

`scoring2a.c`: local-score program by Cassio de Campos, based on GOBNILP's scoring code by James
Cussens. Unpublished; Jirka sent it on Jul 8, 2026 (`tools/scoring2a/`).

- **Use here:** computes the BIC of candidate parent sets for GOBNILP.
- **To cite:** no publication of its own; cite the pruning rule's paper
  ([decampos2011](#decampos2011)) and acknowledge de Campos for the code. **Unverified:** how
  de Campos would like it credited (could go in Email #3).
