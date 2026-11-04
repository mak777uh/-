"""x157_quantum.py — is the 1.9-cell contact gap a threshold, or a logging artefact?

X157 reads the surface gap at the last logged step at which the two bodies are still separate, with one logged step every
ten integration steps. The bodies grow between those steps, so 1.9 cells is an **upper bound** on the gap at which fusion
actually becomes possible: the true threshold lies somewhere between that reading and that reading minus however much the
two radii grew in the ten steps that were not logged.

This script estimates that window per run, from the growth the log does show: for each of the two bodies, the change of
effective radius between the two logged steps before the last one, so a growth rate per integration step, and then the
displacement over one logging quantum (10 steps, `params.sample_every`). The window is

    g_threshold in [ g_last - (dr1/dt + dr2/dt) * sample_every , g_last ]

and the aggregate reports its width, so the article can say whether 1.9 is a number or an interval.

    python scripts/x157_quantum.py --write
    python scripts/x157_quantum.py --window-per-run
"""
from __future__ import annotations

import argparse
import glob
import json
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys_path = ROOT / "scripts"
import sys  # noqa: E402

sys.path.insert(0, str(sys_path))
from x157_gap_geometry import periodic_distance  # noqa: E402

L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x157_quantum.json"

PATTERNS = ["x136_*_s*.json", "x140_*_s*.json", "x142_*_s*.json", "x147_*_s*.json", "x150_*_s*.json",
            "x151_*_s*.json", "x153_*_s*.json", "x154_*_s*.json", "x158_*_s*.json"]


def two_bodies(comps: list[dict]) -> list[dict]:
    have = [c for c in comps if c.get("area")]
    have.sort(key=lambda c: -int(c["area"]))
    return have[:2]


def geometry(row: dict) -> tuple[float, float, float]:
    """(centre distance, r1 + r2, mean radius) of the two largest bodies in a logged row."""
    comps = two_bodies(row.get("components_log") or [])
    if len(comps) < 2:
        return None
    r1 = math.sqrt(int(comps[0]["area"]) / math.pi)
    r2 = math.sqrt(int(comps[1]["area"]) / math.pi)
    d = periodic_distance(float(comps[0]["cx"]), float(comps[0]["cy"]),
                          float(comps[1]["cx"]), float(comps[1]["cy"]))
    return d, r1 + r2, (r1 + r2) / 2.0


def window(path: Path) -> dict | None:
    run = json.loads(path.read_text(encoding="utf-8"))
    params = run.get("params") or {}
    spots = str(params.get("init_spots") or "")
    if ":" not in spots:
        return None
    try:
        radius, sep = (float(part) for part in spots.split(":", 1))
    except ValueError:
        return None
    if sep - 2 * radius < 1.0:
        return None
    sample_every = int(params.get("sample_every") or 10)
    rows = [row for row in (run.get("series") or []) if isinstance(row, dict)]

    # the fusion is the *first* transition from two bodies to one, exactly as x157 reads it
    before: list[int] = []
    fusion_at = None
    for index, row in enumerate(rows):
        comps = [c for c in (row.get("components_log") or []) if c.get("area")]
        if len(comps) >= 2:
            before.append(index)
            continue
        if len(comps) == 1 and before:
            fusion_at = index
            break
        if not before:
            break  # a lone body from the start: not a two-body arm
    if fusion_at is None:
        return None

    # growth over the logged two-body steps immediately before the fusion
    idx = before[-3:]
    if len(idx) < 2:
        return None
    step_a, geo_a = int(rows[idx[0]].get("step") or 0), geometry(rows[idx[0]])
    step_b, geo_b = int(rows[idx[-1]].get("step") or 0), geometry(rows[idx[-1]])
    dstep = max(1, step_b - step_a)
    dr_dt = max(0.0, (geo_b[2] - geo_a[2]) / dstep)
    d, rsum = geo_b[0], geo_b[1]
    g_last = d - rsum
    shrink = 2.0 * dr_dt * sample_every
    return {"file": path.name, "radius": radius, "sep": sep, "design_gap": round(sep - 2 * radius, 2),
            "seed": params.get("seed"), "g_last": round(g_last, 3), "dr_per_step": round(dr_dt, 5),
            "shrink_over_quantum": round(shrink, 3),
            "g_threshold_low": round(g_last - shrink, 3), "g_threshold_high": round(g_last, 3),
            "window_width": round(shrink, 3)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="quantisation window of the contact gap")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--window-per-run", action="store_true")
    args = ap.parse_args(argv)

    rows = []
    for pattern in PATTERNS:
        for path in sorted(glob.glob(str(L1 / pattern))):
            name = Path(path).name
            if any(tag in name for tag in ("series_index", "compact", "summary", "aggregate")):
                continue
            w = window(Path(path))
            if w is not None:
                rows.append(w)
    if not rows:
        print("[x157q] nothing matched")
        return 1

    widths = np.array([r["window_width"] for r in rows], dtype=float)
    lows = np.array([r["g_threshold_low"] for r in rows], dtype=float)
    highs = np.array([r["g_threshold_high"] for r in rows], dtype=float)
    by_radius: dict[str, dict] = {}
    for radius in sorted({r["radius"] for r in rows}):
        sel = [r for r in rows if r["radius"] == radius]
        by_radius[f"r{radius:.1f}"] = {
            "runs": len(sel),
            "g_last_median": round(float(np.median([r["g_last"] for r in sel])), 2),
            "window_width_median": round(float(np.median([r["window_width"] for r in sel])), 3),
            "window_width_max": round(float(np.max([r["window_width"] for r in sel])), 3),
            "g_threshold_low_median": round(float(np.median([r["g_threshold_low"] for r in sel])), 2),
        }
    payload = {
        "kind": "l1_field_x157_quantum",
        "command": "python scripts/x157_quantum.py --write",
        "prereg": "reports/2026-11-04-x157-gap-geometry.md (amendment 1)",
        "note": ("the logged step is one sample every `sample_every` integration steps, so the surface gap read at the "
                 "last two-body step is an upper bound on the threshold; the window grows the two radii at the rate the "
                 "log itself shows over the previous interval."),
        "runs": len(rows),
        "window_width_median": round(float(np.median(widths)), 3),
        "window_width_p90": round(float(np.percentile(widths, 90)), 3),
        "window_width_max": round(float(np.max(widths)), 3),
        "threshold_median": round(float(np.median(highs)), 2),
        "threshold_low_median": round(float(np.median(lows)), 2),
        "share_above_two_cells_at_low_bound": round(float(np.mean(lows >= 2.0)), 3),
        "by_radius": by_radius,
        "verdict": (f"the 1.9-cell reading is an upper bound: the unlogged growth widens it downward by a median of "
                    f"{float(np.median(widths)):.2f} cells (p90 {float(np.percentile(widths, 90)):.2f}), so the "
                    "threshold lies in a window that is narrow against the two-cell scale but is not zero."),
    }
    if args.window_per_run:
        payload["per_run"] = sorted(rows, key=lambda r: -r["window_width"])
    if args.write:
        OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
        print(f"[x157q] written: {OUT.relative_to(ROOT)}")
    print(f"[x157q] runs {len(rows)}; window median {payload['window_width_median']} "
          f"p90 {payload['window_width_p90']} max {payload['window_width_max']}")
    for radius, info in by_radius.items():
        print(f"[x157q] {radius}: g_last {info['g_last_median']}, low {info['g_threshold_low_median']}, "
              f"window {info['window_width_median']} (max {info['window_width_max']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
