# Setup: building the environment from scratch

This file says how to rebuild everything this project needs on a new computer, and records
the versions we actually use. It is the **only** setup guide. It replaces
`phase-0-detailed-steps.md`, `project-task-list.md` (Phase 0) and `docs/bnsl_header.md`, which
were deleted in step 1.5.0a (see `docs/decision-log.md`).

> **Status (2026-11-15).** The paths below are today's paths: GOBNILP is still built inside
> `src/gobnilp/`, and `scoring2a` lives in `src/`. Step 1.5.0b moves the GOBNILP build to
> `~/tools/gobnilp/` and scoring2a to `tools/scoring2a/`, and will update this file.

Where a step was reconstructed from the shell history (`~/.bash_history`) rather than
re-run, it says so.

## Versions in use

| Tool | Version | How checked |
|---|---|---|
| Windows + WSL2 | Ubuntu (WSL2), kernel 6.18 | `uname -r` |
| Python | 3.14.4 | `.venv/bin/python --version` |
| pandas / statsmodels | 3.0.5 / 0.14.6 | imported in `.venv` |
| R | 4.5.2 (2025-10-31) | `R --version` |
| R packages | bnlearn 5.2.1, nnet 7.3.21, MASS 7.3.66, qgraph 1.10.1 | `packageVersion()` |
| C/C++ compiler | g++ (Ubuntu 15.2.0-16ubuntu1) 15.2.0 | `g++ --version` |
| SCIP Optimization Suite | 10.0.3 (SCIP 10.0.3, SoPlex 8.0.3) | first lines of `results/gobnilp-std-run.log` |
| GOBNILP | git commit `5441edf` of `bitbucket.org/jamescussens/gobnilp` ("GitHash: unknown" in its own banner) | `git log -1` inside the GOBNILP folder |

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
pip install numpy pandas scipy statsmodels scikit-learn matplotlib jupyter
```

Step 1.5.0b replaces the `pip install` line with pinned files: `pip install -r requirements.txt`
for the project and `-r requirements-dev.txt` for pytest and ruff.

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
cd ~/bn-project/src
g++ -O2 -o scoring2a scoring2a.c -lm
./scoring2a            # with no arguments it prints its usage message
```

How it is run (from `scoring-how-to-use-it.txt` and Jirka's `script-data24-1`):

```bash
./scoring2a <file>.dat 1 9 prune 0 bic > <file>.scores
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

**7b. GOBNILP** (reconstructed from the shell history):

```bash
git clone https://bitbucket.org/jamescussens/gobnilp.git
cd gobnilp
ln -s ~/scipoptsuite-10.0.3/scip scip    # GOBNILP finds SCIP through a link called `scip`
make
bin/gobnilp -f data/gaussian.bnsl        # GOBNILP's own example; should solve quickly
```

The link must point to the `scip/` folder inside the suite, **not** to `build/`. The history
shows a first link to `build/` that was removed and replaced with this one after `make`. GOBNILP's Makefile uses SCIP's own `make` system, whose libraries are in
`scipoptsuite-10.0.3/scip/lib/static/`. *Unsure:* the history doesn't show exactly which
command created those static libraries. Step 1.5.0b rebuilds GOBNILP and will record it.

**7c. Put `gobnilp` on the PATH.** The *PATH* is the list of folders the shell searches when
you type a command name.

```bash
mkdir -p ~/.local/bin
ln -s <gobnilp folder>/bin/gobnilp.linux.x86_64.gnu.opt.spx ~/.local/bin/gobnilp
# ~/.local/bin must be on PATH; add this to ~/.bashrc if `which gobnilp` finds nothing:
export PATH="$HOME/.local/bin:$PATH"
```

**7d. Run GOBNILP the right way.**

```bash
gobnilp -f <file>.bnsl -s gobnilp.set
```

- **`-f` is required** in this version. A bare filename (`gobnilp file.bnsl`), as in older
  instructions and Jirka's `script-data24-1`, does not work.
- `-s gobnilp.set` loads Jirka's settings file. It sets `gobnilp/outputfile/adjacencymatrix`,
  which this newer GOBNILP doesn't recognize, so it prints a warning and never writes `bi.mat`.
  That is harmless: the learned parent sets are printed in the console output as
  `child:-{parent1,parent2}`, and `scripts/fit_cpt_types.py` reads them from the saved log.
  (The warning is not in `results/gobnilp-std-run.log`, probably because it goes to the error
  stream, which `tee` doesn't save. Step 1.5.0b re-checks this.)

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
scripts/add_bnsl_header.sh data/bn-data-44-bic.scores data/bn-data-44-bic-fixed.bnsl $(cat data/bn-data-44-varnames.txt)
```

How we found this: GOBNILP's example file `scores/chest_100_1_3.bnsl` (which Jirka pointed to
in his Aug 12 email) starts this way, and GOBNILP's reader source looks for `SCORES START`.

## 9. Gotchas

- **Windows line endings.** Files made on Windows end each line with `\r\n` (CRLF) instead of
  `\n` (LF). scoring2a and GOBNILP can misread them, and Jirka has been caught by this before.
  Check with `file <name>` ("with CRLF line terminators" means trouble). Fix a *copy* with
  `sed 's/\r$//' in > out`, never the original in `data/raw/`. `BN-data.csv` is already LF.
- **`bi.mat` is never written** (see 7d); use the console log.
- **Run from the project root** unless a script says otherwise.

## 10. Check list: everything works

```bash
git --version && python3 --version && R --version | head -1 && g++ --version | head -1
src/scoring2a | head -2                     # prints the usage message
which gobnilp                               # ~/.local/bin/gobnilp
Rscript -e 'library(bnlearn)'               # no error
bash scripts/run_gobnilp_pipeline.sh        # ends with objective value -64837.738627
```
