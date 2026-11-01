"""check_claim_artifacts.py — an artifact cited by a claim must exist in git.

The claims matrix names its evidence: aggregate paths in `lab/claims/*.json`, and artifact file names in the rows of
`manuscript/CLAIMS.md`. Nothing checked that those files were actually in the repository, so a row could cite an artifact
that only ever existed in a scratch directory — which is exactly what `X35` spent an hour discovering by hand.

What counts as a violation: a cited `.json` that is neither tracked by git nor present on disk, after normalising the
relative prefixes (`../`, `./`) against the citing file. `_hourly/` references are exempt here and counted by
`check_hourly_refs.py` with its own baseline, because that is a known, documented gap rather than a new one.

    python scripts/check_claim_artifacts.py            # report
    python scripts/check_claim_artifacts.py --ci       # fail on any violation
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
CLAIMS = ROOT / "manuscript" / "CLAIMS.md"
SPECS = ROOT / "lab" / "claims"


def tracked_files() -> tuple[set[str], dict[str, list[str]]]:
    out = subprocess.run(["git", "ls-files"], cwd=str(ROOT), capture_output=True, text=True,
                         encoding="utf-8", errors="replace").stdout.split()
    tracked = set(out)
    by_name: dict[str, list[str]] = collections.defaultdict(list)
    for path in out:
        by_name[pathlib.Path(path).name].append(path)
    return tracked, by_name


def tokens(text: str) -> list[str]:
    return re.findall(r"[\w./\-]+\.json", text)


def resolve(token: str, base: pathlib.Path, tracked: set[str], by_name: dict[str, list[str]]) -> str:
    """Return 'ok', 'exempt' or 'missing' for one cited token."""
    if token.startswith("_hourly/"):
        return "exempt"
    if "/" in token:
        raw = token.lstrip("./")
        candidates = [raw, str((base / token).resolve().relative_to(ROOT)).replace("\\", "/")]
        for cand in candidates:
            cand = cand.lstrip("./")
            if cand in tracked or (ROOT / cand).exists():
                return "ok"
        return "missing"
    return "ok" if token in by_name else "missing"


def collect() -> dict:
    tracked, by_name = tracked_files()
    report = {"sources": {}, "missing": [], "exempt": 0, "tokens": 0}
    sources = [CLAIMS] + sorted(SPECS.glob("*.json"))
    for path in sources:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        rows = []
        for tok in sorted(set(tokens(text))):
            report["tokens"] += 1
            verdict = resolve(tok, path.parent, tracked, by_name)
            if verdict == "exempt":
                report["exempt"] += 1
            elif verdict == "missing":
                rows.append(tok)
                report["missing"].append({"source": str(path.relative_to(ROOT)).replace("\\", "/"), "token": tok})
        report["sources"][str(path.relative_to(ROOT)).replace("\\", "/")] = rows
    return report


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="cited artifacts must be in git")
    ap.add_argument("--ci", action="store_true")
    args = ap.parse_args(argv)

    rep = collect()
    print(f"[claim-artifacts] источников: {len(rep['sources'])}, токенов .json: {rep['tokens']}, "
          f"исключено (_hourly, см. check_hourly_refs): {rep['exempt']}, битых: {len(rep['missing'])}")
    for row in rep["missing"][:10]:
        print(f"    {row['source']}: {row['token']}")
    if args.ci and rep["missing"]:
        print("[claim-artifacts] ПРОВАЛ: утверждение ссылается на артефакт, которого нет в git")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
