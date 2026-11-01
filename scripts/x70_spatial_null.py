"""x70_spatial_null.py — the control the four answers asked for: is the size signal just neighbours sharing a place?

X70 found a parent–daughter correlation in peak area of 0.334 that exceeds a *pairing* null (p95 = 0.054). But parent and
daughter sit next to each other and share the local inflow, so a correlation is expected even with zero transmission. The
right control is a **non-parent structure at the same distance at the same time**: if that also correlates with the
daughter, the signal is the place, not the parent.

Method, per division event (parent uid, child uid):

1. child's birth step `T` from `uid_outcomes.first`;
2. the last snapshot at or before `T - 1` gives the parent's centroid; the first snapshot at or after `T` gives the child's;
3. the parent–child distance `d` is taken from those two centroids (periodic wrap);
4. candidate surrogates: every uid present at the child's snapshot except parent and child, whose centroid is within
   `|dist - d| <= tol` of the child's;
5. one surrogate is drawn at random per event (average over 20 draws), and the same statistic is computed with the
   surrogate's peak area in place of the parent's.

If the observed correlation is no larger than the surrogate's, the parent-specific signal in X70 is spatial.

Run:
    python scripts/x70_spatial_null.py --write
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import random
import statistics as st
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x70_spatial.json"

GRID = 96
TOL = 4.0          # cells; tolerance on the distance match
DRAWS = 20


def wrap_d(a, b, n=GRID):
    dx = abs(a[0] - b[0])
    dy = abs(a[1] - b[1])
    dx = min(dx, n - dx)
    dy = min(dy, n - dy)
    return math.hypot(dx, dy)


def events_for_run(path: Path) -> list[dict]:
    d = json.loads(path.read_text(encoding="utf-8"))
    peaks = {int(u["uid"]): int(u["peak"]) for u in (d.get("uid_outcomes") or []) if u.get("peak")}
    first = {int(u["uid"]): int(u["first"]) for u in (d.get("uid_outcomes") or []) if u.get("first") is not None}
    snapshots = []
    for s in d.get("series") or []:
        entry = {}
        for c in s.get("components_log") or []:
            if c.get("uid") is not None and c.get("cx") is not None:
                entry[int(c["uid"])] = (float(c["cx"]), float(c["cy"]))
        snapshots.append((int(s.get("step") or 0), entry))
    snapshots.sort()

    out = []
    for p_uid, c_uid in (d.get("uid_pairs") or []):
        p_uid, c_uid = int(p_uid), int(c_uid)
        if p_uid not in peaks or c_uid not in peaks or c_uid not in first:
            continue
        t_birth = first[c_uid]
        prev = [(t, m) for t, m in snapshots if t < t_birth and p_uid in m]
        nxt = [(t, m) for t, m in snapshots if t >= t_birth and c_uid in m]
        if not prev or not nxt:
            continue
        p_pos = prev[-1][1][p_uid]
        t_child, m_child = nxt[0]
        c_pos = m_child[c_uid]
        d_pc = wrap_d(p_pos, c_pos)

        surrogates = []
        for uid, pos in m_child.items():
            if uid in (p_uid, c_uid) or uid not in peaks:
                continue
            if abs(wrap_d(pos, c_pos) - d_pc) <= TOL:
                surrogates.append(uid)
        if not surrogates:
            continue
        out.append({"parent_peak": peaks[p_uid], "child_peak": peaks[c_uid],
                    "surrogate_peaks": [peaks[u] for u in surrogates], "distance": round(d_pc, 2)})

    return out


def corr(pairs: list[tuple[float, float]]) -> float | None:
    if len(pairs) < 5:
        return None
    xs = [a for a, _ in pairs]
    ys = [b for _, b in pairs]
    mx, my = st.mean(xs), st.mean(ys)
    sx, sy = st.pstdev(xs), st.pstdev(ys)
    if not sx or not sy:
        return None
    return sum((x - mx) * (y - my) for x, y in pairs) / len(pairs) / (sx * sy)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X70 spatial null")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    rng = random.Random(11)
    result = {"kind": "l1_field_x70_spatial", "experiment": "X70 control",
              "command": "python scripts/x70_spatial_null.py --write",
              "prereg": "reports/2026-11-01-x70-size-heredity-plan.md (control added after the answers)",
              "tolerance_cells": TOL, "draws": DRAWS, "arms": {}}

    for arm in ("pattern", "homog"):
        evs = []
        for f in sorted(glob.glob(str(L1 / f"x70_{arm}_s*.json"))):
            evs += events_for_run(Path(f))
        if not evs:
            continue
        observed = corr([(e["parent_peak"], e["child_peak"]) for e in evs])
        draws = []
        for _ in range(DRAWS):
            pairs = []
            for e in evs:
                pairs.append((rng.choice(e["surrogate_peaks"]), e["child_peak"]))
            c = corr(pairs)
            if c is not None:
                draws.append(c)
        draws.sort()
        result["arms"][arm] = {
            "events": len(evs),
            "observed_corr": round(observed, 3) if observed is not None else None,
            "surrogate_corr_median": round(st.median(draws), 3) if draws else None,
            "surrogate_corr_p95": round(draws[int(0.95 * len(draws)) - 1], 3) if draws else None,
            "exceeds_surrogate": (observed is not None and draws and observed > draws[int(0.95 * len(draws)) - 1]),
            "median_distance": round(st.median([e["distance"] for e in evs]), 2),
        }

    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[x70-spatial] written: {OUT.name}")
    for arm, a in result["arms"].items():
        print("  %-8s events=%4d  observed=%.3f  surrogate median=%.3f p95=%.3f  exceeds: %s" % (
            arm, a["events"], a["observed_corr"], a["surrogate_corr_median"], a["surrogate_corr_p95"],
            a["exceeds_surrogate"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
