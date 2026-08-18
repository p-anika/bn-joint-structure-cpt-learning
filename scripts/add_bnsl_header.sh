#!/bin/bash
# Usage: ./add_bnsl_header.sh input.scores output.bnsl var1 var2 var3 ...
input="$1"
output="$2"
shift 2
echo "$@" > "$output"
echo "SCORES START" >> "$output"
cat "$input" >> "$output"
