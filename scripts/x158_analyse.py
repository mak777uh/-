"""x158_analyse.py — X158: turn the X157 band into a measured crossing.

Reads every two-body run of the block that carries `params.init_spots = "radius:separation"`, derives for each run
whether the pair ended as one body (the same rule as X157: the last logged step with two components, then a step with
one), and groups by (radius, design gap = separation - 2 x radius). Each arm gets a Wilson interval on the share; the
crossing per radius is the largest gap at which the share is still at least one half.

    python scripts/x158_analyse.py --write
    python scripts/x158_analyse.py --write --json-out morphogenesis/experiments/E09_pond/l1_field_x158_crossing.json

Outputs the aggregate with `arms`, `by_radius`, `controls`, `sensitivity`, `verdict`.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from x157_gap_geometry import collect  # noqa: E402  (same geometry, same skip rules)

OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x158_crossing.json"

PATTERNS = ["x136_*_s*.json", "x140_*_s*.json", "x142_*_s*.json", "x147_*_s*.json",
            "x150_*_s*.json", "x151_*_s*.json", "x153_*_s*.json", "x154_*_s*.json", "x158_*_s*.json"]


MIN_RUNS = 5


def wilson(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if n == 0:
        return (None, None)
    p = k / n
    denom = 1.0 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (round(max(0.0, centre - half), 3), round(min(1.0, centre + half), 3))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X158: the fusion crossing at three radii")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--json-out", default="")
    ap.add_argument("--min-runs", type=int, default=5,
                    help="an arm needs this many runs before it may decide the crossing (half-finished arms are listed)")
    args = ap.parse_args(argv)
    global MIN_RUNS
    MIN_RUNS = args.min_runs

    rows = collect(PATTERNS)
    if not rows:
        print("[x158] no artifacts matched")
        return 1

    arms: dict[str, dict] = {}
    dropped = []
    for geo in rows:
        radius = round(float(geo["radius"]), 2)
        gap = round(float(geo["sep"]) - 2.0 * radius, 2)
        if gap < 1.0:
            # a single centred disc (sep = 0) or an overlapping pair: a scale control, not a gap-ladder arm
            dropped.append(geo.get("file"))
            continue
        key = f"r{radius:.1f}_g{gap:.1f}"
        arm = arms.setdefault(key, {"radius": radius, "design_gap": gap, "runs": 0, "fused": 0,
                                    "seeds": [], "g_fusion": []})
        arm["runs"] += 1
        arm["seeds"].append(geo.get("seed"))
        if geo["ended_as_one"]:
            arm["fused"] += 1
            if geo["g_fusion"] is not None:
                arm["g_fusion"].append(geo["g_fusion"])

    for arm in arms.values():
        arm["seeds"].sort()
        arm["share"] = round(arm["fused"] / arm["runs"], 3) if arm["runs"] else None
        arm["ci"] = list(wilson(arm["fused"], arm["runs"]))
        arm["g_fusion_median"] = (round(float(sorted(arm["g_fusion"])[len(arm["g_fusion"]) // 2]), 2)
                                 if arm["g_fusion"] else None)
        arm["n_new"] = sum(1 for s in arm["seeds"] if s is not None and 701 <= int(s) <= 710)

    radii = sorted({arm["radius"] for arm in arms.values()})
    by_radius: dict[str, dict] = {}
    for radius in radii:
        curve = sorted((arm for arm in arms.values() if arm["radius"] == radius),
                       key=lambda a: a["design_gap"])
        usable = [a for a in curve if a["runs"] >= MIN_RUNS]
        shares = [(a["design_gap"], a["share"], a["runs"]) for a in usable]
        # the crossing is the first gap at which the share falls below one half; the fill is the last gap above it
        crossing = None
        filled = None
        for gap, share, _ in shares:
            if share is None:
                continue
            if share >= 0.5:
                filled = gap
            elif crossing is None:
                crossing = gap
        crossing_range = [filled, crossing] if (filled is not None and crossing is not None) else None
        falling = [s for _, s, _ in shares if s is not None]
        by_radius[f"r{radius:.1f}"] = {
            "curve": shares,
            "crossing_gap": crossing,
            "crossing_range": crossing_range,
            "share_min": min(falling) if falling else None,
            "share_max": max(falling) if falling else None,
            "varies": bool(falling) and (max(falling) - min(falling)) >= 0.4,
            "runs": sum(a["runs"] for a in curve),
            "all_arms": [(a["design_gap"], a["share"], a["runs"]) for a in curve],
        }

    # controls: the gap-8 arms, re-measured on seeds that were never used there
    controls = {}
    for radius in (3.0, 4.5, 6.0):
        arm = arms.get(f"r{radius:.1f}_g8.0")
        if arm:
            new_only = [geo for geo in rows
                        if round(float(geo["radius"]), 2) == radius
                        and round(float(geo["sep"]) - 2.0 * radius, 2) == 8.0
                        and geo.get("seed") is not None and 701 <= int(geo["seed"]) <= 710]
            controls[f"r{radius:.1f}"] = {"share_all": arm["share"], "runs_all": arm["runs"],
                                          "new_seed_runs": len(new_only),
                                          "new_seed_fused": sum(1 for g in new_only if g["ended_as_one"]),
                                          "fires": arm["share"] is not None and arm["share"] >= 0.8}

    crossings = {k: {"crossing_gap": v["crossing_gap"], "crossing_range": v["crossing_range"]}
                  for k, v in by_radius.items() if v["crossing_gap"] is not None}
    fall_cells = [c["crossing_gap"] for c in crossings.values()]
    spread = (max(fall_cells) - min(fall_cells)) if len(fall_cells) > 1 else None
    control_ok = all(c["fires"] for c in controls.values()) if controls else False
    varies = any(v["varies"] for v in by_radius.values())

    if not control_ok:
        verdict = ("STOPPED: the gap-8 positive control did not fire, so nothing is written about the crossing "
                   "(pre-registered refusal).")
    elif not varies:
        verdict = ("INSENSITIVE BY CONSTRUCTION: the fusion share does not vary across the tested gaps, so no "
                   "crossing is claimed.")
    elif spread is not None and spread >= 2:
        verdict = (f"THE CROSSING MOVES WITH SIZE: it falls at {crossings} cells for the tested radii, a spread of "
                   f"{spread:g} cells, so the 'flat in body size' sentence of X157 is not supported and the crossing "
                   "is reported per radius.")
    else:
        cells = sorted(crossings[k]["crossing_range"][1] if crossings[k]["crossing_range"] else crossings[k]["crossing_gap"]
                        for k in crossings)
        lo, hi = cells[0], cells[-1]
        if lo == hi:
            verdict = (f"THE CROSSING IS AT {lo:g} CELLS FOR EVERY TESTED SIZE: in design-gap terms the boundary is "
                       "flat in the seeded size, and the X157 band (8-11) shrinks to this one cell.")
        else:
            verdict = (f"THE CROSSING IS AT {lo:g}-{hi:g} CELLS, flat in the seeded size within one cell: the X157 band "
                       "shrinks to this range and is not resolved further at ten seeds per arm.")

    payload = {
        "kind": "l1_field_x158_crossing",
        "command": "python scripts/x158_analyse.py --write",
        "prereg": "reports/2026-11-04-x158-crossing-plan.md",
        "note": ("design gap = separation - 2 x seeded radius (the X157 convention); the readout is the share of runs "
                 "that ended as one body; intervals are Wilson at 95 %; the crossing is the largest gap at which the "
                 "share is still at least one half."),
        "arms": {k: arms[k] for k in sorted(arms)},
        "by_radius": by_radius,
        "controls": controls,
        "dropped_single_body_runs": sorted({name for name in dropped if name}),
        "sensitivity": {"control_fired": control_ok, "readout_varies": varies, "crossing_spread_cells": spread,
                        "seeds_per_new_arm": 10},
        "verdict": verdict,
    }
    target = Path(args.json_out) if args.json_out else OUT
    if args.write:
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
        print(f"[x158] written: {target.relative_to(ROOT)}")
    for radius, info in by_radius.items():
        print(f"[x158] {radius}: " + ", ".join(f"g{g:g} {s:.2f} (n={n})" for g, s, n in info["curve"]))
    print(f"[x158] controls: {controls}")
    print(f"[x158] {verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
