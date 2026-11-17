# Glossary

One-line definitions, alphabetical. Each points to where the term is explained properly.
Explainers link here the first time they use a term.

### Adjacency matrix
A square table of 0/1 with one row and one column per variable; a 1 in row u, column v means an
arc u → v. Our files (`adjmat.txt`, `bnlearn-hc-dag.csv`) use row = parent, column = child.

### Alpha
scoring2a's penalty setting; alpha = 1 gives the true BIC penalty (decision 5;
[setup.md §6](setup.md#6-scoring2a-local-bic-scores)).

### Bayesian network
*BN.* A [DAG](#dag) over variables plus one [CPT](#cpt) per variable; together they define a joint
probability distribution.

### BIC
*Bayesian Information Criterion.* Score = [log-likelihood](#log-likelihood) − (log N / 2) × [free parameters](#free-parameter);
higher is better (paper eq. 7/9). Rewards fit, penalizes complexity
([explainer](explainers/cpt-types.md)).

### `.bnsl` file
GOBNILP's input: [local scores](#local-score) with a header line of variable names and
`SCORES START` ([setup.md §8](setup.md#8-the-bnsl-header-gobnilp-needs)).

### Convergence
An iterative fitting method (used for MLR and OLR) *converged* when it stopped at a maximum
rather than running out of iterations. Recorded per fit since step 1.5.1 (decision 56).

### CPDAG
*completed partially directed acyclic graph.* The graph that represents all DAGs that are [Markov equivalent](#markov-equivalence): arcs whose
direction the data can't decide are drawn undirected (`pdagadjmat.*`; step 1.5.3).

### CPT
*conditional probability table.* For one variable, the probabilities of its states given each combination of its parents' states.
Here it can be written three ways: [STD](#std), [MLR](#mlr), [OLR](#olr)
([explainer](explainers/cpt-types.md)).

### Cut-point
*threshold.* In [OLR](#olr), the numbers that split one continuous score into the ordered child states.

### DAG
*directed acyclic graph.* Arrows between variables with no cycle; the structure of a [Bayesian network](#bayesian-network).

### Dummy coding
Replacing a 3-state parent by two 0/1 columns ("is it 0?", "is it +1?"); the third state is the
[reference state](#reference-state). Used by [MLR](#mlr).

### Exact search
Structure learning that is guaranteed to find the best-scoring DAG for the given
[local scores](#local-score), e.g. [GOBNILP](#gobnilp). Opposite: [greedy search](#greedy-search).

### Family
A variable together with its [parent set](#parent-set). BIC is computed per family.

### Free parameter
A number in a model that is fitted to the data and not fixed by others (e.g. probabilities that
must sum to 1 have one fewer free parameter than states).

### GOBNILP
J. Cussens's program for [exact](#exact-search) BN structure learning by integer programming,
running on [SCIP](#scip) ([setup.md §7](setup.md#7-scip-and-gobnilp-exact-structure-search)).

### Greedy search
*hill-climbing.* Structure learning that repeatedly makes the single change (add, remove or reverse an arc) that
improves the score most, and stops when none does. Fast, but can stop at a local optimum.
bnlearn's `hc()` is used by the paper.

### Joint learning
Choosing the structure and each node's CPT type together: every [parent set](#parent-set) is
scored with the best of the three CPT types before the structure search. This project's
method. Opposite: [two-stage learning](#two-stage-learning).

### Local score
The BIC of one [family](#family). The score of a network is the sum of its local scores.

### Log-likelihood
How probable the data are under a model, on a log scale (always ≤ 0 here). Maximized when
fitting.

### Markov equivalence
Two DAGs are Markov equivalent if they imply the same independences; the data can't tell them
apart, and they have the same BIC. Represented by a [CPDAG](#cpdag).

### MLR
*multinomial logistic regression.* CPT type: log-odds of each child state are a sum of one coefficient per parent state
([dummy-coded](#dummy-coding)). (k−1)(1 + n(k−1)) parameters ([explainer](explainers/cpt-types.md)).

### OLR
*ordinal logistic regression.* CPT type for an ordered child: one slope per parent (parent values used as numbers) and k−1
[cut-points](#cut-point). (k−1) + n parameters ([explainer](explainers/cpt-types.md)).

### Palim
scoring2a's maximum number of parents per variable (we use 9; decision 5).

### Parent configuration
One combination of parent values, e.g. (a19 = −1, a27 = +1). n parents with 3 states have 3^n.

### Parent set
The variables with an arrow into a given variable.

### Penalty weight
log(N)/2: the BIC cost of one free parameter.

### Pruning
Removing candidate parent sets from the lists before structure search, to save time. **Safe**
pruning never removes a parent set that an optimal network uses ([safe pruning rule](#safe-pruning-rule)).

### Reference state
The state whose log-odds are fixed at 0 in [MLR](#mlr); others are compared with it. Here −1.

### Safe pruning rule
A [pruning](#pruning) rule proven never to change the optimum. In this project a rule is only
called safe when a test shows the pruned and unpruned lists give the same GOBNILP optimum
(CLAUDE.md; [reading notes](reading-notes/README.md)).

### SCIP
The integer-programming solver GOBNILP runs on (with the LP solver SoPlex).

### scoring2a
C. P. de Campos's program that computes [local BIC scores](#local-score) of candidate parent
sets with STD tables, with built-in [pruning](#pruning) ([code guide](code-guide/scoring2a.md)).

### STD
*standard / general table.* CPT type with a free distribution for every [parent configuration](#parent-configuration):
(k−1)·k^n parameters ([explainer](explainers/cpt-types.md)).

### Tie rule
How the CPT type is chosen when BICs are (numerically) equal: within 1e-6 counts as a tie, and
ties go to STD, then OLR, then MLR (decision 55; [explainer](explainers/one-parent-mlr-equals-std.md)).

### Two-stage learning
The paper's method: learn the structure with STD tables first, then choose each node's CPT type
on that fixed structure. Our Phase 1 baseline ([report](reports/phase-1.md)).
