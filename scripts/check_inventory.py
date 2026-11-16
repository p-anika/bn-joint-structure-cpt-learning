"""Inventory check: every tracked file must be listed in its folder's README (CLAUDE.md rule).

For each file that git tracks (`git ls-files`), the script finds the README.md of the folder
the file is in, or, if that folder has none, the closest README.md above it. The file
passes if that README mentions it, by file name or by its path relative to the README's
folder. README.md files themselves are not checked.

Run:    python scripts/check_inventory.py      (or: make inventory)
Output: the list of files no README mentions; exit code 1 if there are any, 0 if none.

Example output:
    All 81 tracked files are listed in a README.
"""

import subprocess
import sys
from pathlib import Path

from bnjoint import config


def tracked_files(repo: Path) -> list[Path]:
    """Paths (relative to the repo) of every file git tracks.

    Example:
        >>> Path("Makefile") in tracked_files(config.REPO_ROOT)
        True
    """
    out = subprocess.run(
        ["git", "ls-files"], cwd=repo, capture_output=True, text=True, check=True
    ).stdout
    return [Path(line) for line in out.splitlines() if line]


def nearest_readme(repo: Path, rel: Path) -> Path | None:
    """The README.md in `rel`'s folder, or the closest one in a folder above it.

    Example:
        >>> nearest_readme(config.REPO_ROOT, Path("data/raw/BN-data.csv"))
        PosixPath('data/raw/README.md')
    """
    for folder in rel.parents:  # e.g. data/raw, data, . (the repo root)
        candidate = folder / "README.md"
        if (repo / candidate).exists():
            return candidate
    return None


def undocumented(repo: Path) -> list[Path]:
    """Tracked files that their nearest README does not mention."""
    missing = []
    for rel in tracked_files(repo):
        if rel.name == "README.md":
            continue
        readme = nearest_readme(repo, rel)
        if readme is None:
            missing.append(rel)
            continue
        text = (repo / readme).read_text()
        relative_to_readme = rel.relative_to(readme.parent).as_posix()
        if rel.name not in text and relative_to_readme not in text:
            missing.append(rel)
    return missing


def main() -> None:
    """Print the undocumented files and exit with 1 if there are any."""
    repo = config.REPO_ROOT
    missing = undocumented(repo)
    if missing:
        print("Tracked files not listed in their folder's README:")
        for rel in missing:
            print(f"  {rel}")
        sys.exit(1)
    print(f"All {len(tracked_files(repo))} tracked files are listed in a README.")


if __name__ == "__main__":
    main()
