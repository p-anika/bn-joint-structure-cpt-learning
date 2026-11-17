# Explainers: reading order for a beginner

Each explainer covers one concept: definition, why it matters here, a worked example with our
data, where it is in the code, common confusions, and questions with answers.

| # | Explainer | Status |
|---|---|---|
| 00 | [The repo's tools: Make, package, tests, ruff, line endings, checksums](00-repo-tools.md) | written (1.5.0b) |
| 01 | Bayesian networks | planned, step 1.5.7 |
| 02 | BIC | planned, step 1.5.7 |
| 03 | [The three CPT types: STD, MLR, OLR](03-cpt-types.md) | written (1.5.1) |
| 04 | [Why one-parent MLR and STD are the same model (and the tie rule)](04-one-parent-mlr-equals-std.md) | written (1.5.1) |
| 05 | GOBNILP and exact search | planned, step 1.5.7 |
| 06–10 | CPDAGs; pruning; non-monotone joint score; our pruning rules; running the pipeline | planned (research plan) |

Until 01, 02 and 05 exist, the closest material is `docs/code-guide/` and
`docs/reports/phase-1.md`. Explainers 03 and 04 were written before 01–02 because step 1.5.1
needed them; read 01–02 first once they exist. (Numbering changed 2026-11-16: the planned
GOBNILP explainer moved from 04 to 05; decision log entry 61.)
