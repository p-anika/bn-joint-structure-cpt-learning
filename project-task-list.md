# Joint Structure + CPT-Type BN Learning — Full Task List

A step-by-step guide from a blank laptop to a finished project. Follow the
phases in order. 📧 marks a point where you should email Jirka.

---source .venv/bin/activate

## PHASE 0 — Environment Setup

### 0.1 Install core tools

| Tool | What it's for | Where to get it |
|---|---|---|
| **VS Code** | Your main editor for Python, R, C, and Markdown | https://code.visualstudio.com/ — download installer for your OS, run it, accept defaults |
| **Git** | Version control, talks to GitHub | https://git-scm.com/downloads — on Windows this also gives you "Git Bash"; on Mac, `git` usually ships with Xcode Command Line Tools (`xcode-select --install` in Terminal) |
| **Python 3.10+** | Data prep, scripting, MLR/OLR fitting | https://www.python.org/downloads/ — **on the installer, check "Add Python to PATH"** before clicking Install |
| **R 4.x + RStudio (optional but recommended)** | `bnlearn` hill-climbing, and to sanity-check against Jirka's own R code | R: https://cran.r-project.org/ ; RStudio: https://posit.co/download/rstudio-desktop/ |
| **A C/C++ compiler** | To compile `scoring2a.c` | Windows: install "Build Tools for Visual Studio" or use WSL + `g++`; Mac: `xcode-select --install` gives you `g++`/`clang`; Linux: `sudo apt install build-essential` |
| **GitHub account** | Hosting your repo | https://github.com/join if you don't have one |

### 0.2 Install VS Code extensions

Open VS Code → click the **Extensions** icon in the left sidebar (looks like 4 squares) → search and install each of:
- **Python** (by Microsoft)
- **Pylance** (usually auto-installs with Python extension)
- **R** (by REditorSupport) — only if you'll write R code in VS Code instead of RStudio
- **C/C++** (by Microsoft)
- **GitLens** (optional, makes Git history easier to read)
- **Markdown All in One** (optional, for editing notes/readme nicely)

### 0.3 Set up your project folder

1. Choose a location, e.g. `~/Documents/bn-project` (Mac/Linux) or `C:\Users\<you>\Documents\bn-project` (Windows).
2. Open a terminal (VS Code: **Terminal → New Terminal**, or `` Ctrl+` ``) and run:
   ```bash
   mkdir bn-project
   cd bn-project
   mkdir data src scripts notebooks results docs
   ```
   - `data/` — raw and processed data files (`.dat`, `.csv`, `.scores`)
   - `src/` — your actual algorithm code (Python/R modules)
   - `scripts/` — one-off run scripts (data conversion, pipeline drivers)
   - `notebooks/` — exploratory Jupyter/R Markdown notebooks
   - `results/` — output DAGs, tables, plots (don't commit huge files here — see `.gitignore` below)
   - `docs/` — your notes, derivations, this task list
3. Open the folder in VS Code: **File → Open Folder…** → select `bn-project`.

### 0.4 Create the GitHub repository and connect it

1. Go to https://github.com and click the **+** icon (top right) → **New repository**.
2. Name it something clear, e.g. `bn-joint-structure-cpt-learning`.
3. Set visibility (Private is fine to start; you can invite Jirka as a collaborator later via **Settings → Collaborators**, using his GitHub username or email).
4. **Do not** check "Add a README" (you'll push your own files in a moment) — or check it, doesn't matter much, just keep it simple.
5. Click **Create repository**. GitHub will show you a page with setup commands — you want the **"push an existing repository"** section.
6. Back in your VS Code terminal, inside `bn-project/`, run:
   ```bash
   git init
   git add .
   git commit -m "Initial project structure"
   git branch -M main
   git remote add origin https://github.com/<your-username>/bn-joint-structure-cpt-learning.git
   git push -u origin main
   ```
   - If prompted to log in, GitHub will walk you through browser-based authentication (or you can set up a Personal Access Token: **GitHub → Settings → Developer settings → Personal access tokens**).
7. Create a `.gitignore` file in the project root (VS Code: right-click in the file explorer panel → **New File** → name it `.gitignore`) with at least:
   ```
   __pycache__/
   *.pyc
   .Rhistory
   .RData
   *.egg-info/
   .venv/
   results/*.mat
   ```
   This keeps compiled junk and large result files out of your repo history.
8. From now on, your normal workflow after making changes is:
   ```bash
   git add .
   git commit -m "short description of what changed"
   git push
   ```

### 0.5 Set up a Python virtual environment

In the VS Code terminal, inside `bn-project/`:
```bash
python -m venv .venv
```
Activate it:
- Mac/Linux: `source .venv/bin/activate`
- Windows: `.venv\Scripts\activate`

VS Code should prompt "Select Interpreter" — pick the `.venv` one (or **Ctrl+Shift+P → Python: Select Interpreter → ./​.venv/bin/python**).

Install the Python packages you'll need:
```bash
pip install numpy pandas scipy statsmodels scikit-learn matplotlib jupyter
```
- `statsmodels` gives you multinomial logit (`MNLogit`) and ordinal regression (`OrderedModel`) — this is what you'll use to fit MLR/OLR.

### 0.6 Install R packages (if using R for the `bnlearn` hill-climbing baseline)

In R or RStudio console:
```r
install.packages(c("bnlearn", "nnet", "MASS", "qgraph"))
```
- `bnlearn` — hill-climbing structure search (matches what Jirka used in the paper)
- `nnet::multinom` — fits MLR
- `MASS::polr` — fits OLR
- `qgraph` — optional, for reproducing the paper's force-directed graph layout

### 0.7 Get and compile `scoring2a.c`

1. Copy `scoring2a.c` and `scoring-how-to-use-it.txt` into `bn-project/src/`.
2. In the terminal:
   ```bash
   cd src
   g++ -O2 -o scoring2a scoring2a.c -lm
   ```
3. Test it runs: `./scoring2a` with no arguments should print the usage message (`Usage: scoring datafile alpha parentslimit...`).

### 0.8 Install GOBNILP

1. Go to https://bitbucket.org/jamescussens/gobnilp/src/master/ and follow its build instructions (it depends on the SCIP optimization suite — SCIP has its own installer/build steps, follow SCIP's docs first, then GOBNILP's).
2. Alternatively, install the Python wrapper `pygobnilp` (https://pygobnilp.readthedocs.io/en/latest/), which may be simpler to get running:
   ```bash
   pip install pygobnilp
   ```
   Note: `pygobnilp` still needs a working GOBNILP/SCIP install underneath it in most setups — read its install page carefully before assuming `pip install` alone is enough.
3. Copy `gobnilp.set` into `bn-project/src/` alongside `scoring2a`.
4. Test GOBNILP on the provided example: run it on `data24-training-1-bic.scores` (already computed for you) and confirm you get a sensible adjacency matrix (`bi.mat`) out, with no errors. This validates your GOBNILP install independent of anything else.

### 0.9 Copy in all of Jirka's files

Put these into `bn-project/data/` and `bn-project/docs/` respectively:
- `data/`: `BN-data.csv`, `preprocesseddata.csv`, `data24-training-1.dat`, `data24-training-1-bic.scores`
- `docs/`: `paper_Kybernetika_2026_1.pdf`, `IJAR_2023__...pdf`, `scoring-how-to-use-it.txt`
- `src/`: `scoring2a.c`, `gobnilp.set`, `script-data24-1`

Commit and push:
```bash
git add .
git commit -m "Add project data and reference materials"
git push
```

**📧 EMAIL JIRKA #1 — "I'm set up."**
Once everything above runs without errors (compiler works, GOBNILP produces a DAG on the sample `data24-training-1-bic.scores`, Python/R packages installed), send a short email: environment is ready, GitHub repo link, and that you're starting on the baseline reproduction next. This is the "share your GitHub project" moment he explicitly invited.

---

## PHASE 1 — Reproduce the two-stage STD/MLR/OLR baseline

### 1.1 Convert `BN-data.csv` into `scoring2a`'s `.dat` format

Write `scripts/convert_data.py`:
- Read `BN-data.csv` with pandas.
- Remap values: `-1 → 0`, `0 → 1`, `1 → 2` (scoring2a needs non-negative integer codes starting at 0).
- Write out a `.dat` file with this exact structure:
  ```
  44
  3 3 3 ... (44 times)
  1661
  <44 space-separated values per row, one row per respondent>
  ```
- Save as `data/bn-data-44.dat`.

Run it:
```bash
python scripts/convert_data.py
```

### 1.2 Run the local scoring program

```bash
cd src
./scoring2a ../data/bn-data-44.dat 1 9 prune 0 bic > ../data/bn-data-44-bic.scores
```
(Matches the invocation pattern in `script-data24-1` and `scoring-how-to-use-it.txt` — alpha=1 for true BIC, max 9 parents, pruning on.)

### 1.3 Run GOBNILP to get the BIC-optimal DAG

```bash
gobnilp ../data/bn-data-44-bic.scores
```
(or via `pygobnilp` in a Python script — either is fine, but note which one you used, since Jirka flagged uncertainty about whether the input format still matches the newest GOBNILP version — **if this step errors out, that's useful information to bring to him**, see checkpoint below.)

Save the resulting adjacency matrix / DAG structure into `results/std-baseline-dag.txt` (or whatever GOBNILP outputs as, per `gobnilp.set`).

### 1.4 Fit MLR and OLR for each learned family and pick the best per node

Write `scripts/fit_cpt_types.py`:
- Load the learned DAG structure from 1.3.
- For each node `v` with parent set `pa(v)`:
  - Compute `BIC_STD` from the standard tabular CPT (counts + formula 6/7/9 from the paper).
  - Fit MLR via `statsmodels.discrete.discrete_model.MNLogit` (or R's `nnet::multinom`), compute its BIC using its parameter count (paper's eq. 12).
  - If `pa(v)` is non-empty, fit OLR via `statsmodels.miscmodels.ordinal_model.OrderedModel` (or R's `MASS::polr`), compute its BIC using its parameter count (paper's eq. 17).
  - Record which of the three wins.
- Tabulate results: counts of STD/MLR/OLR wins, and whether every multi-parent node used MLR/OLR (this is the specific claim to check against the paper).

### 1.5 Validate against the paper

Compare your tally to the paper's reported **19 STD (43%), 22 MLR (50%), 3 OLR (7%)**, and the claim that every node with more than one parent used MLR or OLR. Write a short summary in `docs/baseline-reproduction-notes.md`: what matched, what didn't, and your best guess why (e.g., solver version differences, tie-breaking, alpha value, hill-climbing vs. exact search if you used `bnlearn` instead of GOBNILP for structure).

### 1.6 (Optional but recommended) Cross-check with `bnlearn` in R

Since the paper itself used `bnlearn`'s hill-climbing (`hc()`) rather than GOBNILP for the structure step, running this too gives you a second reference point:
```r
library(bnlearn)
d <- read.csv("data/BN-data.csv")
d[] <- lapply(d, as.factor)
dag <- hc(d, score = "bic")
```
Compare this structure to your GOBNILP one — do they agree? If not, that's expected (hill-climbing isn't guaranteed optimal) but worth noting.

Commit everything:
```bash
git add .
git commit -m "Phase 1: two-stage baseline reproduction"
git push
```

**📧 EMAIL JIRKA #2 — "Baseline reproduced."**
Send your `baseline-reproduction-notes.md` summary (or paste the key numbers inline): your STD/MLR/OLR split vs. the paper's, whether the GOBNILP input-format assumption held up, and any bugs/surprises. This is the natural point to ask any clarifying questions about scoring2a's options (alpha, palim) or GOBNILP settings before you start modifying the pipeline itself.

---

## PHASE 2 — Study the pruning-bound machinery you'll need to extend

This phase is mostly reading and note-taking, not code — but write your notes into the repo so Jirka can see your reasoning.

### 2.1 Understand the existing STD pruning bound

- Read `scoring2a.c` closely, specifically:
  - the `subset_tree` / `check_subset` / `add_subset` functions (how it tracks which parent subsets have already survived pruning)
  - the `keep`/`prune` decision logic inside `main()` (search for the `if ( pruning )` block) — this is where the actual BIC-based prune-or-keep decision happens
- Read the de Campos entropy-pruning paper (https://arxiv.org/abs/1707.06194) alongside the code, matching each formula to where it's implemented.
- Write `docs/pruning-notes.md` explaining, in your own words, *why* the bound is valid for standard tabular CPTs (hint: it relies on STD log-likelihood being a closed-form function of sufficient statistics/counts alone).

### 2.2 Study the closest existing precedent: Noisy-OR pruning (Lemma 3)

- Read the IJAR 2023 paper's Lemma 3 (the "general but weak" pruning rule Jirka mentioned) in detail.
- Note exactly what it does and doesn't guarantee, and why it isn't tight.
- Add this to `docs/pruning-notes.md`.

### 2.3 Sketch what's different for MLR/OLR

- Write out (by hand or in the notes doc) why MLR/OLR log-likelihood doesn't decompose into sufficient statistics the way STD does — this is the crux of "why you can't just reuse de Campos's bound."
- List candidate directions: looser upper bounds on MLR/OLR log-likelihood, a cheap approximate score (e.g., single Newton-Raphson step) to screen candidates, or adapting the IJAR Lemma 3 style of argument to MLR/OLR.

Commit:
```bash
git add docs/pruning-notes.md
git commit -m "Phase 2: pruning bound literature notes"
git push
```

**📧 EMAIL JIRKA #3 — "Here's my read on the pruning problem."**
Send your `pruning-notes.md` and your candidate directions from 2.3. This is a good moment to propose *which* direction you want to try first and get his sign-off before investing implementation time — he explicitly said this part is genuinely open/unsolved on their end, so his early feedback here is high-value.

---

## PHASE 3 — Build the joint structure + CPT-type algorithm

### 3.1 Modify the scoring step

- Decide implementation path: either (a) modify `scoring2a.c` directly to compute `max(BIC_STD, BIC_MLR, BIC_OLR)` per candidate family in C, or (b) write a Python/R layer that calls out to fit MLR/OLR per candidate family and produces a modified `.scores` file that GOBNILP can still consume. Path (b) is slower but much faster to develop and debug — recommended to prototype with (b) first.
- Implement whichever pruning/screening approach you settled on in Phase 2.
- Keep the STD-only pipeline (Phase 1) intact and separate, so you can always compare against it.

### 3.2 Test on a small subset first

- Before running on the full 44 variables, test your modified scoring on a small subset (e.g., 8–10 variables) so any bugs are fast to find and fix, and so you can hand-check a few candidate family scores against a manual calculation.

### 3.3 Scale up and run on the full dataset

- Run your joint scorer on all 44 variables.
- Feed the resulting scores into GOBNILP (or your hill-climbing fallback if exact search proves infeasible).
- Time it, and record runtimes at each subset size — this data matters for evaluating your pruning/screening approach's effectiveness, not just the final structure.

### 3.4 If exact search is infeasible: implement the hill-climbing fallback

- Implement (or adapt `bnlearn`'s `hc()`) a version that at each step considers adding/removing/reversing an edge, scoring each move with the joint `max(BIC_STD, BIC_MLR, BIC_OLR)` score.
- Document whatever guarantee you can attach (e.g., a bound on how far from optimal the result can be, or how much of the search space your pruning safely eliminated) — Jirka was explicit this matters to him.

Commit incrementally as you go (don't wait until the end):
```bash
git add .
git commit -m "Phase 3: prototype joint scoring on subset"
git push
# ... later
git add .
git commit -m "Phase 3: joint scoring on full 44-variable dataset"
git push
```

**📧 EMAIL JIRKA #4 — mid-Phase-3 check-in.**
Once you have a working prototype on the small subset (3.2), even before scaling up — send a quick update on what you built, what worked, and any snags. Don't wait until the full pipeline is done; catching a wrong assumption here saves a lot of wasted compute/debugging later.

**📧 EMAIL JIRKA #5 — full pipeline results.**
Once 3.3 (and 3.4 if needed) produce a complete joint-optimized DAG, send the results: runtime, whether exact GOBNILP search was feasible or you needed the hill-climbing fallback, and the resulting BIC.

---

## PHASE 4 — Evaluate and write up

### 4.1 Compare joint vs. two-stage

- Compare your Phase 3 joint-optimized (structure, CPT-type) model against your Phase 1 two-stage baseline:
  - Total BIC score: does the joint approach win, and by how much?
  - Structural differences: are there edges present in one DAG but not the other? This is the interesting result — it demonstrates the two-stage limitation empirically.
  - CPT-type distribution: STD/MLR/OLR split under the joint approach vs. the two-stage one.

### 4.2 Write results into the repo

- `docs/final-results.md`: summary tables/plots, structural comparison (consider visualizing both DAGs side by side — `qgraph` in R or `networkx`+`matplotlib` in Python), and your interpretation.
- Update the main `README.md` in the repo root to describe the project, how to run each phase's scripts, and link to `final-results.md`.

### 4.3 Final commit and tag

```bash
git add .
git commit -m "Phase 4: final evaluation and results writeup"
git tag v1.0-first-results
git push --tags
git push
```

**📧 EMAIL JIRKA #6 — final results and next-steps discussion.**
Send the full writeup (or the repo link with `final-results.md` highlighted). This is the natural point to discuss whether the results are strong enough to fold into a short paper/report, and what — if anything — he'd want extended next (continuous variables, GAMs, Noisy-OR integration, etc., per the paper's own future-work list).

---

## Quick reference: email checkpoint summary

| # | When | What to include |
|---|---|---|
| 1 | Environment fully working (end of Phase 0) | GitHub repo link, confirmation everything installed/compiles/runs |
| 2 | Baseline reproduced (end of Phase 1) | STD/MLR/OLR split vs. paper's numbers, any discrepancies |
| 3 | Pruning literature review done (end of Phase 2) | Your notes, proposed direction, ask for sign-off |
| 4 | Small-subset joint-scoring prototype works (mid-Phase 3) | What you built, early snags |
| 5 | Full joint pipeline produces results (end of Phase 3) | Runtime, feasibility of exact search, resulting BIC |
| 6 | Final evaluation complete (end of Phase 4) | Full writeup, structural comparison, discussion of next steps |
