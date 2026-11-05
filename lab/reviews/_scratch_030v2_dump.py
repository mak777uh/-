#!/usr/bin/env python
"""_scratch_030v2_dump.py — reviewer helper: print the structure/scalars of an E09_pond aggregate.

Usage (from repo root): python lab/reviews/_scratch_030v2_dump.py x157_gap_geometry x157_quantum ...
Prints every JSON path that holds a scalar, plus list/dict sizes. No lab analysis code is used.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POND = ROOT / "morphogenesis" / "experiments" / "E09_pond"


def walk(o, path=""):
    if isinstance(o, dict):
        for k, v in o.items():
            walk(v, f"{path}.{k}" if path else k)
    elif isinstance(o, list):
        print(f"{path} :: list[{len(o)}]")
        if o and isinstance(o[0], (dict, list)):
            walk(o[0], f"{path}[0]")
        elif o:
            print(f"{path} = {json.dumps(o)[:300]}")
    else:
        print(f"{path} = {json.dumps(o, ensure_ascii=False)}")


def main():
    for name in sys.argv[1:]:
        p = POND / f"l1_field_{name}.json"
        print("=" * 100)
        print(name)
        print("=" * 100)
        d = json.loads(p.read_text(encoding="utf-8")) if p.exists() else None
        if d is None:
            print("  !! MISSING", p)
            continue
        walk(d)


if __name__ == "__main__":
    main()
