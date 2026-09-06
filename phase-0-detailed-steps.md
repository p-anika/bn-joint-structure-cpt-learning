# Phase 0, Fully Expanded — for Windows (HP OmniBook)

The HP OmniBook runs **Windows 11**. This changes some Phase 0 steps, so
here's the expanded, Windows-specific version. Check your build first:
**Start menu → type "About your PC" → Enter** — under "Windows
specifications" you'll see the edition/version. Anything Windows 10 22H2+
or Windows 11 works fine for everything below.

## 0.0 A key decision: WSL2 vs. native Windows

`scoring2a.c` needs a C++ compiler, and GOBNILP needs to be built against
SCIP — both are pieces of research software that are documented and tested
almost exclusively on Linux/Mac. Getting them to build with native Windows
tools (Visual Studio's compiler, etc.) is possible but fiddly and not
something their docs walk you through.

**Recommended path: install WSL2 (Windows Subsystem for Linux).** This
gives you a real Ubuntu Linux environment running inside Windows, which you
control from the same VS Code window. Compiling C code, installing SCIP/
GOBNILP, and following any Linux-oriented instructions (including the R
package installs) will all just work the way the documentation assumes.
This is genuinely the standard setup research-software users on Windows
reach for — it's not a workaround, it's the normal path.

Everything below assumes WSL2. It only takes about 15 extra minutes over a
native install and saves you from debugging compiler errors later.

---

## 0.1 Install WSL2 + Ubuntu

**Check if you already have it:**
Open **PowerShell** (Start menu → type "PowerShell" → click "Windows
PowerShell" — regular, not admin, is fine for this check) and run:
```powershell
wsl --list --verbose
```
- If you see an error like "wsl is not recognized" or "no distributions
  are installed" → you don't have it yet, proceed below.
- If you see `Ubuntu` listed with `VERSION 2` → you already have it, skip
  to 0.2.

**Install it:**
1. Close that PowerShell window, right-click the **Start menu**, choose
   **"Terminal (Admin)"** (or "Windows PowerShell (Admin)" — you need
   Administrator this time, unlike the check above).
2. Click "Yes" on the User Account Control prompt.
3. Run:
   ```powershell
   wsl --install
   ```
   This installs WSL2 and Ubuntu (the default distro) in one step. It will
   download several hundred MB — let it finish.
4. **Restart your laptop** when it asks you to (this step is required, WSL
   needs a reboot to enable the underlying Windows feature).
5. After restart, Ubuntu should launch automatically in a terminal window
   and ask you to create a **UNIX username and password**. Pick something
   simple (e.g. your first name, lowercase). This username/password is
   local to Ubuntu only — it has nothing to do with your Windows login or
   GitHub. **Write the password down somewhere** — you'll need it for
   `sudo` commands, and the terminal won't show characters as you type it
   (that's normal, not a bug).
6. Once you have a `username@HOSTNAME:~$` prompt, WSL is working. From now
   on, open it anytime via Start menu → type "Ubuntu" → click it.

**Update it before doing anything else** (always do this first on a fresh
Ubuntu install):
```bash
sudo apt update && sudo apt upgrade -y
```
This will ask for the Ubuntu password you just created. Let it finish (a
few minutes).

---

## 0.2 Install VS Code (on Windows) + connect it to WSL

**Check if you already have it:** Start menu → type "Visual Studio Code".
If it appears, you have it — open it and skip to the extensions step.

**Install it:**
1. In your regular Windows browser, go to https://code.visualstudio.com/
2. Click the big blue **Download for Windows** button.
3. Run the downloaded installer. On the "Select Additional Tasks" screen,
   make sure **"Add to PATH"** is checked (it is by default) — leave
   everything else default. Click through to Install, then Finish.
4. VS Code should open automatically.

**Install extensions** (click the Extensions icon in the far-left sidebar —
it looks like four squares with one detached — then use the search box at
the top of that panel):
- Search **"WSL"** → install the one by Microsoft called **"WSL"**. This
  is the critical one — it lets VS Code edit and run files that live
  inside your Ubuntu environment.
- Search **"Python"** → install the Microsoft one (Pylance installs
  alongside it automatically).
- Search **"R"** → install the one by REditorSupport (only needed if
  you'll edit `.R` files directly in VS Code rather than RStudio).
- Search **"C/C++"** → install the Microsoft one.
- Search **"GitLens"** → optional, install if you want richer Git history
  views.

**Connect VS Code to Ubuntu:**
1. Press `F1` (or `Ctrl+Shift+P`) to open the command palette.
2. Type "WSL: Connect to WSL" and press Enter.
3. A new VS Code window opens — check the bottom-left corner: it should
   now say **"WSL: Ubuntu"**. Everything you do in this window (terminal,
   file editing, extensions) now runs inside Linux, not Windows. **This is
   the window you'll work in for the rest of the project.**
4. Open a terminal inside this window: **Terminal → New Terminal** (or
   `` Ctrl+` ``). You should get the same `username@HOSTNAME:~$` Ubuntu
   prompt as before, but now it's embedded in VS Code.

---

## 0.3 Check for / install Git (inside the WSL/Ubuntu terminal in VS Code)

**Check:**
```bash
git --version
```
Ubuntu via `wsl --install` usually ships with Git already. If you see a
version number (e.g. `git version 2.43.0`), skip installing — go straight
to the config step below. If you see "command not found":
```bash
sudo apt install git -y
```

**Configure Git identity (do this once, regardless of whether it was
already installed):**
```bash
git config --global user.name "Anika Prakash"
git config --global user.email "prakashanika5@gmail.com"
```

---

## 0.4 Check for / install Python (inside WSL)

**Check:**
```bash
python3 --version
```
Ubuntu ships with Python 3 pre-installed. If it shows `Python 3.10` or
higher, you're set. Also check pip:
```bash
pip3 --version
```
If pip is missing:
```bash
sudo apt install python3-pip python3-venv -y
```
(`python3-venv` is needed for the virtual environment step in 0.5 of the
main task list — install it now even if pip is already present, since it's
a separate package on Ubuntu.)

---

## 0.5 Check for / install R (inside WSL)

**Check:**
```bash
R --version
```
If it prints a version, you already have it. If "command not found":
```bash
sudo apt install --no-install-recommends r-base -y
```
This takes a few minutes — R has a lot of dependencies.

**Verify it works:**
```bash
R
```
This should drop you into the R interactive console (prompt changes to
`>`). Type `q()` and press Enter, then answer `n` when it asks about
saving workspace image, to exit back to the bash prompt.

**Install the R packages you'll need** (do this from inside the R console
— run `R` to enter it, then paste this and press Enter):
```r
install.packages(c("bnlearn", "nnet", "MASS", "qgraph"))
```
- The first time you run this, R may ask "Would you like to use a
  personal library... y/n" — answer **y**, then **y** again if asked to
  create the directory. It may also ask you to pick a CRAN mirror — pick
  any (0-Cloud is usually the first option and works globally).
- This step can take 5–10 minutes and will print a lot of compilation
  output — that's normal, not an error, as long as it doesn't stop with
  a message containing "ERROR" at the end.
- When it finishes, verify by running `library(bnlearn)` — no error output
  means it worked. Exit with `q()`, answer `n`.

---

## 0.6 Check for / install a C++ compiler (inside WSL)

**Check:**
```bash
g++ --version
```
**Install (covers gcc, g++, make, and other build essentials at once):**
```bash
sudo apt install build-essential -y
```
Re-run `g++ --version` afterward to confirm.

---

## 0.7 Set up your project folder (inside WSL)

Decide where in the Linux filesystem your project lives — **do not** put
it under `/mnt/c/...` (that's your Windows C: drive mounted into Linux;
file operations there are noticeably slower and can cause permission
issues). Keep it inside Linux's own filesystem instead:
```bash
cd ~
mkdir -p bn-project/{data,src,scripts,notebooks,results,docs}
cd bn-project
```
Open this exact folder as your VS Code workspace: **File → Open Folder…**
→ navigate to `/home/<your-username>/bn-project` → Open. (You're still in
the "WSL: Ubuntu" VS Code window from step 0.2 — the folder picker will
show you the Linux filesystem, not Windows drives.)

---

## 0.8 Create the GitHub repo and connect it

1. In your regular Windows browser: https://github.com → sign in (or
   **Sign up** if you don't have an account yet) → click the **+** icon
   top-right → **New repository**.
2. Repository name: `bn-joint-structure-cpt-learning` (or similar).
   Visibility: Private is fine. Leave "Add a README" unchecked. Click
   **Create repository**.
3. Back in the VS Code (WSL) terminal, inside `~/bn-project`:
   ```bash
   git init
   git branch -M main
   ```
4. **Set up authentication** (GitHub no longer accepts your account
   password for `git push` — you need either an SSH key or a Personal
   Access Token). SSH is the more "set it and forget it" option:
   ```bash
   ssh-keygen -t ed25519 -C "prakashanika5@gmail.com"
   ```
   - Press Enter to accept the default file location.
   - You can press Enter twice more to skip setting a passphrase (simpler
     for now), or set one if you prefer extra security.
   - Then print your new public key:
     ```bash
     cat ~/.ssh/id_ed25519.pub
     ```
   - Copy the entire output line (starts with `ssh-ed25519`).
   - In your browser: GitHub → click your profile picture (top right) →
     **Settings** → left sidebar **SSH and GPG keys** → **New SSH key** →
     paste it in → give it a title like "HP OmniBook WSL" → **Add SSH
     key**.
5. Connect your local repo to GitHub using the SSH URL (on the repo's
   GitHub page, click the green **Code** button → make sure **SSH** tab is
   selected, not HTTPS → copy that URL, it looks like
   `git@github.com:<username>/bn-joint-structure-cpt-learning.git`):
   ```bash
   git remote add origin git@github.com:<your-username>/bn-joint-structure-cpt-learning.git
   ```
6. Test the connection:
   ```bash
   ssh -T git@github.com
   ```
   First time, it'll ask "Are you sure you want to continue connecting?"
   → type `yes`. You should see "Hi <username>! You've successfully
   authenticated..."
7. Make your first commit and push:
   ```bash
   echo "# BN Joint Structure + CPT-Type Learning" > README.md
   git add .
   git commit -m "Initial project structure"
   git push -u origin main
   ```
8. Refresh the GitHub page in your browser — you should see your files
   there.

---

## 0.9 Python virtual environment (inside WSL, inside `~/bn-project`)

```bash
python3 -m venv .venv
source .venv/bin/activate
```
Your terminal prompt should now start with `(.venv)`. In VS Code, it
should also prompt "We noticed a new environment..." — click **Yes** to
use it, or manually: `Ctrl+Shift+P` → "Python: Select Interpreter" → pick
the one showing `./.venv/bin/python`.

Install packages:
```bash
pip install numpy pandas scipy statsmodels scikit-learn matplotlib jupyter
```

Add `.venv/` to `.gitignore` so it never gets committed (it's large and
machine-specific):
```bash
echo -e "__pycache__/\n*.pyc\n.venv/\n.Rhistory\n.RData\nresults/*.mat" > .gitignore
git add .gitignore
git commit -m "Add gitignore"
git push
```

---

## 0.10 Compile `scoring2a.c`

Copy `scoring2a.c` from your uploads into `~/bn-project/src/` (easiest way:
in the WSL VS Code window's file explorer panel, drag-and-drop the file
from Windows File Explorer straight into the `src` folder — WSL-integrated
VS Code allows this).

```bash
cd ~/bn-project/src
g++ -O2 -o scoring2a scoring2a.c -lm
./scoring2a
```
The last command with no arguments should print the usage message
(`Usage: scoring datafile alpha parentslimit...`) — that confirms it
compiled correctly.

---

## 0.11 Install GOBNILP (the involved one — budget real time for this)

GOBNILP depends on **SCIP**, a separate optimization solver, which must be
built/installed first.

1. Go to https://scipopt.org/index.php#download and get the SCIP Optimization
   Suite source (or check if a prebuilt Linux package is offered — read
   the page, options change over time).
2. Follow SCIP's own build instructions inside your WSL Ubuntu terminal —
   this typically involves `cmake` and `make`, so also ensure you have
   those:
   ```bash
   sudo apt install cmake -y
   ```
3. Once SCIP is built and installed, get GOBNILP:
   ```bash
   cd ~/bn-project/src
   git clone https://bitbucket.org/jamescussens/gobnilp.git
   cd gobnilp
   ```
   Follow the build instructions in GOBNILP's own README/INSTALL file
   (it needs to be pointed at your SCIP install location — the exact
   variable/flag names are documented there and can change between
   versions, so follow their file directly rather than a fixed command
   here).
4. **Alternative if this gets painful:** try `pygobnilp` instead, which
   some users find simpler to get working:
   ```bash
   pip install pygobnilp
   ```
   Note this may still expect a working SCIP/GOBNILP install underneath —
   read `pygobnilp`'s own docs (https://pygobnilp.readthedocs.io/en/latest/)
   before assuming `pip install` alone is sufficient.
5. **This step is the single most likely place to hit a wall** — build
   systems for research optimization software are notoriously fiddly. If
   you get stuck after a genuine attempt, this is a completely reasonable
   thing to flag to Jirka early (he's used it before and may have
   version-specific tips) rather than losing days to it alone.

Test it once installed:
```bash
cp /path/to/your/gobnilp.set ~/bn-project/src/
cd ~/bn-project/src
gobnilp data24-training-1-bic.scores
```
(swap in wherever you actually placed `data24-training-1-bic.scores`, e.g.
`~/bn-project/data/`) — this should run without error and produce an
adjacency matrix output file (`bi.mat`, per `gobnilp.set`'s setting).

---

## 0.12 Final Phase 0 checklist

Run each of these in the WSL terminal — every one should return a version
number or expected output, no "command not found" errors:
```bash
git --version
python3 --version
pip3 --version
R --version
g++ --version
./scoring2a          # from inside ~/bn-project/src — should print usage text
gobnilp --version    # or however your build reports its version
```
And confirm:
- [ ] VS Code bottom-left corner says "WSL: Ubuntu" when you're working
- [ ] `git push` works without asking for a password (SSH key is working)
- [ ] `(.venv)` shows in your terminal prompt when you `cd` into the
      project and activate it
- [ ] `library(bnlearn)` loads with no error in R
- [ ] GOBNILP produced `bi.mat` (or equivalent) on the sample scores file

Once every box is checked, you're ready for **📧 Email Jirka #1** from the
main task list, and then Phase 1.
