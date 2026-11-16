"""Regression test: the refactored code reproduces the reported Phase 1 CPT-type table exactly.

`results/phase1/cpt-type-summary.csv` was made on Sep 6, 2026 by the old single-file
`scripts/fit_cpt_types.py` and reported to Jirka. After moving the code into `src/bnjoint/`
(step 1.5.0b) the same inputs must give the same file, byte for byte. If this test fails,
the refactor changed a number: stop and investigate, do not edit the CSV.

Takes about 10-20 seconds (88 logistic-regression fits).
"""

from bnjoint import config
from bnjoint.cpt_scores import fit_cpt_types
from bnjoint.gobnilp_io import parse_parent_sets
from bnjoint.io import read_bn_data


def test_cpt_type_summary_unchanged(tmp_path) -> None:
    df = read_bn_data(config.BN_DATA_CSV)
    varnames = config.VARNAMES_FILE.read_text().split()
    parents = parse_parent_sets(config.PHASE1_GOBNILP_LOG.read_text(), varnames)

    out = tmp_path / "cpt-type-summary.csv"
    fit_cpt_types(df, parents, varnames).to_csv(out, index=False)

    assert out.read_bytes() == config.PHASE1_CPT_SUMMARY.read_bytes()
