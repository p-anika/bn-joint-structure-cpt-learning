# Makefile: one command per pipeline stage. Run from the repo root, e.g. `make phase-1`.
#
# How make works (short version): each rule says "to build TARGET, first make sure the
# PREREQUISITES exist, then run these commands". make only re-runs a rule when a prerequisite
# is newer than the target, so a second `make phase-1` does nothing unless something changed.
# `make -B phase-1` forces everything to be rebuilt. Walkthrough: docs/code-guide/ARCHITECTURE.md.
#
# Output folders can be redirected, which is how the reorganization was checked without
# overwriting the reported files:
#   make phase-1 PROCESSED=/tmp/check/processed OUT=/tmp/check/phase-1

SHELL := /bin/bash
.SHELLFLAGS := -o pipefail -c   # a pipeline (cmd | tee log) fails if cmd fails, not only tee
.DEFAULT_GOAL := help

# (Comments go on their own line: in make, spaces before a trailing # become part of the value.)
PYTHON    ?= .venv/bin/python
# gobnilp is on the PATH via ~/.local/bin (docs/setup.md section 7c)
GOBNILP   ?= gobnilp
CXX       ?= g++

# derived data files / Phase 1 results / GOBNILP smoke-test results
PROCESSED ?= data/processed
OUT       ?= results/phase-1
OUT24     ?= results/test-data24
# Phase 1.5 results, one folder per experiment (results/phase-1.5/README.md)
OUT15     ?= results/phase-1.5

# scoring2a settings (decision log entry 5): alpha = 1 (true BIC), palim = 9, prune, score bic
ALPHA := 1
PALIM := 9

RAW       := data/raw
SCORING2A := tools/scoring2a/scoring2a
GOB_SET   := $(abspath tools/gobnilp/gobnilp.set)

DAT       := $(PROCESSED)/bn-data-44.dat
VARNAMES  := $(PROCESSED)/bn-data-44-varnames.txt
SCORES    := $(PROCESSED)/bn-data-44-bic.scores
BNSL      := $(PROCESSED)/bn-data-44-bic-fixed.bnsl
GOB_LOG   := $(OUT)/gobnilp-std-run.log
HC_CSV    := $(OUT)/bnlearn-hc-dag.csv
BNSL24    := $(PROCESSED)/data24-training-1-bic-fixed.bnsl

# Phase 1.5 outputs (fitting code: scripts/fit_cpt_types.py + src/bnjoint/)
FIT_DEPS  := $(RAW)/BN-data.csv $(VARNAMES) scripts/fit_cpt_types.py src/bnjoint/cpt_scores.py src/bnjoint/config.py
CPT151    := $(OUT15)/1.5.1-gobnilp-tie-fix/cpt-type-summary.csv
CPT152    := $(OUT15)/1.5.2-hc-vs-table2/cpt-type-summary-hc.csv
CMP152    := $(OUT15)/1.5.2-hc-vs-table2/table2-comparison.csv
TABLE2    := data/reference/kybernetika-table2.csv

.PHONY: help phase-1 phase-1.5 test-data24 provenance scoring2a test lint format inventory

help:   ## list the targets
	@grep -E '^[a-z0-9.-]+:.*##' $(MAKEFILE_LIST) | sed -E 's/:.*## /\t/'

# ---------------------------------------------------------------- tools
scoring2a: $(SCORING2A)   ## build de Campos's scoring program from source
# $@ = the target, $< = the first prerequisite (the compile command is from de Campos's note)
$(SCORING2A): tools/scoring2a/scoring2a.c
	$(CXX) -O2 -o $@ $< -lm

# ---------------------------------------------------------------- Phase 1
# The CPT types on these structures are made by `make phase-1.5` (results/phase-1.5/), so this
# target only makes the structures.
phase-1: $(GOB_LOG) $(HC_CSV)   ## Phase 1 structures: scores, GOBNILP, hc (~20 min from scratch)
	@grep "objective value" $(GOB_LOG)

# 1. BN-data.csv -> scoring2a's .dat format + names file (one rule makes both files)
$(DAT) $(VARNAMES) &: $(RAW)/BN-data.csv scripts/convert_data.py src/bnjoint/io.py
	@mkdir -p $(PROCESSED)
	$(PYTHON) scripts/convert_data.py --csv $< --dat $(DAT) --varnames $(VARNAMES)

# 2. local BIC scores of every candidate parent set (the slow step, ~15 min)
$(SCORES): $(DAT) $(SCORING2A)
	$(SCORING2A) $(DAT) $(ALPHA) $(PALIM) prune 0 bic > $@

# 3. add the header GOBNILP needs (variable names + "SCORES START")
$(BNSL): $(SCORES) $(VARNAMES) scripts/add_bnsl_header.sh
	scripts/add_bnsl_header.sh $(SCORES) $@ $$(cat $(VARNAMES))

# 4. exact structure search. GOBNILP writes adjmat.* and pdagadjmat.* (the DAG and its
#    CPDAG) into the folder it runs in, so it runs inside $(OUT).
$(GOB_LOG): $(BNSL) tools/gobnilp/gobnilp.set
	@mkdir -p $(OUT)
	cd $(OUT) && $(GOBNILP) -f $(abspath $(BNSL)) -s $(GOB_SET) | tee $(notdir $@)

# 6. bnlearn hill-climbing structure, for comparison
$(HC_CSV): $(RAW)/BN-data.csv R/bnlearn_hc.R
	@mkdir -p $(OUT)
	Rscript R/bnlearn_hc.R $(RAW)/BN-data.csv $@

# ---------------------------------------------------------------- Phase 1.5
phase-1.5: $(CPT151) $(CMP152)   ## CPT types with the tie rule: GOBNILP (1.5.1) and hc vs Table 2 (1.5.2)

# The Phase 1 structures (GOBNILP log, hc adjacency CSV) are READ but deliberately NOT listed as
# prerequisites: listing them would let make rebuild them (and so rewrite results/phase-1/, the
# record of what was reported to Jirka) whenever a file further up the chain looks newer.
#
# 1.5.1: CPT types on the GOBNILP structure. tee keeps the console output (split and
# convergence report) next to the CSV as fit-log.txt.
$(CPT151): $(FIT_DEPS) src/bnjoint/gobnilp_io.py
	@mkdir -p $(dir $@)
	$(PYTHON) scripts/fit_cpt_types.py --structure gobnilp --structure-file $(GOB_LOG) \
	  --varnames $(VARNAMES) --out $@ | tee $(dir $@)fit-log.txt

# 1.5.2: CPT types on the hill-climbing structure, then the comparison with Table 2
$(CPT152): $(FIT_DEPS) src/bnjoint/structures.py
	@mkdir -p $(dir $@)
	$(PYTHON) scripts/fit_cpt_types.py --structure hc --structure-file $(HC_CSV) \
	  --varnames $(VARNAMES) --out $@ | tee $(dir $@)fit-log.txt

$(CMP152): $(CPT152) $(TABLE2) scripts/compare_with_table2.py src/bnjoint/structures.py
	$(PYTHON) scripts/compare_with_table2.py --ours $(CPT152) --reference $(TABLE2) --out $@ \
	  | tee $(dir $@)comparison-log.txt

# ---------------------------------------------------------------- checks
test-data24:   ## GOBNILP smoke test on Jirka's 23-variable example (seconds)
	@mkdir -p $(PROCESSED) $(OUT24)
	scripts/add_bnsl_header.sh $(RAW)/data24-training-1-bic.scores $(BNSL24) $$(seq 0 22)
	cd $(OUT24) && $(GOBNILP) -f $(abspath $(BNSL24)) -s $(GOB_SET) | tee gobnilp-data24.log
	@grep "objective value" $(OUT24)/gobnilp-data24.log

# The rebuilt copy goes to scratch/ (git-ignored): a regenerated copy of a data file is never
# committed (CLAUDE.md). Only the checksum comparison is recorded, in results/data-provenance/.
PROV_CSV := scratch/provenance/BN-data-from-jirka-code.csv
provenance:   ## re-run Jirka's Aug 5 R conversion and compare with BN-data.csv (sha256)
	Rscript R/convert_jirka_aug5.R $(RAW)/preprocessed-data.csv $(RAW)/BN-data.csv $(PROV_CSV)
	sha256sum $(PROV_CSV) $(RAW)/BN-data.csv
	cmp $(PROV_CSV) $(RAW)/BN-data.csv && echo "byte-identical"

test:   ## run all tests
	$(PYTHON) -m pytest

lint:   ## check style and formatting (changes nothing)
	$(PYTHON) -m ruff check src scripts tests
	$(PYTHON) -m ruff format --check src scripts tests

format:   ## reformat Python files in place
	$(PYTHON) -m ruff format src scripts tests

inventory:   ## list tracked files not mentioned in their folder's README
	$(PYTHON) scripts/check_inventory.py
