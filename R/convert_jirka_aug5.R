# Check that BN-data.csv is exactly Jirka's conversion of preprocessed-data.csv.
#
# The conversion code below is copied VERBATIM from Jirka's email of Aug 5, 2026 (between the
# "verbatim" markers). Only the reading, the comparison and the writing around it are ours.
# We do NOT use its output for analysis: Jirka asked us to use BN-data.csv directly so both of
# us work with identical data (decision log entry 2). This script only confirms the provenance.
#
# Input:  data/raw/preprocessed-data.csv (1-7 scale, 72 columns), data/raw/BN-data.csv
# Output: scratch/provenance/BN-data-from-jirka-code.csv (git-ignored scratch; never committed,
#         CLAUDE.md), and a printed PASS/FAIL. The sha256 match is recorded in
#         results/data-provenance/README.md.
# Run:    Rscript R/convert_jirka_aug5.R          (or: make provenance)

args <- commandArgs(trailingOnly = TRUE)
pre_csv <- if (length(args) >= 1) args[1] else "data/raw/preprocessed-data.csv"
bn_csv  <- if (length(args) >= 2) args[2] else "data/raw/BN-data.csv"
out_csv <- if (length(args) >= 3) args[3] else "scratch/provenance/BN-data-from-jirka-code.csv"

d <- read.csv(pre_csv)   # Jirka's email: d is read from preprocessed-data.csv

# ---- verbatim from Jirka's Aug 5, 2026 email ----
# Data conversions:
# - select only "a*" and "d*" variables
vars <- colnames(d)[29:72]
other.vars <- colnames(d)[1:28]
# - convert states 1,..,7 to -1,0,+1
states.conversion <- function(v){
 ret <- 0
 if (v < 4){
     ret <- -1
 }else{
     if (v > 4){
         ret <- 1
     }
 }
 return(ret)
}
d.vars <- d[,vars]
d.three <- sapply(d.vars,FUN=as.numeric)
d.three[] <- vapply(d.three[],FUN=states.conversion,numeric(1))
# ---- end of verbatim code ----

# d.three is a numeric matrix; compare it value by value with BN-data.csv
b <- read.csv(bn_csv)
same_names <- identical(colnames(d.three), colnames(b))
n_diff <- sum(d.three != as.matrix(b))
cat("dimensions:", dim(d.three), "vs BN-data.csv", dim(b), "\n")
cat("column names identical:", same_names, "\n")
cat("values that differ:", n_diff, "of", length(d.three), "\n")

# Write it the way BN-data.csv is stored (no quotes, no row names, CRLF line endings), so the
# Makefile can also compare the two files byte for byte.
dir.create(dirname(out_csv), showWarnings = FALSE, recursive = TRUE)
write.table(d.three, out_csv, sep = ",", quote = FALSE, row.names = FALSE, eol = "\r\n")
cat(if (same_names && n_diff == 0) "PASS" else "FAIL", "\n")
