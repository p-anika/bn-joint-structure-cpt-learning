"""Regression tests for the CPT-type results (Phase 1 and steps 1.5.1, 1.5.2).

Three questions, each answered by comparing with a saved, reported file:

1. Did the scores stay the same? Step 1.5.1 changed only the WINNER rule, so the three BIC
   columns must equal those of `results/phase1/cpt-type-summary.csv` (reported to Jirka on
   Sep 7, 2026) exactly, to the last digit.
2. Did exactly the expected winners change? The tie rule turns the six nodes where MLR won by
   rounding noise (~1e-13) into STD: 10/30/4 becomes 16/24/4 (STD/MLR/OLR).
3. Does the code still produce the saved step-1.5.1 and step-1.5.2 CSVs byte for byte, and
   does the hc result match Table 2 of the paper (19/22/3, same type on every node)?

If a test fails, a code change altered a number: stop and investigate, never edit the CSVs.
Takes about 30-40 seconds (about 175 logistic-regression fits).
"""

import pandas as pd
import pytest

from bnjoint import config
from bnjoint import structures as st
from bnjoint.cpt_scores import fit_cpt_types
from bnjoint.gobnilp_io import parse_parent_sets
from bnjoint.io import read_bn_data

SCORE_COLUMNS = ["variable", "n_parents", "bic_std", "bic_mlr", "bic_olr"]
FLIPPED_BY_TIE_RULE = ["a13", "a15", "d6", "d11", "d12", "d13"]  # MLR -> STD


@pytest.fixture(scope="module")
def data() -> tuple[pd.DataFrame, list[str]]:
    return read_bn_data(config.BN_DATA_CSV), config.VARNAMES_FILE.read_text().split()


@pytest.fixture(scope="module")
def gobnilp_summary(data) -> pd.DataFrame:
    """CPT types on the Phase 1 GOBNILP structure, computed now by the current code."""
    df, varnames = data
    parents = parse_parent_sets(config.PHASE1_GOBNILP_LOG.read_text(), varnames)
    return fit_cpt_types(df, parents, varnames)


@pytest.fixture(scope="module")
def hc_summary(data) -> pd.DataFrame:
    """CPT types on the bnlearn hill-climbing structure, computed now by the current code."""
    df, varnames = data
    parents = st.read_adjacency_csv(config.PHASE1_HC_DAG_CSV, varnames)
    return fit_cpt_types(df, parents, varnames)


def _read_exact(path) -> pd.DataFrame:
    # "round_trip" parses each number to exactly the float that was written (the default
    # parser may be off in the last bit, which would make an exact comparison fail wrongly)
    return pd.read_csv(path, float_precision="round_trip", keep_default_na=False)


def test_scores_unchanged_from_phase1(gobnilp_summary) -> None:
    old = _read_exact(config.PHASE1_CPT_SUMMARY)
    new = gobnilp_summary[SCORE_COLUMNS]
    pd.testing.assert_frame_equal(new, old[SCORE_COLUMNS].astype(new.dtypes), check_exact=True)


def test_tie_rule_changes_exactly_six_winners(gobnilp_summary) -> None:
    old = _read_exact(config.PHASE1_CPT_SUMMARY)
    changed = gobnilp_summary["winner"] != old["winner"]
    assert gobnilp_summary.loc[changed, "variable"].tolist() == FLIPPED_BY_TIE_RULE
    assert (old.loc[changed, "winner"] == "MLR").all()
    assert (gobnilp_summary.loc[changed, "winner"] == "STD").all()


def test_gobnilp_split_16_24_4(gobnilp_summary) -> None:
    assert gobnilp_summary["winner"].value_counts().to_dict() == {"MLR": 24, "STD": 16, "OLR": 4}


def test_all_fits_converged(gobnilp_summary, hc_summary) -> None:
    """Every MLR and OLR fit on both structures converged (OLR of a root node is not fitted)."""
    for summary in (gobnilp_summary, hc_summary):
        assert summary["mlr_converged"].eq(True).all()
        olr = summary.loc[summary["n_parents"] > 0, "olr_converged"]
        assert olr.eq(True).all()


def test_gobnilp_output_file_reproduced(gobnilp_summary, tmp_path) -> None:
    out = tmp_path / "cpt.csv"
    gobnilp_summary.to_csv(out, index=False)
    assert out.read_bytes() == config.STEP151_CPT_SUMMARY.read_bytes()


def test_hc_matches_kybernetika_table2(hc_summary) -> None:
    """Step 1.5.2: same parent set AND same CPT type for all 44 nodes; split 19/22/3."""
    ref = st.read_reference_table(config.KYBERNETIKA_TABLE2)
    cmp = st.compare_with_reference(hc_summary, ref)
    assert cmp["same_parents"].all()
    assert cmp[~cmp["same_type"]]["variable"].tolist() == []
    assert hc_summary["winner"].value_counts().to_dict() == {"MLR": 22, "STD": 19, "OLR": 3}


def test_hc_output_file_reproduced(hc_summary, tmp_path) -> None:
    out = tmp_path / "cpt.csv"
    hc_summary.to_csv(out, index=False)
    assert out.read_bytes() == config.STEP152_CPT_SUMMARY.read_bytes()
