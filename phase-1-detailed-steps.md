# Phase 1, Fully Expanded — Reproduce the two-stage STD/MLR/OLR baseline

Revised against `paper_Kybernetika_2026_1.pdf` and the Jirka email thread —
corrections from the first draft are called out inline where they matter.

Assumes Phase 0 is complete: WSL Ubuntu VS Code window, `~/bn-project`,
`.venv` available, `scoring2a` compiled in `src/`, GOBNILP built (your own
build, not necessarily Jirka's old v1.6.3 — see note in 1.3), and
`data/BN-data.csv` copied in (this is the exact 44-variable file Jirka sent
Aug 5, already remapped to `{-1,0,1}` — do not re-derive it from
`preprocessed-data.csv` yourself; his email says to use the file he sent so
you're both working from identical data).

```bash
cd ~/bn-project
source .venv/bin/activate
```

---

## 1.0 Bring over two files from your earlier prototype repo

Your `bayesian-network-learning` repo already solved the GOBNILP-header
problem independently — and that fix is now *confirmed correct* against
Jirka's Aug 12 email (he pointed at
`bitbucket.org/jamescussens/gobnilp/.../chest_100_1_3.bnsl` as the reference
example; the only difference from raw scores is the variable-names line
plus `SCORES START`). Bring both files in rather than re-deriving them:

```bash
cp ~/bayesian-network-learning/scripts/add_bnsl_header.sh ~/bn-project/scripts/
cp ~/bayesian-network-learning/docs/bnsl_header ~/bn-project/docs/
chmod +x ~/bn-project/scripts/add_bnsl_header.sh
```
If not available locally, recreate:
```bash
cat > ~/bn-project/scripts/add_bnsl_header.sh << 'EOF'
#!/bin/bash
# Usage: ./add_bnsl_header.sh input.scores output.bnsl var1 var2 var3 ...
input="$1"
output="$2"
shift 2
echo "$@" > "$output"
echo "SCORES START" >> "$output"
cat "$input" >> "$output"
EOF
chmod +x ~/bn-project/scripts/add_bnsl_header.sh
```

**Note on GOBNILP version:** Jirka's own Kybernetika results used GOBNILP
1.6.3 / SCIP 3.2.1 (a 2016-era build on his Rocky Linux server) — but
Anika's newer self-built GOBNILP against SCIP 10.0.3 already works
correctly once the `.bnsl` header fix is applied (confirmed: "solved it in
about 3 seconds ... full parent set structure printed for all 23
variables"). No need to track down the old version — use what's already
working.

---

## 1.1 Convert `BN-data.csv` into `scoring2a`'s `.dat` format

`scripts/convert_data.py` — unchanged from before, still correct against
the paper (44 vars, k=3 states, values already in `{-1,0,1}`):

```python
# scripts/convert_data.py
import pandas as pd

SRC = "data/BN-data.csv"
DST = "data/bn-data-44.dat"

df = pd.read_csv(SRC)

uniq = sorted(pd.unique(df.values.ravel()))
print("Unique raw values found in BN-data.csv:", uniq)
expected = {-1, 0, 1}
if not set(uniq).issubset(expected):
    raise ValueError(
        f"Found values outside {expected}: {set(uniq) - expected}. "
        "This contradicts both the paper (Sec 4.1, k=3 states) and Jirka's "
        "own remapping code from his Aug 5 email -- investigate before proceeding."
    )

remap = {-1: 0, 0: 1, 1: 2}
df_remapped = df.apply(lambda col: col.map(remap))

nvars = df_remapped.shape[1]
nrows = df_remapped.shape[0]
print(f"nvars={nvars}, nrows={nrows}")  # expect nvars=44, nrows=1661 per paper Sec 4.1
arities = [3] * nvars  # paper confirms k=3 for every variable, uniformly

with open(DST, "w") as f:
    f.write(f"{nvars}\n")
    f.write(" ".join(str(a) for a in arities) + "\n")
    f.write(f"{nrows}\n")
    for _, row in df_remapped.iterrows():
        f.write(" ".join(str(int(v)) for v in row) + "\n")

with open("data/bn-data-44-varnames.txt", "w") as f:
    f.write(" ".join(df.columns))

print(f"Wrote {DST}")
```

```bash
python scripts/convert_data.py
```
Expect `nvars=44, nrows=1661` — the paper states 1661 respondents (Sec 4.1),
so if your row count differs, stop and investigate before continuing (could
mean `BN-data.csv` was modified, or contains a header/blank-row artifact).

**Line-ending check** (Jirka explicitly flagged CRLF vs LF as something he's
been bitten by before with these files):
```bash
file data/BN-data.csv
```
If it reports "with CRLF line terminators," strip them before anything
downstream touches the file:
```bash
sed -i 's/\r$//' data/BN-data.csv
```

---

## 1.2 Run the local scoring program

First, confirm the exact CLI syntax `scoring2a` expects:
```bash
cd ~/bn-project/src
./scoring2a          # usage message
cat script-data24-1  # the actual invocation Jirka's sample data used
cd ..
```

**Important — `alpha` and `palim` for the 44-variable run are not
confirmed anywhere in the paper or the email thread.** The paper doesn't
state these values, and Jirka's correspondence only discusses the pruning
*problem* in general, not this specific run's parameters. One soft signal:
every family in the paper's final model (Table 2) has **at most 2
parents** — if your own run with a given `palim` produces the same
pattern, that's a good consistency check; if it doesn't, that's worth
raising in Email #2 rather than silently picking a number. Start with
`palim=9` (generous upper bound, prunes down naturally) and `alpha=1`
(matches the paper's BIC convention with no extra scaling — see 1.4 for
why alpha=1 is the right choice given eq. 7/9), but treat this as your
working assumption, not a settled fact:
```bash
cd ~/bn-project/src
./scoring2a ../data/bn-data-44.dat 1 9 prune 0 bic > ../data/bn-data-44-bic.scores
cd ..
wc -l data/bn-data-44-bic.scores
head -5 data/bn-data-44-bic.scores    # first line should read "44"
```

---

## 1.3 Build the GOBNILP-ready `.bnsl` file and run GOBNILP

```bash
cd ~/bn-project
VARNAMES=$(cat data/bn-data-44-varnames.txt)
scripts/add_bnsl_header.sh data/bn-data-44-bic.scores data/bn-data-44-bic-fixed.bnsl $VARNAMES
head -5 data/bn-data-44-bic-fixed.bnsl   # var names, then "SCORES START", then 44, then data
```

Run GOBNILP, capturing console output (this is where the parent sets get
printed unambiguously — per Anika's Aug 18 confirmation that GOBNILP prints
"a full parent set structure ... for all 23 variables" directly):
```bash
cd src
cp ../data/bn-data-44-bic-fixed.bnsl .
gobnilp bn-data-44-bic-fixed.bnsl | tee ../results/gobnilp-std-run.log
cd ..
```
If this errors, check line endings first (`file data/bn-data-44-bic-fixed.bnsl`)
before assuming it's a deeper format problem — that's the specific failure
mode Jirka warned about.

```bash
cp src/bi.mat results/std-baseline-dag.txt
```

---

## 1.4 Fit MLR and OLR for each learned family, pick the best per node

This is the section that changed most. The paper gives exact, closed-form
parameter-count formulas — no need to approximate:

- STD: `Cv = (k−1)·k^n` (eq. 6), `BICv = LLv − (log|D|/2)·Cv` (eq. 9)
- MLR: `C'v = (k−1)·(1 + n·(k−1))` (eq. 12) — verified against paper Table 1
- OLR: `C''v = (k−1) + n` (eq. 17) — verified against paper Table 1

**Critical sign convention:** the paper's BIC (eq. 7/9) is
`LL − (log|D|/2)·C` — higher is better — and Algorithm 1 picks the CPT
type that *maximizes* this. This is the opposite convention from
statsmodels' built-in `.bic` attribute (which is `-2·LL + k·log(n)`, lower
is better) — don't mix the two. The script below computes everything
manually in the paper's convention and takes the max.

**MLR vs OLR predictor encoding differs** (this is in the paper, easy to
miss): MLR dummy-codes each parent (eq. 11, one dummy per non-reference
state); OLR uses each parent's raw value directly, one coefficient per
parent (eq. 16) — no dummy-coding for OLR.

```python
# scripts/fit_cpt_types.py
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.discrete.discrete_model import MNLogit
from statsmodels.miscmodels.ordinal_model import OrderedModel

DATA_CSV = "data/BN-data.csv"
GOBNILP_LOG = "results/gobnilp-std-run.log"
VARNAMES_FILE = "data/bn-data-44-varnames.txt"
OUT_SUMMARY = "results/cpt-type-summary.csv"

df = pd.read_csv(DATA_CSV)
with open(VARNAMES_FILE) as f:
    varnames = f.read().split()
assert list(df.columns) == varnames

n_obs = len(df)
k = 3  # every variable has 3 states -- paper Sec 4.1, confirmed by Jirka's remap code
w = np.log(n_obs) / 2.0  # penalty weight, paper eq. (7)/(9)

# ---- parse parent sets from the GOBNILP log from step 1.3 ----
with open(GOBNILP_LOG) as f:
    log_text = f.read()
print("---- inspect this before trusting the parser below ----")
print(log_text[:2000])
print("---------------------------------------------------------")

parents_by_var = {v: [] for v in varnames}
# TODO: fill in based on what you see printed above. GOBNILP's exact stdout
# format varies by version/build -- write the parsing logic to match your
# actual log, e.g. lines like "<child> <- <parent1> <parent2> ..." or a
# "Best DAG" block. Cross-check one parsed edge against results/std-baseline-dag.txt
# to confirm you haven't mixed up parent/child direction.

results = []
for v in varnames:
    parents = parents_by_var[v]
    n = len(parents)
    y = df[v]

    # ---------------- STD (general CPT) -- paper eq. (5), (6), (9) ----------------
    if parents:
        grp = df.groupby(parents)[v]
        ll_std = 0.0
        for _, sub in grp:
            counts = sub.value_counts()
            total = counts.sum()
            for c in counts:
                ll_std += c * np.log(c / total)
    else:
        counts = y.value_counts()
        total = counts.sum()
        ll_std = sum(c * np.log(c / total) for c in counts)
    Cv = (k - 1) * (k ** n)          # eq. (6) -- full k^n configs, not just observed ones
    bic_std = ll_std - w * Cv        # eq. (9)

    # ---------------- MLR -- paper eq. (10)-(13), param count eq. (12) ----------------
    if parents:
        # dummy-code each parent (eq. 11): ascending category order means the
        # lowest state (-1) is dropped as reference, matching the paper's xv,1
        # reference-state convention.
        X = pd.get_dummies(df[parents].astype("category"), drop_first=True).astype(float)
        X = sm.add_constant(X)
    else:
        X = pd.DataFrame({"const": np.ones(n_obs)})
    try:
        mlr_res = MNLogit(y.astype("category"), X).fit(disp=0)
        ll_mlr = mlr_res.llf
    except Exception as e:
        print(f"[{v}] MLR fit failed: {e}")
        ll_mlr = -np.inf
    Cv_mlr = (k - 1) * (1 + n * (k - 1))   # eq. (12)
    bic_mlr = ll_mlr - w * Cv_mlr

    # ---------------- OLR -- paper eq. (16)-(17); only if parents non-empty ----------------
    if parents:
        try:
            # raw parent values, NOT dummy-coded -- eq. (16) uses xpa(v) directly
            olr_res = OrderedModel(y, df[parents].astype(float), distr="logit").fit(method="bfgs", disp=0)
            ll_olr = olr_res.llf
        except Exception as e:
            print(f"[{v}] OLR fit failed: {e}")
            ll_olr = -np.inf
        Cv_olr = (k - 1) + n                # eq. (17)
        bic_olr = ll_olr - w * Cv_olr
    else:
        bic_olr = -np.inf  # OLR needs >=1 parent -- matches paper

    scores = {"STD": bic_std, "MLR": bic_mlr, "OLR": bic_olr}
    winner = max(scores, key=scores.get)    # Algorithm 1: maximize BIC (higher = better)
    results.append({
        "variable": v, "n_parents": n,
        "bic_std": bic_std, "bic_mlr": bic_mlr, "bic_olr": bic_olr,
        "winner": winner,
    })
    print(f"{v}: parents={parents} -> STD={bic_std:.2f} MLR={bic_mlr:.2f} OLR={bic_olr:.2f} -> {winner}")

out = pd.DataFrame(results)
out.to_csv(OUT_SUMMARY, index=False)
print(out["winner"].value_counts())
print(f"Saved {OUT_SUMMARY}")
```

Fill in the log parser, then run:
```bash
python scripts/fit_cpt_types.py
```

---

## 1.5 Validate against the paper

Compare against the paper's reported split: **19 STD (43%), 22 MLR (50%),
3 OLR (7%)**, and the claim that every family with more than one parent
used MLR or OLR (the paper's own text has a minor internal inconsistency
here — it says both "19 standard CPTs" and "all 17 standard CPTs
correspond to..." in adjacent sentences; just note this if you spot it,
it's not something to resolve on your end).

`docs/baseline-reproduction-notes.md`:
```markdown
# Baseline reproduction notes

## STD/MLR/OLR split
- Paper: 19 STD (43%), 22 MLR (50%), 3 OLR (7%)
- Mine: <fill in from results/cpt-type-summary.csv>

## Multi-parent nodes: did all use MLR/OLR?
<check n_parents > 1 rows against winner in the summary CSV>

## Max parent count sanity check
- Paper's final model (Table 2): no family has more than 2 parents
- Mine: <fill in -- if very different, alpha/palim in step 1.2 may not
  match what produced the paper's results; worth asking Jirka>

## Discrepancies and best guesses why
- <e.g. GOBNILP exact search (yours) vs. bnlearn hill-climbing (paper) -- see 1.6>
- <e.g. alpha/palim choice in scoring2a -- unconfirmed by paper/correspondence,
  see step 1.2>
```

---

## 1.6 (Optional but recommended) Cross-check with `bnlearn` in R

The paper's own reported structure was learned with `bnlearn`'s
hill-climbing, not GOBNILP's exact search (confirmed in Jirka's Aug 12
email: "I used the hill-climbing (hc) algorithm from the bnlearn R package
rather than GOBNILP... GOBNILP is needed to guarantee optimality"). This
makes this cross-check more than "optional" in practice — it's your
closest point of comparison to how the paper's own numbers were actually
produced:

```r
library(bnlearn)
d <- read.csv("data/BN-data.csv")
d[] <- lapply(d, as.factor)
dag <- hc(d, score = "bic")
print(dag)
write.csv(amat(dag), "results/bnlearn-hc-dag.csv")
```
Compare `results/bnlearn-hc-dag.csv` against `results/std-baseline-dag.txt`
(your GOBNILP exact-search result). Since the paper used hill-climbing,
your `bnlearn` structure is actually the more directly comparable one for
matching the paper's exact reported numbers — treat the GOBNILP result as
your "exact optimum" reference point, and the `bnlearn` result as the
paper-matching baseline.

---

## Commit everything

```bash
git add .
git commit -m "Phase 1: two-stage baseline reproduction"
git push
```

**EMAIL JIRKA #2 — "Baseline reproduced."** Send
`docs/baseline-reproduction-notes.md`. Given what's still unconfirmed,
specifically worth asking:
- What `alpha`/`palim` values were used for the 44-variable BIC run in the
  paper (unconfirmed by the paper text or correspondence so far).
- Whether comparing against `bnlearn::hc()` (matching his original method)
  or GOBNILP exact search (guaranteed optimal) is the more useful baseline
  for this project going forward, given Phase 3 will need exact search
  either way once CPT-type is folded into the objective.
