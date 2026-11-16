# src/bnjoint/: the project's Python package

Reusable code. Scripts in `scripts/` are thin wrappers around it, and `tests/` tests it.
Installed in editable mode by `pip install -r requirements.txt` (the `-e .` line), so
`import bnjoint` works everywhere and always uses the code in this folder. How the modules
connect: [`docs/code-guide/ARCHITECTURE.md`](../../docs/code-guide/ARCHITECTURE.md).

| File | What it does |
|---|---|
| `__init__.py` | Marks the folder as a package; lists the modules |
| `config.py` | Shared paths (`data/raw/BN-data.csv`, `results/phase1/…`) and constants (3 states, alpha 1, palim 9) |
| `io.py` | Read and check BN-data.csv; write scoring2a's `.dat` file and the names file |
| `gobnilp_io.py` | Read the learned parent sets out of a GOBNILP console log |
| `cpt_scores.py` | BIC of STD, MLR and OLR for a family; the per-node winner. The only copy of this math. |

All files are originals written by us.
