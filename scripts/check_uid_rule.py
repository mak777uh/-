"""check_uid_rule.py — the identity rule of the field tracker, pinned as a data check.

Rule (03.11, X122/X123): with `--split-new-uid` a structure's uid ends when it divides. Every daughter of a split gets a new uid, and no daughter inherits the
mother's uid, so a parent's last logged appearance can never come *after* its child's first appearance.

This script checks the stored runs for that property and fails if any pair violates it — which would mean the identity rule changed, or a run used different flags,
and every survival statistic in the line would need re-reading.

    python scripts/check_uid_rule.py
    python scripts/check_uid_rule.py --limit 5
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"


def check_run(path: Path) -> list[str]:
    d = json.loads(path.read_text(encoding="utf-8"))
    params = d.get("params") or {}
    if not params.get("split_new_uid"):
        return []
    first: dict[int, int] = {}
    last: dict[int, int] = {}
    for row in d.get("series") or []:
        step = int(row.get("step") or 0)
        for c in row.get("components_log") or []:
            uid = int(c["uid"])
            first.setdefault(uid, step)
            last[uid] = step
    problems = []
    for a, b in d.get("uid_pairs") or []:
        parent, child = int(a), int(b)
        if parent not in last or child not in first:
            continue
        if last[parent] > first[child]:
            problems.append(f"{path.name}: parent {parent} last at {last[parent]} after child {child} first at {first[child]}")
    return problems


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="pin the tracker's identity rule on stored runs")
    ap.add_argument("--limit", type=int, default=0, help="check only the first N runs")
    args = ap.parse_args(argv)
    runs = sorted(p for p in L1.glob("x108_*_s*.json") if not p.name.endswith(".compact.json"))
    if args.limit:
        runs = runs[: args.limit]
    if not runs:
        print("[uid-rule] no x108 runs found — nothing to check")
        return 0
    problems: list[str] = []
    pairs_checked = 0
    for path in runs:
        problems.extend(check_run(path))
        d = json.loads(path.read_text(encoding="utf-8"))
        pairs_checked += len(d.get("uid_pairs") or [])
    print(f"[uid-rule] runs: {len(runs)}, pairs checked: {pairs_checked}")
    for p in problems[:10]:
        print(f"[uid-rule] ВНИМАНИЕ: {p}")
    if problems:
        print(f"[uid-rule] НАРУШЕНИЙ: {len(problems)} — the identity rule is not what the analyses assume")
        return 1
    print("[uid-rule] OK — no parent outlives its child's birth")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
