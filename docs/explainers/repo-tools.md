# The repo's tools: Make, a Python package, tests, ruff, line endings, checksums

Terms used here (one-line definitions in the glossary): [GOBNILP](../glossary.md#gobnilp), [scoring2a](../glossary.md#scoring2a), [CPT](../glossary.md#cpt), [STD](../glossary.md#std), [MLR](../glossary.md#mlr), [OLR](../glossary.md#olr).

## 1. Plain-words definitions

- **Make** reads a `Makefile` of *rules*: "to build this file, these files must exist first,
  then run these commands". Typing `make phase-1` builds everything Phase 1 needs, in the right
  order, and skips steps whose inputs haven't changed.
- **A Python package** is a folder of `.py` files with an `__init__.py`, which other code can
  `import`. Ours is `src/bnjoint/`. An **editable install** (`pip install -e .`) tells Python
  "the package `bnjoint` is that folder", so edits take effect immediately.
- **pytest** runs every function named `test_…` in `tests/` and reports which `assert`
  statements failed. A **regression test** checks that a result we already reported has not
  changed.
- **ruff** checks Python code for mistakes and style (`ruff check`) and formats it
  consistently (`ruff format`).
- **Line endings**: the invisible character(s) at the end of each line of a text file. Linux
  uses LF (`\n`), Windows CR + LF (`\r\n`). Programs written for Linux can read a stray `\r`
  as part of the last value on a line.
- **SHA-256 checksum**: a 64-character fingerprint computed from a file's bytes. Same bytes,
  same checksum; change one byte and the checksum is completely different.

## 2. Why it matters here

- Two commands (`make phase-1`, then `make phase-1.5`) reproduce every Phase 1 and 1.5 number, so
  anyone, including Jirka, can check them.
- The STD/MLR/OLR math is used again in every later phase; as a tested package, it can't
  silently drift.
- The regression test is how step 1.5.0b proved the reorganization changed no number.
- Jirka's files have Windows line endings; we keep them exactly as received, and the
  checksums in `data/raw/README.md` prove they are untouched.

## 3. Worked example with our data

- `make phase-1` on a fresh checkout: Make sees that `results/phase-1/gobnilp-std-run.log` needs
  `bn-data-44-bic-fixed.bnsl`, which needs `bn-data-44-bic.scores`, which needs
  `bn-data-44.dat` (and the scoring2a program), which needs `data/raw/BN-data.csv`. It runs
  those steps in that order. Run it again and it does nothing, because every output is newer
  than its inputs.
- `BN-data.csv` has CRLF endings: the first line ends with the bytes `d14\r\n`. Its SHA-256 is
  `e8a1aeb11d0709e81cdbd8d6ed6315b8bb8d644fa4a305254aab3aa62c0891d7`. Jirka's R code
  reproduces it byte for byte only if written with `eol = "\r\n"`; written with LF, every value
  is the same but the checksum differs.
- `tests/test_regression.py` refits all 44 nodes on both structures and compares the
  results with the committed CSVs in `results/phase-1.5/` byte for byte, every digit equal.

## 4. Where it appears in the code

`Makefile`; `pyproject.toml` (package, ruff and pytest settings); `requirements*.txt`;
`tests/`; `.gitattributes` (line endings); `data/raw/README.md` (checksums).
Architecture: `docs/code-guide/ARCHITECTURE.md`.

## 5. Common confusions

- *"Make re-ran nothing, so it's broken."* No: nothing was out of date. `make -B` forces it.
- *"A Makefile recipe line must start with a TAB"*, not spaces; otherwise make says "missing
  separator".
- *"Same values = same file."* Not for checksums: line endings, quotes or a final newline
  change the bytes. `cmp` and `sha256sum` compare bytes; pandas compares values.
- *"Passing tests prove the code is correct."* They prove it does what the tests check. The
  hand-computed BIC test checks the math; the regression test only checks nothing *changed*.
- *"git mv changes the file."* No: it only renames; the content (git "blob") is identical.

## 6. Check your understanding

1. You edit `src/bnjoint/cpt_scores.py`. What do `make phase-1` and `make phase-1.5` re-run?
2. Why is `data/raw/** -text` in `.gitattributes`?
3. A colleague's copy of `BN-data.csv` has a different SHA-256 from ours. Does that mean the
   data values differ?
4. Why is `scripts/fit_cpt_types.py` so short?
5. What would happen if `tests/test_regression.py` failed after a change?

---

**Answers.**
1. `make phase-1` re-runs nothing: scoring, GOBNILP and hc don't depend on `cpt_scores.py`.
   `make phase-1.5` re-runs both CPT-type fits (and the Table 2 comparison), because their CSVs
   list `cpt_scores.py` as a prerequisite.
2. So git never converts the CRLF line endings of Jirka's originals; converting them would
   change the bytes and the checksums.
3. Not necessarily: it might only differ in line endings or quoting. Compare values with pandas
   (or R) to find out; either way, investigate before using it.
4. All the logic lives in `src/bnjoint/`; the script only reads arguments, calls the package and
   prints a summary.
5. A reported number has changed. Stop and find out why. If the change is right, write the new
   result to a new results folder, add a decision log entry and a History line in the report
   that reported the number; never edit the old CSV.
