# src/bnjoint/: the project's Python package

Reusable code. Scripts in `scripts/` are thin wrappers around it, and `tests/` tests it.
Installed in editable mode by `pip install -r requirements.txt` (the `-e .` line), so
`import bnjoint` works everywhere and always uses the code in this folder. How the modules
connect: [`docs/code-guide/ARCHITECTURE.md`](../../docs/code-guide/ARCHITECTURE.md).

| File | What it does |
|---|---|
| `__init__.py` | Marks the folder as a package; lists the modules |
| `config.py` | Shared paths (`data/raw/BN-data.csv`, `results/phase1/…`, `results/phase1.5/…`, Table 2) and constants (3 states, tie tolerance 1e-6 and order STD/OLR/MLR, alpha 1, palim 9) |
| `io.py` | Read and check BN-data.csv; write scoring2a's `.dat` file and the names file |
| `gobnilp_io.py` | Read the learned parent sets out of a GOBNILP console log |
| `cpt_scores.py` | BIC of STD, MLR and OLR for a family, with MLR/OLR convergence flags; the per-node winner (tie rule). The only copy of this math. |
| `structures.py` | Read a bnlearn adjacency-matrix CSV and a typed-in reference table (Table 2); compare per node |

All files are originals written by us.
