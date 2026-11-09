"""Inheritance, stratified by how the cell was born.

Why. A cell can arrive in this world by two different paths, and the question "is the trait inherited" has a
different answer for each:

  * **activation** (birth_mode = 1) - grown by the rule, the genome came from the value pre-assigned to that
    grid position. There is no parent, so nothing is inherited: the trait was always there.
  * **reproduction** (birth_mode = 2) - budded, the genome came from the parent with mutation. Here there IS a
    parent, and a parent-child correlation is a measurement of transmission.

Pooling the two gives a number that is neither. This script reports them separately.

Usage:
  python scripts/inheritance_by_birth.py --dir morphogenesis/experiments/E19
"""
from __future__ import annotations
import argparse
import glob
import json
import os
import statistics
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODE_NAMES = {0: "never born", 1: "activation", 2: "reproduction"}


def read_run(path: str) -> dict | None:
    try:
        with open(path, encoding="utf-8") as fh:
            d = json.load(fh)
    except Exception:  # noqa: BLE001
        return None
    return d


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    args = ap.parse_args(argv)

    directory = args.dir if os.path.isabs(args.dir) else os.path.join(ROOT, args.dir)
    files = sorted(glob.glob(os.path.join(directory, "*.json")))
    if not files:
        print(f"[inherit] no artifacts in {directory}")
        return 1

    # birth_mode is a per-cell grid; the artifact records it in the summary as counts if it records it at all
    counts: dict[str, int] = {}
    runs_with_mode = 0
    for p in files:
        d = read_run(p)
        if not d:
            continue
        summary = d.get("summary") or {}
        bm = summary.get("birth_mode_counts")
        if bm:
            runs_with_mode += 1
            for k, v in bm.items():
                counts[str(k)] = counts.get(str(k), 0) + int(v)

    print(f"[inherit] artifacts: {len(files)}, with birth_mode counts: {runs_with_mode}")
    if not runs_with_mode:
        print()
        print("[inherit] the artifacts do NOT record how each cell was born, so an inheritance analysis")
        print("          cannot be stratified. This is the finding: the field exists in the world")
        print("          (`run_pond.birth_mode`) but never reaches the artifact.")
        print()
        print("          What the next run must record: `birth_mode_counts` = {1: n_activation, 2: n_reproduction}")
        print("          in the summary, and the per-cell mode in `k_steps`.")
        return 1

    total = sum(counts.values())
    print()
    print(f"{'mode':16s} {'cells':>8s} {'share':>8s}")
    for mode in sorted(counts, key=lambda x: int(x)):
        n = counts[mode]
        name = MODE_NAMES.get(int(mode), f"unknown {mode}")
        print(f"{name:16s} {n:8d} {n / total:8.3f}")
    print()
    act = counts.get("1", 0)
    rep = counts.get("2", 0)
    if act == 0:
        print("[inherit] NO cell arrived by activation: every birth was a reproduction, so the trait of every")
        print("          cell came from a parent and the inheritance question is well posed")
    elif rep == 0:
        print("[inherit] NO cell arrived by reproduction: every birth was an activation, so nothing is")
        print("          inherited and a parent-child correlation would measure the pre-assigned field")
    else:
        print(f"[inherit] both paths are present: activation {act / total:.2f}, reproduction {rep / total:.2f}")
        print("          a pooled inheritance number would mix transmission with pre-assignment; report them apart")
    return 0


if __name__ == "__main__":
    sys.exit(main())
