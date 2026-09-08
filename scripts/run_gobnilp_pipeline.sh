#!/bin/bash
# Reproduces Phase 1 steps 1.2 and 1.3: local BIC scoring, then GOBNILP's
# exact structure search. Run from the project root, e.g.:
#   bash scripts/run_gobnilp_pipeline.sh
set -e  # stop immediately if any step fails

# ---- 1.2: score every candidate family with scoring2a ----
cd src
./scoring2a ../data/bn-data-44.dat 1 9 prune 0 bic > ../data/bn-data-44-bic.scores
cd ..

# ---- 1.3: add the GOBNILP header, then run the exact structure search ----
VARNAMES=$(cat data/bn-data-44-varnames.txt)
scripts/add_bnsl_header.sh data/bn-data-44-bic.scores data/bn-data-44-bic-fixed.bnsl $VARNAMES

cd src
cp ../data/bn-data-44-bic-fixed.bnsl .
gobnilp -f bn-data-44-bic-fixed.bnsl -s gobnilp.set | tee ../results/gobnilp-std-run.log
cd ..

echo "Done. Structure is in results/gobnilp-std-run.log"
