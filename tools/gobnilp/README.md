# tools/gobnilp/: GOBNILP settings

GOBNILP itself (James Cussens's exact structure learner) is built outside the repo in
`~/tools/gobnilp/` and found through `~/.local/bin/gobnilp`; see `docs/setup.md` §7.

| File | What it is | From |
|---|---|---|
| `gobnilp.set` | Settings file passed with `-s`. Its only active line, `gobnilp/outputfile/adjacencymatrix = "bi.mat"`, is a parameter name this newer GOBNILP doesn't know: it prints a warning on stderr and ignores it (decision log entry 6). CRLF line endings, kept as received. | Jirka, email Jul 8, 2026, "unix files.zip" (SHA-256 `b3765982ef6ecce0806871f5f210974bf4e02eb619827e7e4b5647f6ea1cf074`) |

We keep passing it so our runs use the same settings file as Jirka's.
