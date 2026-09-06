import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.discrete.discrete_model import MNLogit
from statsmodels.miscmodels.ordinal_model import OrderedModel
import re

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


pattern = re.compile(r'^(\w+):-\{([^}]*)\}\s+1\s+\(obj:')
for line in log_text.splitlines():
    m = pattern.match(line.strip())
    if m:
        child, parents_str = m.groups()
        parents_by_var[child] = [p.strip() for p in parents_str.split(',') if p.strip()]

n_with_parents = sum(1 for v in varnames if parents_by_var[v])
print(f"Parsed {len(parents_by_var)} variables; {n_with_parents} have >=1 parent")



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
        expected_cols = 1 + n * (k - 1)
        if X.shape[1] != expected_cols:
            print(f"[{v}] WARNING: expected {expected_cols} MLR predictor columns, got {X.shape[1]} "
                f"-- a parent is missing one of its 3 states in this data; Cv_mlr formula may not match the actual fit.")
    else:
        X = pd.DataFrame({"const": np.ones(n_obs)})
    try:
        mlr_res = MNLogit(y, X).fit(disp=0)
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