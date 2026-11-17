# Phase 1.5 report: checking the baseline

**Summary for Jirka.** We verified that our data is exactly the paper's data and that the whole
Phase 1 pipeline reproduces byte for byte from it. With a 1e-6 tie rule for the CPT-type choice,
the exact GOBNILP structure gets 16 standard / 24 MLR / 4 OLR tables, and all MLR/OLR fits
converge. On the bnlearn hill-climbing structure, whose parent sets equal Table 2's, our code
reproduces the published CPT types on all 44 nodes (19/22/3). So our fitting matches yours, and
the remaining differences come from the structure.

Status: steps 1.5.0–1.5.2 done (2026-11-15/16); 1.5.3–1.5.7 to come. Decisions: entries 12–15,
45 and 55–62 in `docs/decision-log.md`. Runs: `docs/experiment-log.md`. Repository work done in
the same phase (moves, package, Makefile): [infrastructure.md](infrastructure.md).

## 1.5.0 Data and reproducibility

**Goal:** be sure the data is the paper's, and that every Phase 1 number can be rebuilt from it.

| Check | Result |
|---|---|
| `BN-data.csv` is 1661 × 44, columns a1–a30, d1–d14, values in {−1, 0, 1} | **Pass**, no missing values (`tests/test_io.py`) |
| Jirka's Aug 5 R code (verbatim, `R/convert_jirka_aug5.R`) applied to `preprocessed-data.csv` reproduces `BN-data.csv` | **Pass**: 0 of 73,084 values differ, column names identical, and the output is **byte-identical** (same SHA-256) when written with CRLF line endings, as `BN-data.csv` is. Command: `make provenance`; record in `results/data-provenance/README.md` |
| Checksums of the originals | `data/raw/README.md`, `tools/*/README.md`, `data/reference/README.md` |

### Rebuild from the raw data

`make -B phase-1 PROCESSED=<scratch>/p OUT=<scratch>/r`, with every derived file deleted and
scoring2a recompiled, compared with the committed files. Done twice: on 2026-11-15 (after the
repository reorganization, 12 min 45 s) and on 2026-11-16 (after the Makefile change of step
1.5.1). Both times:

| File | Result |
|---|---|
| `data/processed/bn-data-44.dat`, `bn-data-44-varnames.txt`, `bn-data-44-bic.scores`, `bn-data-44-bic-fixed.bnsl` | byte-identical |
| `results/phase-1/gobnilp-std-run.log` | objective **−64837.738627**, gap 0.00 %; all 44 `child:-{…}` lines identical. Only timings differ, so the reported log is kept. |
| `results/phase-1/bnlearn-hc-dag.csv`, `adjmat.*`, `pdagadjmat.*` | byte-identical (the adjmat files also match the copies first committed on Sep 6, `fd2b479`) |

GOBNILP smoke test (`make test-data24`): objective **−3411.597651**, adjmat/pdagadjmat files
byte-identical to those first committed in `de88a7e`.

## 1.5.1: GOBNILP structure

**Goal:** fix the CPT-type choice (scores within 1e-6 are tied; ties go to STD, then OLR, then
MLR), check that every MLR and OLR fit converged, and re-run on the exact structure. Expected
split: 16 STD / 24 MLR / 4 OLR.

**What was done.** Tests first (`tests/test_cpt_scores.py`): MLR = STD for 0- and 1-parent
families (synthetic data, and all 18 such families of our structure); the tie rule picks STD over
a 1e-13 "win" (with the real a13 numbers); OLR beats MLR in a tie; the 1e-6 boundary; −∞
handling; convergence flags. Then `pick_winner` got the tolerance and order
(`config.TIE_TOLERANCE`, `config.TIE_ORDER`), MLR/OLR fits return statsmodels'
`mle_retvals["converged"]`, and the output CSV got the columns `parents`, `mlr_converged`,
`olr_converged` (decisions 55, 56). The regression tests now pin the BIC values to the numbers
reported in Phase 1 (decisions 58, 64).

**Results** (`results/phase-1.5/1.5.1-gobnilp-tie-fix/cpt-type-summary.csv`):

- **Split: 16 STD / 24 MLR / 4 OLR** (36 / 55 / 9 %), as expected.
- All three BIC columns are identical, to the last digit, to the CSV reported on Sep 7
  (`git show 9d80757:results/phase1/cpt-type-summary.csv`; test `test_scores_unchanged_from_phase1`).
  Only the winner rule changed.
- Exactly six winners changed, all MLR → STD; in each, MLR was "better" by 2.27e-13:

  | Node | Parents | BIC_STD | BIC_MLR − BIC_STD |
  |---|---|---|---|
  | a13 | a6 | −1583.719733998301 | 2.27e-13 |
  | a15 | d11 | −1585.6912713734384 | 2.27e-13 |
  | d6 | d1 | −1616.8639144069173 | 2.27e-13 |
  | d11 | (none) | −1816.2167982410447 | 2.27e-13 |
  | d12 | d7 | −1431.3744656508022 | 2.27e-13 |
  | d13 | d12 | −1524.9166516430732 | 2.27e-13 |

  The 1.5.0a audit had predicted the same six by re-reading the old scores.
- By number of parents: 0 parents 1 STD; 1 parent 15 STD + 2 OLR (d7, d10); 2 parents 24 MLR +
  2 OLR (a20, d8). Largest |BIC_STD − BIC_MLR| over all 0-/1-parent nodes: 4.5e-13.
- **Convergence: 44/44 MLR fits and 43/43 OLR fits converged** (d11 has no parents, so OLR is not
  fitted; `fit-log.txt`).

**Hand-check** (done by Anika, 2026-11-16): the STD BIC of a3 | a4 computed in a spreadsheet from
raw counts is −1142.50831, matching `bic_std` = −1142.5083085785432. Method: count table of
(a4, a3) (rows 1118/137/114, 58/61/30, 68/16/59), sum of count × ln(count / row total)
= −1120.26278, minus 6 × ln(1661)/2 = 22.24553.

## 1.5.2: hc structure vs. Table 2

**Goal:** fit the CPT types on the bnlearn hill-climbing structure, the method the paper used,
and compare node by node with Table 2 of [vomlel2026](../references.md#vomlel2026), p. 411
(`data/reference/kybernetika-table2.csv`). Expected: 19 STD / 22 MLR / 3 OLR, same type on every
node.

**What was done.** New module `bnjoint.structures` (reads bnlearn's adjacency matrix and Table 2;
compares parent *sets* and types per node), `fit_cpt_types.py --structure gobnilp|hc`, script
`compare_with_table2.py`, and the `make phase-1.5` target (decisions 57, 59, 60).

**Results** (`results/phase-1.5/1.5.2-hc-vs-table2/`):

- **Arcs first:** the hc structure (`results/phase-1/bnlearn-hc-dag.csv`, 66 arcs) has exactly
  Table 2's parent set on all 44 nodes (test `test_hc_structure_equals_table2`; `same_parents` is
  True on every row of `table2-comparison.csv`).
- **Split: 19 STD / 22 MLR / 3 OLR**, as in Table 2, with the **same CPT type on 44/44 nodes**
  (`table2-comparison.csv`, `comparison-log.txt`). The OLR nodes are a20 | a17, a28; d7 | a27;
  d8 | a28, as in the paper.
- By number of parents: 0 parents 1 STD (a3); 1 parent 18 STD + 2 OLR; 2 parents 22 MLR + 1 OLR.
- **Convergence: 44/44 MLR and 43/43 OLR fits converged** (`fit-log.txt`).
- So our fitting (MLR dummy-coded with −1 as reference, OLR with raw parent values, statsmodels,
  tie rule) reproduces the published model exactly. This is strong evidence for decision 8 (how
  OLR codes its parents).
- The paper's Section 4.3 says "17 standard CPTs", but Table 2 lists 19 and we reproduce 19
  ([phase-1.md](phase-1.md#comparison-with-the-paper)).

**Margins.** Every winner beats the runner-up by far more than 1e-6. The closest calls: d5 | d11
on the hc structure (STD beats OLR by 0.168) and a12 (MLR beats OLR by 0.332, both structures).
On every 1-parent node of the GOBNILP structure the margin is at least 1.01 (a29). Any tolerance
between about 1e-12 and 0.1 gives the same winners.

## What we tried that didn't work

- **Keeping the old regression test** (1.5.1). It required the new CSV to be byte-identical to
  the Phase 1 CSV, which had to fail once the winner rule changed on purpose. Replaced by
  stricter tests that pin the BIC values and allow exactly the six expected winner changes
  (decision 58).
- **Listing the Phase 1 structures as Make prerequisites of `phase-1.5`** (1.5.2). A dry run
  showed that, after a fresh checkout, this would rebuild the whole Phase 1 chain and rewrite the
  reported GOBNILP log. They are read without being prerequisites (decision 60).
- **Checking the "17 standard CPTs" sentence by machine.** No PDF text tool is installed; Anika
  checked it by hand.
- **Reconstructing Jirka's R conversion from its description** (1.5.0). Replaced by his verbatim
  code from the Aug 5 email, which reproduces `BN-data.csv` byte for byte (decision 45).

## Surprises

- None in the numbers: every expected result came out exactly.
- In the hc structure the arc between a3 and a4 points the other way (a3 is the root, a4 | a3),
  so the hand-check family a3 | a4 exists only in the GOBNILP structure.
- Jirka's files have Windows (CRLF) line endings. No number is affected (pandas and R read them;
  scoring2a reads our LF `.dat`), but it is why `.gitattributes` exempts the originals
  ([infrastructure.md](infrastructure.md)).

## History

No number reported in this phase has changed.

## Open questions

- **For Jirka (Email #3): OLR parent coding.** Our OLR uses the parents' raw values −1/0/1 with
  one slope each (decision 8). The exact Table 2 match supports this, and so does the paper's
  Example 3.2 (parent values enter the linear term directly; a shift of the values is absorbed
  by the cut-points; [reading note](../reading-notes/vomlel2026.md)), but Jirka has not
  confirmed it.
- **To watch in Phase 2: the absolute 1e-6 tolerance.** Fine for BICs of order 10³ with rounding
  noise of 10⁻¹³. In Phase 2 (thousands of families, some with zero-count cells where MLR cannot
  converge exactly) check the convergence flags and the STD−MLR gaps of 0-/1-parent families
  before relying on it.
- The "17 vs 19 standard CPTs" inconsistency in the paper: mention it to Jirka? It affects no
  result.

## Riskiest assumptions in the code

1. **OLR parent coding** (above).
2. **The absolute 1e-6 tolerance** (above): a non-converged MLR could fall just outside 1e-6
   below STD. It would then lose correctly, but the flag must be watched.
3. **statsmodels' convergence flag is trusted as is.** For BFGS (OLR) it means the gradient norm
   fell below statsmodels' default threshold within the default iteration limit; we do not
   re-check the gradient ourselves.
