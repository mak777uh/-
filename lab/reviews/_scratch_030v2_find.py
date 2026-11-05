#!/usr/bin/env python
"""_scratch_030v2_find.py — locate scalar values inside E09_pond aggregates.

Usage (from repo root):
  python lab/reviews/_scratch_030v2_find.py <agg-name> <value> [<value> ...]
Finds every JSON path whose scalar equals a target within 1e-9 (also tries the value
rounded to 2/3/4/5 decimals), so the reviewer can check a printed number against the
exact stored field without dumping whole files.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POND = ROOT / "morphogenesis" / "experiments" / "E09_pond"


def leaves(o, path=""):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from leaves(v, f"{path}.{k}" if path else k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from leaves(v, f"{path}[{i}]")
    else:
        yield path, o


def main():
    name = sys.argv[1]
    targets = [float(x) for x in sys.argv[2:]]
    d = json.loads((POND / f"l1_field_{name}.json").read_text(encoding="utf-8"))
    hits = {t: [] for t in targets}
    for path, val in leaves(d):
        if isinstance(val, bool) or not isinstance(val, (int, float)):
            continue
        for t in targets:
            for r in (t, round(t, 2), round(t, 3), round(t, 4), round(t, 5), round(t, 6)):
                if abs(float(val) - r) <= 1e-9:
                    hits[t].append((path, val))
                    break
    for t in targets:
        print(f"--- {t}")
        seen = set()
        for path, val in hits[t]:
            if (path, val) in seen:
                continue
            seen.add((path, val))
            print(f"    {path} = {val}")
        if not hits[t]:
            print("    (no exact match)")


if __name__ == "__main__":
    main()
