"""Read the survey data and write it in the format scoring2a expects.

Inputs:  `data/raw/BN-data.csv` (44 columns a1-a30, d1-d14; values -1, 0, 1; 1661 rows).
Outputs: `data/processed/bn-data-44.dat` and `data/processed/bn-data-44-varnames.txt`.
Run:     `python scripts/convert_data.py` (or `make phase-1`, which calls it).

The `.dat` format read by de Campos's scoring2a (see `docs/code-guide/scoring2a.md`):

    44                    <- number of variables
    3 3 3 ... 3           <- number of states of each variable
    1661                  <- number of rows
    2 0 1 0 2 ...         <- one row per line, states numbered 0, 1, 2

scoring2a needs states numbered from 0, so -1/0/1 are shifted to 0/1/2. The variable names
are not part of the `.dat` file; they are saved separately because GOBNILP's `.bnsl` header
needs them (`scripts/add_bnsl_header.sh`).
"""

from pathlib import Path

import pandas as pd

from bnjoint import config

# BN-data value -> scoring2a state index. Order is kept: -1 is the lowest state.
STATE_INDEX: dict[int, int] = {-1: 0, 0: 1, 1: 2}


def read_bn_data(path: Path) -> pd.DataFrame:
    """Read BN-data.csv into a DataFrame (one column per variable, integer values).

    Args:
        path: the CSV file, e.g. `config.BN_DATA_CSV`.

    Returns:
        DataFrame of shape (rows, variables).

    Example:
        >>> df = read_bn_data(config.BN_DATA_CSV)
        >>> df.shape
        (1661, 44)
    """
    return pd.read_csv(path)


def check_values(df: pd.DataFrame, allowed: tuple[int, ...] = config.DATA_VALUES) -> None:
    """Raise ValueError if the data contains any value other than `allowed`.

    Args:
        df: the data.
        allowed: the permitted values (default -1, 0, 1).

    Example:
        >>> check_values(pd.DataFrame({"a": [-1, 0, 1]}))   # passes silently
    """
    found = set(pd.unique(df.to_numpy().ravel()).tolist())
    extra = found - set(allowed)
    if extra:
        raise ValueError(
            f"Found values outside {set(allowed)}: {extra}. The paper (Sec. 4.1) and Jirka's "
            "conversion code both give 3 states; investigate before going on."
        )


def to_state_indices(df: pd.DataFrame) -> pd.DataFrame:
    """Shift values -1/0/1 to state numbers 0/1/2 (column by column).

    Example:
        >>> to_state_indices(pd.DataFrame({"a": [-1, 0, 1]}))["a"].tolist()
        [0, 1, 2]
    """
    return df.apply(lambda col: col.map(STATE_INDEX))


def dat_text(states: pd.DataFrame, k: int = config.K_STATES) -> str:
    """Return the full text of a scoring2a `.dat` file.

    Args:
        states: data already converted with `to_state_indices`.
        k: number of states of every variable (all variables here have 3).

    Returns:
        The file contents, ending in a newline.

    Example:
        >>> dat_text(pd.DataFrame({"a": [0, 2], "b": [1, 0]}))
        '2\\n3 3\\n2\\n0 1\\n2 0\\n'
    """
    n_rows, n_vars = states.shape
    lines = [str(n_vars), " ".join([str(k)] * n_vars), str(n_rows)]
    lines += [" ".join(str(int(v)) for v in row) for row in states.to_numpy()]
    return "\n".join(lines) + "\n"


def convert_bn_data(csv_path: Path, dat_path: Path, varnames_path: Path) -> pd.DataFrame:
    """Read BN-data.csv, check it, and write the `.dat` file and the variable-names file.

    The variable-names file is one line of space-separated names with **no** final newline
    (that is how the Phase 1 file was written, and it is pasted into the `.bnsl` header).

    Args:
        csv_path: input CSV (values -1/0/1).
        dat_path: where to write the scoring2a input.
        varnames_path: where to write the names.

    Returns:
        The data as read (values -1/0/1), for printing a summary.

    Example:
        >>> convert_bn_data(config.BN_DATA_CSV, Path("/tmp/x.dat"), Path("/tmp/n.txt")).shape
        (1661, 44)
    """
    df = read_bn_data(csv_path)
    check_values(df)
    # newline="\n": always write LF line endings, also on Windows
    with open(dat_path, "w", newline="\n") as f:
        f.write(dat_text(to_state_indices(df)))
    with open(varnames_path, "w", newline="\n") as f:
        f.write(" ".join(df.columns))
    return df
