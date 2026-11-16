# Experiment log

One row per run that produced a number. **Commit** is the commit whose code and data produced
the number. A row is never edited after the number has been reported; mistakes get a new row
or a dated note.

Phase 1 runs (Sep 2026) are backfilled in step 1.5.0b, from `docs/reports/phase-1.md` and the
git history.

| Date | Commit | Exact command | Inputs | Output folder | Headline result | Notes |
|---|---|---|---|---|---|---|
| 2026-11-15 | `6a38593` | Inline Python check; the full snippet is in `docs/reports/1.5.0a.md` ("How the split was checked") | `results/cpt-type-summary.csv` | none (printed only) | Re-applying the tie rule (within 1e-6; STD, then OLR, then MLR) to the existing scores gives **16 STD / 24 MLR / 4 OLR**. Six nodes change MLR → STD: a13, a15, d6, d11, d12, d13. Largest STD−MLR gap among tied nodes: 4.5e-13. | A re-reading of existing numbers, not a new fit. The official corrected split comes from re-running the fixed script in step 1.5.1. |
