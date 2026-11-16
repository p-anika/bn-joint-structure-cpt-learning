#!/bin/bash
# Add the two header lines this GOBNILP version needs in front of a scoring2a .scores file.
#
# Usage:  scripts/add_bnsl_header.sh input.scores output.bnsl var1 var2 var3 ...
# Example (what `make phase1` runs):
#   scripts/add_bnsl_header.sh data/processed/bn-data-44-bic.scores \
#       data/processed/bn-data-44-bic-fixed.bnsl $(cat data/processed/bn-data-44-varnames.txt)
#
# The output is:  line 1 = the variable names, line 2 = "SCORES START", then the input unchanged.
# Why: GOBNILP's reader looks for "SCORES START" (docs/setup.md section 8).
input="$1"      # $1 = first argument
output="$2"     # $2 = second argument
shift 2         # drop the first two arguments; "$@" is now just the variable names
echo "$@" > "$output"            # >  creates/overwrites the file
echo "SCORES START" >> "$output" # >> appends
cat "$input" >> "$output"
