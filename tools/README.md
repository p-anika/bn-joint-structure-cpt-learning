# tools/: other people's programs and their settings

Only source code and settings live here. Compiled programs are built by `make` and are not
committed. Big external builds (SCIP, GOBNILP) live outside the repo, in `~/tools/` and
`~/scipoptsuite-10.0.3/`; how to build them is in `docs/setup.md`.

| Folder | What it holds |
|---|---|
| [`scoring2a/`](scoring2a/README.md) | de Campos's local-score program (C source) and Jirka's notes on running it |
| [`gobnilp/`](gobnilp/README.md) | The GOBNILP settings file we run with |
