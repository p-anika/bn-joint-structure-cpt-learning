# data/raw/: Jirka's original data files (READ-ONLY)

These files are exactly as Jirka sent them. **Never edit, re-save or convert them.** Anything
derived from them goes to `data/processed/` or `results/`. Git is told never to change their
bytes (`-text` in `.gitattributes`), because four of them have Windows line endings (CRLF),
and converting those would change the files and their checksums.

To check that a file is unchanged: `sha256sum data/raw/<file>` and compare with the table.
A SHA-256 checksum is a 64-character fingerprint of a file's bytes; changing even one byte
gives a completely different checksum (explainer `docs/explainers/00-repo-tools.md`).

| File | What it is | From | Line endings | SHA-256 |
|---|---|---|---|---|
| `BN-data.csv` | The 44-variable data of the Kybernetika paper: columns a1–a30, d1–d14, 1661 rows, values −1/0/1. The input to everything. | Jirka, email **Aug 5, 2026** | CRLF | `e8a1aeb11d0709e81cdbd8d6ed6315b8bb8d644fa4a305254aab3aa62c0891d7` |
| `preprocessed-data.csv` | Jirka's preprocessed survey, original 1–7 answer scale, 72 columns (28 background variables, then a1–a30, d1–d14). | Jirka, email **Jul 8, 2026** | CRLF | `839df9ca3c6b29171eb673389ee26a9ce2c26d8f08a8acc04c4f1ed5eabbf033` |
| `data24-training-1.dat` | Jirka's 23-variable example in scoring2a format, used as a GOBNILP smoke test. | Jirka, email **Jul 8, 2026**, "unix files.zip" | CRLF | `bbf5d659ba0d83cb613c864f955035e7088cf8d8820abc199d913ff2e67cff7f` |
| `data24-training-1-bic.scores` | Jirka's scoring2a output for that example (local BIC scores). | Jirka, email **Jul 8, 2026**, "unix files.zip" | LF | `5205adc723ec8e2d98360328876717bbd64bb2134606e6b1af6e730c2af97d87` |

## How BN-data.csv was made (verified)

Jirka's Aug 5, 2026 email gives the R code that turns `preprocessed-data.csv` into
`BN-data.csv`: keep columns 29–72, then map answers 1–3 → −1, 4 → 0, 5–7 → +1. His code is
saved verbatim in [`R/convert_jirka_aug5.R`](../../R/convert_jirka_aug5.R). Re-running it
(`make provenance`) gives a file **byte-identical** to `BN-data.csv` (2026-11-15; details in
`docs/reports/1.5.0b.md`). In the same email Jirka wrote that it is better to use `BN-data.csv`
directly, so that we both work with identical data, and that is what all our code does
(decision log entry 2).

## Files from the Jul 8 zip that are not here

- `scoring2a.c`, `scoring-how-to-use-it.txt`, `script-data24-1` are tools, so they live in
  `tools/scoring2a/`; `gobnilp.set` lives in `tools/gobnilp/` (decision log entry 14). They are
  byte-identical to what Jirka sent.
- `scoring2a`, Jirka's **compiled** program, is not kept: no compiled binaries in git (decision
  log entry 29). Its SHA-256 was
  `3dc618b6a034265c17efeeb8006083f424c68770e1a0fef93c06bfc671d5b5fa`. The original is still in
  the Jul 8 email's "unix files.zip". We build our own from `scoring2a.c` with
  `make scoring2a`.
