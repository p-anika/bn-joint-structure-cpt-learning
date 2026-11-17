# Learn a network structure with bnlearn's hill-climbing (hc) and BIC, like the Kybernetika
# paper did (Jirka, Sep 28 email; decision log entries 10 and 19).
# References: bnlearn = docs/references.md#scutari2010; the paper = docs/references.md#vomlel2026.
#
# Input:  data/raw/BN-data.csv (values -1/0/1; each column is treated as a 3-level factor)
# Output: an adjacency matrix CSV: row = parent, column = child, 1 = arc
#         (default results/phase-1/bnlearn-hc-dag.csv); the model is also printed.
# Run:    Rscript R/bnlearn_hc.R                         (defaults)
#         Rscript R/bnlearn_hc.R <data.csv> <out.csv>
#
# hc is a greedy search, so the random seed is fixed to make the run repeatable.

library(bnlearn)

args <- commandArgs(trailingOnly = TRUE)       # arguments after the script name
data_csv <- if (length(args) >= 1) args[1] else "data/raw/BN-data.csv"
out_csv  <- if (length(args) >= 2) args[2] else "results/phase-1/bnlearn-hc-dag.csv"

set.seed(1)
d <- read.csv(data_csv)
d[] <- lapply(d, as.factor)    # bnlearn needs factors (categories) for a discrete network
dag <- hc(d, score = "bic")    # all other hc settings at their defaults
print(dag)
write.csv(amat(dag), out_csv)  # amat() = adjacency matrix
