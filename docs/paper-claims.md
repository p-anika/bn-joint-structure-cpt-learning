# Paper claims

Every statement we might make in the paper, with a link to the report section that holds the
evidence. The numbers themselves live in the reports; this file only points to them.
Status: *draft* → *checked by Anika* → *agreed with Jirka*.

| # | Claim | Evidence | Status |
|---|---|---|---|
| 1 | On the Kybernetika data (44 variables, 1661 rows), the exact BIC-optimal structure with general tables (scoring2a, palim 9, + GOBNILP) has 69 arcs, at most 2 parents per node, and a proven-optimal BIC (gap 0 %). | [phase-1.md, "Step 1.3 result: GOBNILP structure search"](reports/phase-1.md#step-13-result-gobnilp-structure-search); regenerated unchanged in [1.5.0b.md](reports/1.5.0b.md#results) | draft |
| 2 | bnlearn hill-climbing with BIC (the paper's method) finds 66 arcs on the same data, a different structure from the exact optimum. | [phase-1.md, "Step 1.6 result"](reports/phase-1.md#step-16-result-bnlearn-hill-climbing-cross-check) | draft |
| 3 | bnlearn, scoring2a and our Python code use the same BIC penalty, log(N)/2 per parameter. | [phase-1.md, "Step 1.6 result"](reports/phase-1.md#step-16-result-bnlearn-hill-climbing-cross-check) | draft |
| 4 | With one parent, STD and MLR fit the same distribution and have the same parameter count, so their BICs are equal (up to rounding). | [phase-1.md, "An important quirk…"](reports/phase-1.md#an-important-quirk-i-noticed-std-and-mlr-sometimes-tie-exactly); [1.5.0a.md](reports/1.5.0a.md) | draft; proof to be written by Anika (step 1.5.1) |
| 5 | Our BN-data.csv is exactly the paper's data: Jirka's own conversion code (Aug 5, 2026 email) reproduces it byte for byte from his preprocessed survey file. | [1.5.0b.md, "Data verification"](reports/1.5.0b.md#data-verification) | draft |
| 6 | The whole Phase 1 pipeline is reproducible from the raw data with one command; a from-scratch rebuild reproduces every intermediate file byte for byte. | [1.5.0b.md, "Results"](reports/1.5.0b.md#results) | draft |

Claims not yet backed by a report section (do not use until they are): the corrected CPT-type
split 16/24/4 (step 1.5.1), "our fitting reproduces Table 2" (1.5.2), the two-stage BIC of the
GOBNILP structure and its comparison with hc (1.5.4).
