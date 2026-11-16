# Methods notes (paper-style)

Paragraphs describing exactly what was done, to assemble the Methods section later. Results
are not repeated here; they are in `docs/reports/`. Software versions are not repeated either:
they are in [`docs/setup.md`, "Versions in use"](../setup.md#versions-in-use); fill them in from
there when writing the paper. Appended per step; the step is in brackets.

## Data [Phase 1; verified in 1.5.0b]

We use the data set of Vomlel (Kybernetika 62(3), 2026): 1661 respondents and 44 variables
(a1–a30, d1–d14), each with three states coded −1, 0, +1. The file was provided by the author
(`data/raw/BN-data.csv`). It was obtained from the preprocessed survey responses on a 1–7 scale
by mapping answers 1–3 to −1, 4 to 0 and 5–7 to +1; re-running the author's conversion code on
the preprocessed file reproduces the data file exactly. All 44 variables are treated as
categorical with k = 3 states.

## Local scores and exact structure learning [Phase 1]

Local BIC scores were computed with `scoring2a` (based on GOBNILP's scoring code by J. Cussens,
modified by C. P. de Campos), compiled with g++ (`-O2`), with alpha = 1 (the standard
BIC penalty), a maximum of 9 parents per node, and its built-in pruning enabled. The score is
BIC = LL − (log N / 2)·C, with natural logarithms and C = (k − 1)·k^n free parameters for a
node with n parents, counting all parent configurations. The BIC-optimal directed acyclic graph
for these local scores was found with GOBNILP (Bitbucket `jamescussens/gobnilp`) using the
SCIP Optimization Suite (SCIP with the LP solver SoPlex), which solved the problem to a gap of
0 %.

## CPT types on a fixed structure (two-stage method) [Phase 1]

For each node of the learned structure, three CPT types were fitted by maximum likelihood on
all 1661 rows and compared by BIC: a general table (STD; closed-form counts), multinomial
logistic regression (MLR; each parent dummy-coded with state −1 as reference; (k − 1)(1 + n(k − 1))
parameters) and ordinal logistic regression (OLR; logit link, parents entering as their numeric
values −1/0/+1; (k − 1) + n parameters). OLR is only considered for nodes with at least one
parent. MLR and OLR were fitted with the Python package statsmodels (`MNLogit`; `OrderedModel`
with BFGS). The type with the highest BIC was selected per node.
(Tie handling is revised in step 1.5.1.)

## Hill-climbing comparison [Phase 1]

For comparison, a structure was learned with the hill-climbing algorithm `hc` of the R
package bnlearn with the BIC score and default settings, after `set.seed(1)`,
which is how the structure in the Kybernetika paper was obtained.

## Reproducibility [1.5.0b]

All stages are driven by a Makefile (`make phase1`); the scoring and structure-learning
programs are deterministic for a given input. Source code, settings files and checksums of the
original data are kept in the project repository.
