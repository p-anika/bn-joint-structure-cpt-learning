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