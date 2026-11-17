"""Read the learned network out of a GOBNILP console log.

Input:  a log saved with `gobnilp -f file.bnsl -s tools/gobnilp/gobnilp.set | tee <log>`,
        e.g. `results/phase-1/gobnilp-std-run.log`.
Output: a dict {child: [parents]} for every variable.

Why the log and not `bi.mat`: this GOBNILP version ignores the `adjacencymatrix` setting in
`gobnilp.set`, so `bi.mat` is never written (decision log entry 6). After solving, GOBNILP
prints the solution, one line per family (a node and its parents):

    a1:-{a19,a27}                                       1 	(obj:-1410.601461)
    d11:-{}                                             1 	(obj:-1816.216798)

`a1:-{a19,a27}` means "a1 has parents a19 and a27" (`:-` is read "given"), `1` means this
family is chosen, and `obj` is its local BIC score. Further down the log repeats each arc on
its own line (`a1:-a19   1  (obj:0)`); those have no braces and are ignored.
"""

import re

# ^(\w+)      the child's name at the start of the line
# :-\{(...)\} the parents inside braces (may be empty)
# \s+1\s+\(obj:  "1" (family selected) followed by "(obj:" -- this skips the arc-only lines
FAMILY_LINE = re.compile(r"^(\w+):-\{([^}]*)\}\s+1\s+\(obj:")


def parse_parent_sets(log_text: str, varnames: list[str]) -> dict[str, list[str]]:
    """Return {child: [parents in the order GOBNILP prints them]} for every variable.

    Args:
        log_text: the whole GOBNILP console log.
        varnames: all variable names; every one must appear exactly in the log.

    Returns:
        A dict with one entry per name in `varnames`, in the order of `varnames`.

    Raises:
        ValueError: if the log has a family for an unknown variable, or misses one.

    Example:
        >>> parse_parent_sets("a3:-{a4}   1 \\t(obj:-1142.5)\\na4:-{}  1 (obj:-9)", ["a3", "a4"])
        {'a3': ['a4'], 'a4': []}
    """
    found: dict[str, list[str]] = {}
    for line in log_text.splitlines():
        match = FAMILY_LINE.match(line.strip())
        if match:
            child, parents_str = match.groups()
            found[child] = [p.strip() for p in parents_str.split(",") if p.strip()]

    unknown = sorted(set(found) - set(varnames))
    if unknown:
        raise ValueError(f"GOBNILP log has families for unknown variables: {unknown}")
    missing = [v for v in varnames if v not in found]
    if missing:
        raise ValueError(f"GOBNILP log has no family line for: {missing}")
    return {v: found[v] for v in varnames}
