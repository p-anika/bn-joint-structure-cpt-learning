"""Tests for `bnjoint.io`: reading BN-data.csv and writing scoring2a's `.dat` format."""

import pandas as pd
import pytest

from bnjoint import config, io


def test_bn_data_shape_columns_values() -> None:
    """BN-data.csv: 1661 rows x 44 columns a1-a30, d1-d14, every value in {-1, 0, 1}."""
    df = io.read_bn_data(config.BN_DATA_CSV)
    assert df.shape == (1661, 44)
    assert list(df.columns) == [f"a{i}" for i in range(1, 31)] + [f"d{i}" for i in range(1, 15)]
    assert set(pd.unique(df.to_numpy().ravel())) <= {-1, 0, 1}
    assert not df.isna().any().any()


def test_check_values_rejects_other_values() -> None:
    with pytest.raises(ValueError, match="outside"):
        io.check_values(pd.DataFrame({"a": [-1, 0, 2]}))


def test_to_state_indices() -> None:
    """-1/0/1 become 0/1/2 (scoring2a wants states numbered from 0)."""
    df = pd.DataFrame({"a": [-1, 0, 1], "b": [1, 1, -1]})
    out = io.to_state_indices(df)
    assert out["a"].tolist() == [0, 1, 2]
    assert out["b"].tolist() == [2, 2, 0]


def test_dat_text_format() -> None:
    """Line 1: number of variables; line 2: arities; line 3: number of rows; then the rows."""
    df = pd.DataFrame({"a": [0, 2], "b": [1, 0]})
    assert io.dat_text(df, k=3) == "2\n3 3\n2\n0 1\n2 0\n"


def test_regenerates_committed_dat_and_varnames(tmp_path) -> None:
    """The package reproduces data/processed/bn-data-44.dat and the varnames file byte for byte."""
    dat, names = tmp_path / "x.dat", tmp_path / "names.txt"
    io.convert_bn_data(config.BN_DATA_CSV, dat, names)
    assert dat.read_bytes() == config.DAT_FILE.read_bytes()
    assert names.read_bytes() == config.VARNAMES_FILE.read_bytes()
