"""Tests for `bnjoint.gobnilp_io`: reading learned parent sets out of a GOBNILP console log.

The sample lines are copied from `results/phase-1/gobnilp-std-run.log`.
"""

import pytest

from bnjoint import config
from bnjoint.gobnilp_io import parse_parent_sets

SAMPLE_LOG = """\
objective value:                        -64837.738627
a1:-{a19,a27}                                       1 \t(obj:-1410.601461)
a3:-{a4}                                            1 \t(obj:-1142.508309)
d11:-{}                                             1 \t(obj:-1816.216798)
a1:-a19                                             1 \t(obj:0)
a1:-a27                                             1 \t(obj:0)
"""


def test_parses_families_including_empty_parent_set() -> None:
    parents = parse_parent_sets(SAMPLE_LOG, ["a1", "a3", "d11"])
    assert parents == {"a1": ["a19", "a27"], "a3": ["a4"], "d11": []}


def test_arc_lines_are_ignored() -> None:
    """Lines like `a1:-a19 ... (obj:0)` describe single arcs, not families; they must not
    overwrite the family `a1:-{a19,a27}`."""
    parents = parse_parent_sets(SAMPLE_LOG, ["a1", "a3", "d11"])
    assert parents["a1"] == ["a19", "a27"]


def test_variable_missing_from_log_raises() -> None:
    with pytest.raises(ValueError, match="d14"):
        parse_parent_sets(SAMPLE_LOG, ["a1", "a3", "d11", "d14"])


def test_unknown_variable_in_log_raises() -> None:
    with pytest.raises(ValueError, match="d11"):
        parse_parent_sets(SAMPLE_LOG, ["a1", "a3"])


def test_gobnilp_log_has_69_arcs() -> None:
    """The Phase 1 structure has 44 families and 69 arcs (docs/reports/phase-1.md)."""
    text = config.PHASE1_GOBNILP_LOG.read_text()
    varnames = config.VARNAMES_FILE.read_text().split()
    parents = parse_parent_sets(text, varnames)
    assert len(parents) == 44
    assert sum(len(p) for p in parents.values()) == 69
