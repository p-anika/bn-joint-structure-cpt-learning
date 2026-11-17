"""Tests for `bnjoint.structures`: reading an adjacency-matrix CSV and a typed-in reference
table, and comparing our per-node result with the reference node by node.

Run with `make test` (or `pytest tests/test_structures.py -v`). All examples are tiny and
made up, except the last test, which reads the real files of step 1.5.2.
"""

import pandas as pd
import pytest

from bnjoint import config
from bnjoint import structures as st


@pytest.fixture
def adj_csv(tmp_path):
    """A 3-node network a -> c <- b, written the way R's write.csv(amat(dag)) writes it:
    first column = row names (parents), header = children, 1 = arc."""
    path = tmp_path / "dag.csv"
    path.write_text('"","a","b","c"\n"a",0,0,1\n"b",0,0,1\n"c",0,0,0\n')
    return path


def test_read_adjacency_csv(adj_csv) -> None:
    assert st.read_adjacency_csv(adj_csv, ["a", "b", "c"]) == {"a": [], "b": [], "c": ["a", "b"]}


def test_read_adjacency_csv_rejects_wrong_names(adj_csv) -> None:
    with pytest.raises(ValueError):
        st.read_adjacency_csv(adj_csv, ["a", "b", "x"])


def test_read_reference_table(tmp_path) -> None:
    """Empty parents (a root node) must become [], not ['nan'] or ['']."""
    path = tmp_path / "ref.csv"
    path.write_text("variable,n_parents,parents,cpt_type\na,0,,STD\nc,2,a;b,MLR\n")
    ref = st.read_reference_table(path)
    assert ref == {"a": ([], "STD"), "c": (["a", "b"], "MLR")}


def test_read_reference_table_checks_n_parents(tmp_path) -> None:
    path = tmp_path / "ref.csv"
    path.write_text("variable,n_parents,parents,cpt_type\nc,1,a;b,MLR\n")
    with pytest.raises(ValueError):
        st.read_reference_table(path)


def test_compare_with_reference() -> None:
    """Parent ORDER does not matter (a;b equals b;a); a different set or type is flagged."""
    ours = pd.DataFrame(
        {"variable": ["a", "c", "d"], "parents": ["", "b;a", "a"], "winner": ["STD", "MLR", "OLR"]}
    )
    ref = {"a": ([], "STD"), "c": (["a", "b"], "MLR"), "d": (["b"], "STD")}
    cmp = st.compare_with_reference(ours, ref)
    assert cmp["same_parents"].tolist() == [True, True, False]
    assert cmp["same_type"].tolist() == [True, True, False]


def test_hc_structure_equals_table2() -> None:
    """Step 1.5.2 precondition: the bnlearn hc arcs are exactly the arcs of Table 2."""
    varnames = config.VARNAMES_FILE.read_text().split()
    hc = st.read_adjacency_csv(config.PHASE1_HC_DAG_CSV, varnames)
    ref = st.read_reference_table(config.KYBERNETIKA_TABLE2)
    assert list(ref) == varnames
    for v in varnames:
        assert set(hc[v]) == set(ref[v][0]), v
    assert sum(len(p) for p in hc.values()) == 66
