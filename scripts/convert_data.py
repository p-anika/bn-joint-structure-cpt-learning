"""Convert BN-data.csv into scoring2a's `.dat` format and save the variable names.

Inputs:  data/raw/BN-data.csv (values -1/0/1)
Outputs: data/processed/bn-data-44.dat, data/processed/bn-data-44-varnames.txt
Run:     python scripts/convert_data.py            (defaults below)
         python scripts/convert_data.py --csv X.csv --dat X.dat --varnames X-names.txt

All the logic is in `bnjoint.io` (`src/bnjoint/io.py`); this script only reads the
command-line arguments and prints a one-line summary.
"""

import argparse
from pathlib import Path

from bnjoint import config
from bnjoint.io import convert_bn_data


def main() -> None:
    """Parse arguments, convert, print a summary."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--csv", type=Path, default=config.BN_DATA_CSV, help="input CSV")
    parser.add_argument("--dat", type=Path, default=config.DAT_FILE, help="output .dat")
    parser.add_argument(
        "--varnames", type=Path, default=config.VARNAMES_FILE, help="output names file"
    )
    args = parser.parse_args()

    df = convert_bn_data(args.csv, args.dat, args.varnames)
    n_rows, n_vars = df.shape
    print(f"Wrote {args.dat} ({n_vars} variables, {n_rows} rows) and {args.varnames}")


if __name__ == "__main__":
    main()
