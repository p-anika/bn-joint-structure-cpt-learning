# Paper claims

Every statement we might make in the paper, with a link to the report section that holds the
evidence. Each claim keeps its numbers, because the claim is the sentence that will go into the
paper; the evidence and the full write-up live in the linked report.
Status: *draft* → *checked by Anika* → *agreed with Jirka*.

| # | Claim | Evidence | Status |
|---|---|---|---|
| 1 | On the Kybernetika data (44 variables, 1661 rows), the exact BIC-optimal structure with general tables (scoring2a, palim 9, + GOBNILP) has 69 arcs, at most 2 parents per node, and a proven-optimal BIC (gap 0 %). | [phase-1.md, "Exact structure (GOBNILP)"](../reports/phase-1.md#exact-structure-gobnilp); regenerated unchanged in [phase-1.5.md §1.5.0](../reports/phase-1.5.md#rebuild-from-the-raw-data) | draft |
| 2 | bnlearn hill-climbing with BIC (the paper's method) finds 66 arcs on the same data, a different structure from the exact optimum. | [phase-1.md, "Hill-climbing structure (bnlearn)"](../reports/phase-1.md#hill-climbing-structure-bnlearn) | draft |
| 3 | bnlearn, scoring2a and our Python code use the same BIC penalty, log(N)/2 per parameter. | [phase-1.md, "Hill-climbing structure (bnlearn)"](../reports/phase-1.md#hill-climbing-structure-bnlearn) | draft |
| 4 | With 0 or 1 parent (and no empty (parent, child) cell), STD and MLR describe the same set of distributions and have the same parameter count, so their BICs are equal (up to rounding; ≤ 6.8e-13 on our data). | [lemma and proof](../theory/one-parent-mlr-equals-std.md); [explainer](../explainers/one-parent-mlr-equals-std.md) (worked example); [phase-1.5.md, "1.5.1"](../reports/phase-1.5.md#151-gobnilp-structure) | draft. **Known fact (saturated model), not a contribution:** state as a remark with a textbook reference, still to be found and verified ([novelty note](../theory/one-parent-mlr-equals-std.md#novelty-a-known-fact-not-a-new-result)). Anika to write the proof in her own words |
| 5 | Our BN-data.csv is exactly the paper's data: Jirka's own conversion code (Aug 5, 2026 email) reproduces it byte for byte from his preprocessed survey file. | [phase-1.5.md §1.5.0](../reports/phase-1.5.md#150-data-and-reproducibility) | draft |
| 6 | The whole Phase 1 pipeline is reproducible from the raw data with one command; a from-scratch rebuild reproduces every intermediate file byte for byte. | [phase-1.5.md §1.5.0](../reports/phase-1.5.md#rebuild-from-the-raw-data) | draft |
| 7 | On the exact GOBNILP structure, the two-stage method (tie rule: within 1e-6, STD then OLR then MLR) chooses 16 STD, 24 MLR and 4 OLR tables; all MLR/OLR fits converged. | [phase-1.5.md, "1.5.1"](../reports/phase-1.5.md#151-gobnilp-structure) | draft |
| 8 | Our implementation reproduces the published model exactly: on the bnlearn hc structure (which equals Table 2's parent sets) it chooses the same CPT type as Table 2 for all 44 nodes (19/22/3). | [phase-1.5.md, "1.5.2"](../reports/phase-1.5.md#152-hc-structure-vs-table-2) | checked by Anika (2026-11-16) |

Claims not yet backed by a report section (do not use until they are): the two-stage BIC of
the GOBNILP structure and its comparison with hc (1.5.4).
