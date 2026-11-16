# tools/scoring2a/: the local-score program

scoring2a computes the BIC of every candidate parent set of every variable and writes them to
a `.scores` file for GOBNILP. What the code does: [`docs/code-guide/scoring2a.md`](../../docs/code-guide/scoring2a.md).

| File | What it is | From |
|---|---|---|
| `scoring2a.c` | C source. Based on GOBNILP's scoring code (© 2012 James Cussens, GPL v3), with a one-line note that Cassio de Campos modified it on 22 Sept 2014; the file does not say what he changed. CRLF line endings, kept as received. | Jirka, email Jul 8, 2026, "unix files.zip" (SHA-256 `e22001e7d3f843429f1606dfb0f27c472317c1f8b9654bf1469ec8cb90f125af`) |
| `scoring-how-to-use-it.txt` | de Campos's note: how to compile and run it; alpha = 1 gives the true BIC | Jirka, Jul 8, 2026 zip (SHA-256 `a04470bf6fb0dbd4b164c297a095d4c8ce36d77f7898abb5b24e78b5e3b6c496`) |
| `script-data24-1` | Jirka's 3-line example: strip CRLF, run scoring2a with `1 9 prune 0 bic`, run GOBNILP (old syntax without `-f`) | Jirka, Jul 8, 2026 zip (SHA-256 `037383666655386c0fb1137cc2dda47f9baba3e3a5e3fda5b5c62a966d7809c3`) |
| `scoring2a` | **Not in git.** The compiled program, built by `make scoring2a` (`g++ -O2 -o scoring2a scoring2a.c -lm`, de Campos's command) | built locally |

Check with `sha256sum tools/scoring2a/*`. Compiling prints `-Wunused-result` warnings
about `fscanf`; they are harmless and the code is deliberately left unchanged.

Run (what `make phase1` does): `tools/scoring2a/scoring2a <file>.dat 1 9 prune 0 bic > <file>.scores`.
The meaning of each argument is in `docs/setup.md` §6.
