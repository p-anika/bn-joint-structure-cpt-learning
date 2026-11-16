# Baseline reproduction notes (Phase 1)

> **Note (2026-11-15).** This file was `docs/baseline_reproduction_notes.md` until step 1.5.0a;
> it was moved here unchanged. Jirka has seen the original, so mistakes are fixed with dated
> **Correction** notes placed next to the original text, never by rewriting it. Each
> correction is explained in `docs/reports/1.5.0a.md`.

> **Note (2026-11-15, step 1.5.0b): files moved.** The paths in this report are the
> September paths. Contents are unchanged (moved with `git mv`; every derived file was rebuilt
> from scratch and came out identical, see `docs/reports/1.5.0b.md`). New locations:
>
> | Path in this report | Now |
> |---|---|
> | `data/BN-data.csv` | `data/raw/BN-data.csv` |
> | `data/bn-data-44.dat`, `data/bn-data-44-bic.scores` (and the `-fixed.bnsl`, varnames files) | `data/processed/…` (same names) |
> | `results/gobnilp-std-run.log`, `results/cpt-type-summary.csv`, `results/bnlearn-hc-dag.csv` | `results/phase1/…` (same names) |
> | `src/scoring2a.c`, `src/gobnilp.set` | `tools/scoring2a/scoring2a.c`, `tools/gobnilp/gobnilp.set` |
> | `scripts/bnlearn_hc.R` | `R/bnlearn_hc.R` |
> | `python scripts/convert_data.py`, `bash scripts/run_gobnilp_pipeline.sh`, `python scripts/fit_cpt_types.py`, `Rscript scripts/bnlearn_hc.R` | all four: `make phase1` (`run_gobnilp_pipeline.sh` was replaced by the Makefile) |

## Reproducibility details

> **Note (2026-11-15, step 1.5.0b):** the software versions, the build details of GOBNILP and
> scoring2a, and the step-by-step run instructions that stood here (sections "Reproducibility
> details" and "How to reproduce these results from scratch") now live in one place each:
> versions in [`docs/setup.md`, "Versions in use"](../setup.md#versions-in-use), running the
> pipeline in [`docs/code-guide/phase1-pipeline.md`](../code-guide/phase1-pipeline.md)
> (`make phase1`). The removed text can be read with `git show a183df9:docs/reports/phase-1.md`.
> **Correction (2026-11-15):** that text said `scoring2a.c` came in Jirka's Aug 5 email; it came
> in his **Jul 8, 2026** email ("unix files.zip"), and the Aug 5 email sent only `BN-data.csv`
> (confirmed by Anika; decision log entry 14). No result or finding was changed; the finding
> below is kept as it was.

- Randomness: `scoring2a` and GOBNILP's exact search are deterministic given
  the same input file -- no seed needed. `bnlearn::hc()` in
  `scripts/bnlearn_hc.R` was run with `set.seed(1)` before calling
  `hc()`. Confirmed reproducible: re-running the script produced an
  identical structure (same 66-arc model string, same penalization
  coefficient) both times.

## File map -- where each claim in this document comes from
| Claim | Source file |
|---|---|
| Full 44-variable STD/MLR/OLR structure + winners | `results/cpt-type-summary.csv` |
| GOBNILP's exact structure + solve statistics | `results/gobnilp-std-run.log` |
| bnlearn's hill-climbed structure | `results/bnlearn-hc-dag.csv` (arcs) + console output pasted below |
| Local BIC scores per candidate family (pre-GOBNILP) | `data/bn-data-44-bic.scores` |
| Raw survey data (44 vars, -1/0/1 coded) | `data/BN-data.csv` (sent by Jirka, email Aug 5 2026) |

## Background
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

> **Note (2026-11-15, step 1.5.0b):** the gotchas listed here (GOBNILP on the PATH, the `-f`
> flag, the ignored `gobnilp.set` parameter and `bi.mat`, the repo name) now live in
> [`docs/setup.md` §7c–7d](../setup.md#7-scip-and-gobnilp-exact-structure-search) and §2. The
> original text is in this file's git history.

## Step 1.3 result: GOBNILP structure search
- Ran: `bash scripts/run_gobnilp_pipeline.sh` (internally:
  `gobnilp -f bn-data-44-bic-fixed.bnsl -s gobnilp.set`)
- Status: **optimal solution found, 0.00% gap** -- this is the exact
  BIC-best structure under standard (table) CPTs, not an approximation.
- Objective (total BIC across all 44 families): **-64837.74**
- Total directed arcs in this structure: **69** (summed from per-variable
  parent counts in `results/cpt-type-summary.csv`)

**Note on this number vs. the paper's Figure 4:** the paper's plotted BIC
values are roughly -58,500 to -59,000, noticeably less negative than mine.
My best guess why: Figure 4's numbers come from 10-fold cross-validation,
so each of those runs trained on 90% of the data (~1495 rows) rather than
the full 1661. Since -58,500 / -64,838 is almost exactly 0.9, that lines up
with a "less data = less negative log-likelihood penalty" effect. This is a
hypothesis, not a confirmed explanation -- worth asking Jirka directly
rather than assuming it's settled.

> **Correction (2026-11-15):** confirmed. Jirka wrote on Sep 28, 2026: "I can confirm that the
> BIC, number of parameters and log-likelihood in Figure 4 come from the 10-fold
> cross-validation." So the Figure 4 numbers and our full-data −64837.74 are not directly
> comparable. (The 0.9 ratio above is still only a rough consistency check, not a derivation.)

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
overall split isn't surprising. Step 1.6 (the `bnlearn` cross-check) helped
pin down how much of this gap is "different structure" vs. something else
(see below).

> **Correction (2026-11-15):** the split was 10/30/4 because of a tie-breaking bug, not only
> because of the structure. Six nodes with 0 or 1 parents (a13, a15, d6, d11, d12, d13) were
> labelled MLR even though their STD and MLR scores in `results/cpt-type-summary.csv` differ
> by at most 4.5e-13, which is floating-point noise (see the "quirk" section below). The script
> picked whichever number happened to be larger. Under the project's tie rule (scores within
> 1e-6 are tied; ties go to STD, then OLR, then MLR), those six become STD. Applying that rule
> to the existing CSV gives **16 STD, 24 MLR, 4 OLR**. The official corrected split comes from
> re-running the fixed script in step 1.5.1; see `docs/reports/1.5.1.md`. The remaining gap to
> the paper's 19/22/3 is what step 1.5.2 (fitting on the hc structure) tests.

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

> **Correction (2026-11-15):** two fixes to this paragraph.
> 1. *The unfinished sentence.* With k = 3 states and n = 2 parents, STD has
>    (k−1)·k^n = 2·9 = **18** parameters and MLR has (k−1)·(1 + n(k−1)) = 2·5 = **10**
>    (paper eq. 6 and 12). So for 2+ parents MLR is a restricted model with fewer parameters,
>    not just the table written differently. That part of the paragraph was right.
> 2. *"STD can only ever tie MLR, never beat it" is wrong for 2+ parents.* STD is the most
>    flexible model for a given parent set, so its log-likelihood is always **at least** MLR's.
>    BIC also subtracts a penalty, and STD's is larger (18 vs 10 parameters). STD therefore wins
>    when its better fit outweighs the extra penalty, for example when the two parents have a
>    strong *interaction* (their combined effect isn't the sum of their separate effects), which
>    MLR can't represent. In this data that simply didn't happen. The *observation* is correct:
>    no 2-parent node chose STD, in our run or in the paper's Table 2
>    (`data/reference/kybernetika-table2.csv`). The *reason* is the data, not a mathematical rule.

## Multi-parent nodes: did all of them use MLR/OLR?
Yes, matching the paper's claim exactly: scanning every 2-parent family in
my result, none of them picked STD as the winner -- all went to MLR or
OLR. All 10 of my STD winners have 0 or 1 parent, same pattern the paper
reports for its own STD winners.

> **Correction (2026-11-15):** all 10 STD winners have exactly **1** parent. The only 0-parent
> node, d11, was labelled MLR because of the tie bug described above.

## Max parent count sanity check
Paper's final structure: max 2 parents per node (their Table 2).
Mine: also max 2 parents per node. This matches, which is a reasonable
(though not certain) sign that `alpha=1, palim=9` from step 1.2 isn't
producing a wildly different kind of structure than whatever was used for
the paper -- still worth confirming with Jirka directly since the exact
value was never stated anywhere.

## Step 1.6 result: bnlearn hill-climbing cross-check
Ran `Rscript scripts/bnlearn_hc.R`. Result: 44 nodes, 66 directed arcs, 0
undirected arcs, average branching factor 1.50 (i.e. ~1.5 parents per
variable on average).

**Useful sanity check:** the printed "penalization coefficient" was
3.707588. This is exactly log(1661)/2 = 3.7076 -- i.e. `bnlearn` is using
the *same* BIC penalty-weight convention (log(N)/2) as the paper's formula
(eq. 7/9) and as `scoring2a`. Nice confirmation that all three pieces of
software agree on what "BIC" means here, even though they're independently
implemented.

**Comparing structures directly:** GOBNILP's exact-optimal structure (step
1.3) has 69 total arcs; bnlearn's hill-climbing found 66. Close, but not
identical -- expected, since hill-climbing is greedy and isn't guaranteed
to find the true best graph, while GOBNILP's search is exact.

One concrete example of the two disagreeing at the individual-edge level:
GOBNILP puts A4 as a parent of A3 (`a3: parents=['a4']`); bnlearn's model
string has `[a4|a3]`, meaning the *reverse* -- A3 as a parent of A4. Same
two variables, connected either way, just opposite direction. This is a
nice concrete illustration of exactly the kind of discrepancy predicted
earlier in these notes (greedy vs. exact search converging to different,
comparably-good structures) -- not a bug, just a real limitation of
hill-climbing as a search method.

Full bnlearn console output, preserved here for the record:
```
  Bayesian network learned via Score-based methods
  model:
   [a3][a4|a3][a1|a4][a9|a4][a27|a1][a28|a4:a27][d7|a27][a18|a27:a28][d8|a28]
   [d12|d7][a2|a4:a18][a30|a18:a28][d10|d8][d11|a18:a27][d13|d12][a17|a18:d10]
   [a19|a1:d11][d2|d7:d13][d5|d11][a7|a19][a12|a1:a19][a15|a19:d11][a20|a17:a28]
   [a21|a17:a18][d3|a19:d5][d14|d5][a5|a19:d3][a8|a1:a7][a11|a7:a15]
   [a16|a18:a21][a26|a15:a27][a29|a15][d1|d3:d13][d9|d3][a6|a8:a20][a23|a16:a18]
   [a24|a5][a25|a26][d4|a16:d3][d6|d1][a10|a9:a24][a13|a6][a14|a25][a22|a14]
  nodes:                                 44
  arcs:                                  66
    undirected arcs:                     0
    directed arcs:                       66
  average markov blanket size:           3.64
  average neighbourhood size:            3.00
  average branching factor:              1.50
  learning algorithm:                    Hill-Climbing
  score:                                 BIC (disc.)
  penalization coefficient:              3.707588
  tests used in the learning procedure:  3870
  optimized:                             TRUE
```

**Overall takeaway for Phase 1:** the pipeline works end-to-end and is
internally consistent (same BIC convention everywhere, sensible
parent-count patterns matching the paper's own structure), and the
remaining numeric differences from the paper's exact figures are
explained by known, reasonable causes (exact vs. greedy search;
full-dataset vs. 10-fold-cross-validation numbers) rather than bugs in
this reproduction.

## Discrepancies and best guesses why
- Overall split (23/68/9 mine vs. 43/50/7 paper) -- most likely explained
  by GOBNILP exact search vs. paper's `bnlearn` hill-climbing producing
  different structures (69 vs. 66 arcs, at least one confirmed reversed
  edge -- see Step 1.6).
- STD/MLR near-ties on 0- and 1-parent nodes are a mathematical
  equivalence, not a real discrepancy -- see the quirk section above.
- Total BIC magnitude (-64838 mine vs. ~-58500 to -59000 paper) -- likely
  explained by the paper's numbers coming from 10-fold cross-validation
  (90% of the data per fold) rather than the full dataset; unconfirmed,
  worth asking.
- `alpha`/`palim` in scoring2a (step 1.2) -- still unconfirmed by the paper
  or correspondence; the max-parent-count match above is a reassuring but
  not conclusive sign these were reasonable choices.

> **Correction (2026-11-15)** to this list:
> - *Split.* Part of the 23/68/9 vs 43/50/7 gap was the tie-breaking bug (see the correction
>   in Step 1.4). With the tie rule the existing numbers give 16/24/4 (36/55/9).
> - *BIC magnitude.* Confirmed by Jirka (Sep 28, 2026): Figure 4 comes from 10-fold
>   cross-validation.
> - *Paper's structure.* Confirmed by Jirka (Sep 28, 2026): "The model structure in the
>   Kybernetika paper was learnt using the hc procedure from the R package bnlearn."
>   So the paper never used scoring2a's alpha/palim for its structure. alpha = 1 is the true
>   BIC according to de Campos's note `scoring-how-to-use-it.txt`, and palim = 9 matches
>   Jirka's own example `script-data24-1`.

## Phase 1 status: COMPLETE

## Open questions (added 2026-11-15)

- **Possible inconsistency in the paper's text (unverified).** The old Phase 1 plan noted that
  the Kybernetika paper says "19 standard CPTs" and, in an adjacent sentence, "all 17 standard
  CPTs correspond to…". This hasn't been re-checked against the PDF (it isn't in the repo).
  Table 2 (`data/reference/kybernetika-table2.csv`) has 19 STD rows. Worth re-reading before
  quoting the paper; probably not worth an email question on its own.
