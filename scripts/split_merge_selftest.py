"""Prove the new split/merge counter sees events the old delta counter could not.

A split plus a merge in one interval leaves the component count unchanged: the old counter reported 0, the
new one must report 1 split and 1 merge.
"""
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from field_lab import label_components, match_events  # noqa: E402

fails = 0


def check(name, ok, detail=""):
    global fails
    print(f"{'OK  ' if ok else 'FAIL'} {name}{(' — ' + detail) if detail and not ok else ''}")
    if not ok:
        fails += 1


# --- case 1: one blob splits into two -------------------------------------------------
prev = np.zeros((20, 20), dtype=bool)
prev[8:12, 4:16] = True                      # one wide bar
now = np.zeros((20, 20), dtype=bool)
now[8:12, 4:9] = True                        # left half
now[8:12, 11:16] = True                      # right half, a gap in the middle
prev_lab, _ = label_components(prev)
now_lab, _ = label_components(now)
sp, mg = match_events(prev_lab, now_lab)
check("a split is counted", sp == 1, f"splits={sp}")
check("a split is not a merge", mg == 0, f"merges={mg}")

# --- case 2: two blobs merge into one -------------------------------------------------
sp2, mg2 = match_events(now_lab, prev_lab)
check("a merge is counted", mg2 == 1, f"merges={mg2}")
check("a merge is not a split", sp2 == 0, f"splits={sp2}")

# --- case 3: the case the old counter could not see -----------------------------------
# A splits into two AND two others merge into one: the component count is unchanged.
prev3 = np.zeros((30, 30), dtype=bool)
prev3[2:6, 2:14] = True        # bar A, will split
prev3[20:24, 2:8] = True       # blob B, will merge
prev3[20:24, 14:20] = True     # blob C, will merge
now3 = np.zeros((30, 30), dtype=bool)
now3[2:6, 2:7] = True          # A left
now3[2:6, 9:14] = True         # A right
now3[20:24, 2:20] = True       # B and C fused
prev3_lab, n_prev = label_components(prev3)
now3_lab, n_now = label_components(now3)
sp3, mg3 = match_events(prev3_lab, now3_lab)
check("the component count is unchanged", n_prev == n_now, f"{n_prev} -> {n_now}")
check("the old delta counter would report nothing", n_now - n_prev == 0, f"delta={n_now - n_prev}")
check("the new counter sees the split", sp3 == 1, f"splits={sp3}")
check("the new counter sees the merge", mg3 == 1, f"merges={mg3}")

print(f"\n[split-merge-selftest] провалов: {fails} из 8")
sys.exit(0 if fails == 0 else 1)
