# Baseline reproduction notes (Phase 1)

## Background, for future-me
Phase 1's goal: reproduce the "two-stage" result from the Kybernetika paper.
"Two-stage" means: first learn one BN structure (which variable depends on
which) assuming every node uses a plain lookup-table CPT, then -- with that
structure now frozen -- go back and check, node by node, whether swapping in
a Multinomial Logistic Regression (MLR) or Ordinal Logistic Regression (OLR)
representation gets a better BIC score than the table did. BIC (Bayesian
Information Criterion) rewards a model for fitting the data well but
penalizes it for having more parameters -- so a fancier model only "wins" if
its better fit is worth more than the complexity it costs.

The paper's own formula (their eq. 7/9) is:
    BIC = log-likelihood - (log(N)/2) * (number of parameters)
Higher is better under this convention (this is the opposite sign from the
"-2*LL + k*log(n)" convention used in most stats textbooks -- don't mix the
two, they'll give the same *ranking* but look like different numbers).

## Environment gotchas discovered while running this (useful if re-running later)
- `bn-project` and the GitHub repo `bayesian-network-learning` are the same
  repo -- the local folder name just doesn't match the GitHub repo name.
  That's fine and doesn't need fixing, Git doesn't care about folder names.
- GOBNILP wasn't on PATH after building it -- fixed by symlinking the built
  binary into `~/.local/bin/gobnilp` and adding that folder to PATH in
  `~/.bashrc`.
- This GOBNILP build's command-line syntax needs `-f <file>` for the input
  file, not a bare filename argument (older versions apparently accepted a
  bare filename; this one doesn't).
- `gobnilp.set` (inherited from Jirka's older 1.6.3-era setup) sets a
  parameter called `gobnilp/outputfile/adjacencymatrix` that this newer
  GOBNILP build doesn't recognize -- it prints a harmless warning and just
  never writes the `bi.mat` adjacency-matrix file. Not a real problem: the
  console output GOBNILP prints while solving already contains every
  learned family in an unambiguous `child:-{parents}` format, so that's
  what `scripts/fit_cpt_types.py` parses instead of relying on `bi.mat`.

## Step 1.3 result: GOBNILP structure search
- Ran: `gobnilp -f bn-data-44-bic-fixed.bnsl -s gobnilp.set`
- Status: **optimal solution found, 0.00% gap** -- this is the exact
  BIC-best structure under standard (table) CPTs, not an approximation.
- Objective (total BIC across all 44 families): **-64837.74**

**Note on this number vs. the paper's Figure 4:** the paper's plotted BIC
values are roughly -58,500 to -59,000, noticeably less negative than mine.
My best guess why: Figure 4's numbers come from 10-fold cross-validation,
so each of those runs trained on 90% of the data (~1495 rows) rather than
the full 1661. Since -58,500 / -64,838 is almost exactly 0.9, that lines up
with a "less data = less negative log-likelihood penalty" effect. This is a
hypothesis, not a confirmed explanation -- worth asking Jirka directly
rather than assuming it's settled.

**Structural note:** my learned graph has exactly one variable with zero
parents (D11). Interestingly, the paper's own structure (their Table 2/8)
also has exactly one zero-parent variable, though it's a different one
(A3). Same count, different specific root -- a small but reassuring sign
that the two structures, while not identical, aren't wildly different in
character. Max parents-per-node in mine is 2, matching the paper's own
structure (their Table 2 never shows more than 2 parents either) -- so the
`alpha`/`palim` choice from step 1.2, while still not confirmed against
whatever the paper actually used, at least produced a structure of similar
"shape."

## Step 1.4 result: STD/MLR/OLR split
- Paper's reported split: 19 STD (43%), 22 MLR (50%), 3 OLR (7%)
- Mine: **10 STD (23%), 30 MLR (68%), 4 OLR (9%)**

Noticeably more MLR-heavy than the paper's split. Best guess why: this
almost certainly traces back to the structure itself, not the CPT-fitting
step. The paper used `bnlearn`'s hill-climbing (`hc()`) to find its
structure (confirmed in Jirka's Aug 12 email), which is a *greedy* search --
it's not guaranteed to find the true BIC-optimal graph, just a local
optimum. My structure came from GOBNILP's exact search, which **is**
guaranteed optimal. Different structures mean different actual parent
sets for each node, which means each node's STD-vs-MLR-vs-OLR comparison
is being run on a different "family" than in the paper -- so a different
overall split isn't surprising. Step 1.6 (the `bnlearn` cross-check) will
help pin down how much of this gap is "different structure" vs. something
else, since it lets me compare CPT-type splits under both structures.

## An important quirk I noticed: STD and MLR sometimes tie exactly
Look at the raw fit_cpt_types.py output for any node with **1 or fewer
parents** -- e.g. `a3: STD=-1142.51 MLR=-1142.51`. This isn't a coincidence
or a bug. Here's why it happens, worth understanding rather than just
noting: MLR represents a parent by "dummy" variables, one per non-reference
state. For a single parent with 3 states, that's 2 dummy variables plus an
intercept -- exactly enough free parameters to reproduce *any* possible
table of conditional probabilities for that parent, with no
loss of flexibility at all. In other words, for a 1-parent (or 0-parent)
node, MLR isn't an *approximation* of the table CPT -- it's mathematically
capable of representing the exact same distribution, using the exact same
number of parameters. So STD and MLR are actually the same model in this
case, just written two different ways, and will always tie (up to tiny
floating-point noise from however MLR's iterative fitting converges).

Practically, this means: which one gets reported as the "winner" for
1-parent nodes can flip between STD and MLR based on floating-point noise
alone, not a real modeling difference. This won't happen for 2+-parent
nodes (dummy-coding two 3-state parents needs 4 dummy columns, but MLR only
gets `n*(k-1) = 2*2 = 4`... actually double check this per-node, in general
whenever a node has 2+ parents, MLR's parameter budget is smaller than a
full table would need, so it's a genuine, lossy approximation there -- no
tie is expected or seen for any 2-parent node in this run). This is
consistent with the paper's own finding (and mine): every multi-parent
winner was MLR or OLR, never STD -- because STD can only ever *tie* MLR
for small families, never actually beat it.

## Multi-parent nodes: did all of them use MLR/OLR?
Yes, matching the paper's claim exactly: scanning every 2-parent family in
my result, none of them picked STD as the winner -- all went to MLR or
OLR. All 10 of my STD winners have 0 or 1 parent, same pattern the paper
reports for its own STD winners.

## Max parent count sanity check
Paper's final structure: max 2 parents per node (their Table 2).
Mine: also max 2 parents per node. This matches, which is a reasonable
(though not certain) sign that `alpha=1, palim=9` from step 1.2 isn't
producing a wildly different kind of structure than whatever was used for
the paper -- still worth confirming with Jirka directly since the exact
value was never stated anywhere.

## Discrepancies and best guesses why
- Overall split (23/68/9 mine vs. 43/50/7 paper) -- most likely explained
  by GOBNILP exact search vs. paper's `bnlearn` hill-climbing producing
  different structures (see above); the 1.6 cross-check should clarify
  how much of the gap this accounts for.
- STD/MLR near-ties on 0- and 1-parent nodes are a mathematical
  equivalence, not a real discrepancy -- see the quirk section above.
- Total BIC magnitude (-64838 mine vs. ~-58500 to -59000 paper) -- likely
  explained by the paper's numbers coming from 10-fold cross-validation
  (90% of the data per fold) rather than the full dataset; unconfirmed,
  worth asking.
- `alpha`/`palim` in scoring2a (step 1.2) -- still unconfirmed by the paper
  or correspondence; the max-parent-count match above is a reassuring but
  not conclusive sign these were reasonable choices.



  LEFT OFF RIGHT BEFORE PHASE 1.6 !!!! PICK UP FROM PHASE 1.6