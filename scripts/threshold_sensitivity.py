"""Q8: how much do the lifetimes and division counts depend on the matching threshold?

The literature says 0.5 is not canonical and that the choice has measurable consequences. This script runs the
same world at several thresholds and reports what moves. If a conclusion about reproduction changes under a
small change of threshold, the conclusion is about the threshold, not about the world.

The threshold is `min_overlap` in match_events, which compares a parent's share with the BEST share of that
child (a relative rule). The sweep is over that fraction.

Usage:
  python scripts/threshold_sensitivity.py            # report
"""
from __future__ import annotations
import importlib.util
import io
import json
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("fl", os.path.join(ROOT, "scripts", "field_lab.py"))
fl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fl)

THRESHOLDS = (0.2, 0.3, 0.5, 0.7)


def synthetic_pair(seed: int = 5):
    """A previous snapshot and a current one with a known split and a known merge."""
    rng = np.random.default_rng(seed)
    prev = np.zeros((48, 48), dtype=bool)
    now = np.zeros((48, 48), dtype=bool)
    # a bar that splits into two
    prev[5:9, 5:21] = True
    now[5:9, 5:12] = True
    now[5:9, 14:21] = True
    # two blobs that merge into one
    prev[30:36, 5:12] = True
    prev[30:36, 16:23] = True
    now[30:36, 5:23] = True
    # a lone blob that just moves
    prev[20:24, 30:34] = True
    now[21:25, 31:35] = True
    return prev, now


def main() -> int:
    prev, now = synthetic_pair()
    prev_lab, n_prev = fl.label_components(prev)
    now_lab, n_now = fl.label_components(now)
    print(f"previous components: {n_prev}, current: {n_now}")
    print(f"component count delta: {n_now - n_prev} (the old counter would report this)")
    print()
    print(f"{'threshold':>10s} {'splits':>8s} {'merges':>8s}")
    rows = []
    for th in THRESHOLDS:
        sp, mg = fl.match_events(prev_lab, now_lab, min_overlap=th)
        rows.append((th, sp, mg))
        print(f"{th:10.1f} {sp:8d} {mg:8d}")

    sps = {r[1] for r in rows}
    mgs = {r[2] for r in rows}
    print()
    if len(sps) == 1 and len(mgs) == 1:
        print("[threshold] the counts do NOT depend on the threshold in this case")
    else:
        print(f"[threshold] THE COUNTS DEPEND ON THE THRESHOLD: splits {sorted(sps)}, merges {sorted(mgs)}")
        print("            a conclusion that changes with the threshold is about the threshold")
    return 0


if __name__ == "__main__":
    sys.exit(main())
