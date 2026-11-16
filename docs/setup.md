# Setup: building the environment from scratch

This file says how to rebuild everything this project needs on a new computer, and records
the versions we actually use. It is the **only** setup guide. It replaces
`phase-0-detailed-steps.md`, `project-task-list.md` (Phase 0) and `docs/bnsl_header.md`, which
were deleted in step 1.5.0a (see `docs/decision-log.md`).

> **Updated 2026-11-15 (step 1.5.0b).** GOBNILP is now built in `~/tools/gobnilp/` (outside
> the repo), scoring2a's source is in `tools/scoring2a/` and is compiled with `make scoring2a`,
> and the Python packages are pinned in `requirements.txt` / `requirements-dev.txt`.

Where a step was reconstructed from the shell history (`~/.bash_history`) rather than
re-run, it says so.

## Versions in use

| Tool | Version | How checked |
|---|---|---|
| Windows + WSL2 | Ubuntu (WSL2), kernel 6.18 | `uname -r` |
| Python | 3.14.4 | `.venv/bin/python --version` |
| Python packages | pinned in `requirements.txt` (numpy 2.5.1, pandas 3.0.5, scipy 1.18.0, statsmodels 0.14.6, patsy 1.0.2, matplotlib 3.11.1) and `requirements-dev.txt` (pytest 9.2.0, ruff 0.17.5) | `pip freeze` in `.venv` |
| GNU Make | 4.4.1 | `make --version` |
| R | 4.5.2 (2025-10-31) | `R --version` |
| R packages | bnlearn 5.2.1, nnet 7.3.21, MASS 7.3.66, qgraph 1.10.1 | `packageVersion()` |
| C/C++ compiler | g++ (Ubuntu 15.2.0-16ubuntu1) 15.2.0 | `g++ --version` |
| SCIP Optimization Suite | 10.0.3 (SCIP 10.0.3, SoPlex 8.0.3) | first lines of `results/gobnilp-std-run.log` |
| GOBNILP | git commit `5441edf` of `bitbucket.org/jamescussens/gobnilp` ("GitHash: unknown" in its own banner), built in `~/tools/gobnilp/` | `git -C ~/tools/gobnilp log -1` |

Jirka's own Kybernetika results used a much older GOBNILP 1.6.3 with SCIP 3.2.1. We don't
need that version: our build reads the same score files once the header below is added
(decision log, 2026-11-15).

## 1. WSL2 and VS Code (Windows only)

**Why WSL2.** WSL2 (Windows Subsystem for Linux) is a real Ubuntu Linux running inside Windows.
`scoring2a.c` and GOBNILP/SCIP are research programs written and tested on Linux. Building them
with native Windows tools is possible but poorly documented, so WSL2 is the standard path.

1. Open PowerShell **as Administrator** and run `wsl --install`. Restart when asked.
2. Ubuntu opens and asks for a UNIX username and password. This password is only for `sudo`
   inside Ubuntu. Write it down; nothing appears on screen while you type it.
3. Update Ubuntu: `sudo apt update && sudo apt upgrade -y`.
4. Install VS Code on Windows (https://code.visualstudio.com/). Add the extensions **WSL**
   (Microsoft), **Python** (Microsoft), **R** (REditorSupport) and **C/C++** (Microsoft).
5. In VS Code press `F1` → "WSL: Connect to WSL". The bottom-left corner should say
   **WSL: Ubuntu**. Always work in that window.
6. Keep the project inside Linux (`~/bn-project`), **not** under `/mnt/c/...`. The Windows
   drive is slower from Linux and causes permission problems.

## 2. Git and GitHub

```bash
git config --global user.name  "<your name>"
git config --global user.email "<your email>"
ssh-keygen -t ed25519 -C "<your email>"   # press Enter to accept defaults
cat ~/.ssh/id_ed25519.pub                 # paste into GitHub → Settings → SSH and GPG keys
ssh -T git@github.com                     # should say "Hi <username>!"
git clone git@github.com:p-anika/bn-joint-structure-cpt-learning.git ~/bn-project
```

We use an SSH key because GitHub no longer accepts account passwords for `git push`.

## 3. Ubuntu packages

These are the packages installed on this machine (from the shell history):

```bash
sudo apt install -y build-essential cmake                          # C/C++ compiler, make, cmake
sudo apt install -y python3-pip python3-venv                       # Python virtual environments
sudo apt install --no-install-recommends -y r-base                 # R
sudo apt install -y libblas-dev liblapack-dev gfortran libxml2-dev libssl-dev \
  libcurl4-openssl-dev libfontconfig1-dev libharfbuzz-dev libfribidi-dev \
  libfreetype6-dev libpng-dev libjpeg-dev libtiff5-dev libglpk-dev pandoc libuv1-dev  # needed by R packages
sudo apt install -y libreadline-dev libmpfr-dev                    # needed by SCIP's cmake
sudo apt-get install -y gfortran liblapacke-dev libopenblas-dev    # needed by GOBNILP
```

## 4. Python virtual environment

A *virtual environment* (`.venv/`) is a private folder of Python packages for this project only,
so other projects can't break it. It is not committed to git.

```bash
cd ~/bn-project
python3 -m venv .venv
source .venv/bin/activate        # the prompt now starts with (.venv)
pip install -r requirements-dev.txt   # research packages + pytest + ruff, exact versions
```

`requirements.txt` holds the packages the research code needs, pinned to exact versions so
results don't change when a package updates; its last line, `-e .`, installs our own package
`src/bnjoint/` in *editable* mode (Python uses the folder directly, so edits take effect at
once). `requirements-dev.txt` adds pytest (tests) and ruff (formatting). Check with `make test`.
Jupyter and scikit-learn were installed earlier for exploring but are not used by the code, so
they are not pinned.

## 5. R packages

Inside R (run `R`, then):

```r
install.packages(c("bnlearn", "nnet", "MASS", "qgraph"))
library(bnlearn)   # no error = it worked; leave with q() and answer n
```

`bnlearn` is used for hill-climbing and CPDAGs. `nnet`/`MASS` contain R versions of MLR/OLR,
and `qgraph` draws graphs.

## 6. scoring2a (local BIC scores)

`scoring2a.c` is Cassio de Campos's scoring program, sent by Jirka in his Jul 8 zip. For every
variable it computes the BIC of every candidate parent set that survives de Campos's pruning,
and writes them to a `.scores` file.

```bash
cd ~/bn-project
make scoring2a                 # runs: g++ -O2 -o tools/scoring2a/scoring2a tools/scoring2a/scoring2a.c -lm
tools/scoring2a/scoring2a      # with no arguments it prints its usage message
```

The compiled program is not committed (no binaries in git); `make phase1` builds it if it is
missing. The compiler prints `-Wunused-result` warnings about `fscanf`; they are harmless.

How it is run (from `scoring-how-to-use-it.txt` and Jirka's `script-data24-1`):

```bash
tools/scoring2a/scoring2a <file>.dat 1 9 prune 0 bic > <file>.scores
```

- `1` is **alpha**. For BIC it multiplies the penalty, so `1` gives the true BIC.
- `9` is the maximum number of parents (**palim**).
- `prune` switches on the safe pruning.
- `0` is used only by another score type (min-BDeu) and is ignored here.
- `bic` is the score type.

## 7. SCIP and GOBNILP (exact structure search)

GOBNILP finds the best-scoring network from a scores file by solving an integer program.
It needs the SCIP solver underneath. This is the part most likely to cause trouble.

**7a. SCIP Optimization Suite 10.0.3** (reconstructed from the shell history):

```bash
cd ~
wget https://scipopt.org/download/release/scipoptsuite-10.0.3.tgz
tar -xzf scipoptsuite-10.0.3.tgz
cd scipoptsuite-10.0.3 && mkdir -p build && cd build
cmake .. -DPAPILO=off -DAUTOBUILD=ON     # history: plain `cmake ..` was retried with these flags (reason not recorded)
make -j$(nproc)
sudo make install                        # puts `scip` in /usr/local/bin
```

`build/CMakeCache.txt` records the settings actually used: `LPS=spx` (the SoPlex LP solver),
`SYM=snauty`, `GMP=ON`, `AMPL=ON`, `ZIMPL=ON`, `IPOPT=ON`, `TPI=tny`, `PAPILO=off`.

**SoPlex** needs no separate step: the SCIP Optimization Suite contains SoPlex 8.0.3 and
builds it together with SCIP (`LPS=spx`).

**7b. GOBNILP**, built **outside the repo** in `~/tools/gobnilp/`:

```bash
mkdir -p ~/tools && cd ~/tools
git clone https://bitbucket.org/jamescussens/gobnilp.git
cd gobnilp
git checkout 5441edf                     # the commit we use
ln -s ~/scipoptsuite-10.0.3/scip scip    # GOBNILP finds SCIP through a link called `scip`
make
bin/gobnilp -f data/gaussian.bnsl        # GOBNILP's own example; should solve quickly
```

The link must point to the `scip/` folder inside the suite, **not** to `build/`. The history
shows a first link to `build/` that was removed and replaced with this one.

GOBNILP's `make` also builds the SCIP libraries it links against: its Makefile's `all` target
depends on a target `scip` that runs `make -C scip libs`, which writes
`scipoptsuite-10.0.3/scip/lib/static/`. (Settled in step 1.5.0b: the library timestamps are
Aug 10, 15:51–15:52, just before the GOBNILP binary's 15:52:31, and a re-run of `make` in the
new location visibly rebuilds `libscipbase` before linking GOBNILP.) The GOBNILP binary
contains SCIP (static linking; `ldd` lists only system libraries), so moving the GOBNILP folder
doesn't break it as long as the `scip` link still points at an existing folder.

*History:* until step 1.5.0b the build lived inside the repo at `src/gobnilp/`. It was moved
with `mv ~/bn-project/src/gobnilp ~/tools/gobnilp`, the PATH link below was redirected, and
`make` was re-run there; the data24 smoke test and `make phase1` then gave the same results
(`docs/reports/1.5.0b.md`).

**7c. Put `gobnilp` on the PATH.** The *PATH* is the list of folders the shell searches when
you type a command name.

```bash
mkdir -p ~/.local/bin
ln -sfn ~/tools/gobnilp/bin/gobnilp.linux.x86_64.gnu.opt.spx ~/.local/bin/gobnilp
# ~/.local/bin must be on PATH; add this to ~/.bashrc if `which gobnilp` finds nothing:
export PATH="$HOME/.local/bin:$PATH"
```

**7d. Run GOBNILP the right way.**

```bash
gobnilp -f <file>.bnsl -s tools/gobnilp/gobnilp.set
```

- **`-f` is required** in this version. A bare filename (`gobnilp file.bnsl`), as in older
  instructions and Jirka's `script-data24-1`, does not work.
- `-s gobnilp.set` loads Jirka's settings file. It sets `gobnilp/outputfile/adjacencymatrix`,
  which this newer GOBNILP doesn't recognize, so it prints a warning and never writes `bi.mat`.
  That is harmless: the learned parent sets are printed in the console output as
  `child:-{parent1,parent2}`, and `scripts/fit_cpt_types.py` reads them from the saved log.
  The warning (`WARNING: unknown parameter <gobnilp/outputfile/adjacencymatrix>`) goes to the
  error stream (stderr), which `| tee` doesn't capture, so it is not in the saved logs
  (confirmed in step 1.5.0b).
- GOBNILP also writes `adjmat.txt`/`.dot` and `pdagadjmat.txt`/`.dot` (the DAG and its CPDAG;
  row = parent, column = child) into the folder it is run from. The Makefile runs it inside the
  results folder for that reason.
- Easiest: `make test-data24` (5 seconds) and `make phase1`.

## 8. The `.bnsl` header GOBNILP needs

scoring2a writes a `.scores` file that starts with the number of variables. This GOBNILP
version needs **two extra lines first**: the variable names, then `SCORES START`.

```
a1 a2 a3 ... d14        ← line 1: variable names, separated by spaces
SCORES START            ← line 2
44                      ← then the scoring2a output, unchanged: number of variables
0 177                   ← variable index (0 = a1) and how many parent sets follow
-1410.601461 2 18 26    ← score, number of parents, parent indices (18 = a19, 26 = a27)
```

`scripts/add_bnsl_header.sh` adds those lines:

```bash
scripts/add_bnsl_header.sh data/processed/bn-data-44-bic.scores data/processed/bn-data-44-bic-fixed.bnsl $(cat data/processed/bn-data-44-varnames.txt)
```

How we found this: GOBNILP's example file `scores/chest_100_1_3.bnsl` (which Jirka pointed to
in his Aug 12 email) starts this way, and GOBNILP's reader source looks for `SCORES START`.

## 9. Gotchas

- **Windows line endings.** Files made on Windows end each line with `\r\n` (CRLF) instead of
  `\n` (LF). scoring2a and GOBNILP can misread them, and Jirka has been caught by this before.
  Check with `file <name>` ("with CRLF line terminators" means trouble). Fix a *copy* with
  `sed 's/\r$//' in > out`, never the original in `data/raw/`.
  **Correction (2026-11-15):** this file used to say "`BN-data.csv` is already LF". That was
  wrong: `BN-data.csv`, `preprocessed-data.csv`, `data24-training-1.dat`, `scoring2a.c` and
  `gobnilp.set` all have CRLF endings (`git ls-files --eol` shows `i/crlf`; `file` doesn't
  report it for CSV files). No result is affected: pandas and R read CRLF correctly, and
  scoring2a reads `bn-data-44.dat`, which our script writes with LF. Git is told never to
  convert the originals (`.gitattributes`).
- **`bi.mat` is never written** (see 7d); use the console log.
- **Run from the project root** unless a script says otherwise.

## 10. Check list: everything works

```bash
git --version && python3 --version && R --version | head -1 && g++ --version | head -1
make scoring2a && tools/scoring2a/scoring2a | head -2   # prints the usage message
which gobnilp && readlink -f $(which gobnilp)           # ~/tools/gobnilp/bin/gobnilp.linux.x86_64.gnu.opt.spx
Rscript -e 'library(bnlearn)'               # no error
make test                                   # all tests pass
make test-data24                            # objective value -3411.597651
make phase1                                 # ends with objective value -64837.738627
```
