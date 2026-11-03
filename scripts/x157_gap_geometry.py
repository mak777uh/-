"""x157_gap_geometry.py — where does fusion actually happen, in the geometry the bodies have at that moment?

The mixing-length claim of the field line was stated in "surface gap" computed from the *nominal* radius of the discs at
t = 0 (`g = separation − 2r`). An independent review showed two problems: the discs grow during the run, and the arms are
five seeds wide, so the quoted "stop" gaps are not monotone. This script re-derives the geometry from the logs, which
carry every component's area and centre at every tenth step:

    for each run, find the step at which the two bodies become one (the last step with two components),
    take their areas and centres at the previous logged step, convert area to an effective radius r = sqrt(A/pi),
    and report the surface gap at that moment: g = d − r1 − r2, with d the periodic centre distance.

Outputs `morphogenesis/experiments/E09_pond/l1_field_x157_gap_geometry.json`:

    arms:      per arm, the share of runs that ended as one body and the observed gaps at fusion
    by_radius: the distribution of g at fusion, per nominal radius
    growth:    r_effective at the first logged step against r at fusion (how much a body grows before meeting)
    verdict:   the sentence the correction can stand on

Run:
    python scripts/x157_gap_geometry.py --write
"""
from __future__ import annotations

import argparse
import glob
import json
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x157_gap_geometry.json"

GRID = 96


def periodic_distance(ax: float, ay: float, bx: float, by: float, grid: int = GRID) -> float:
    dx = abs(ax - bx)
    dy = abs(ay - by)
    dx = min(dx, grid - dx)
    dy = min(dy, grid - dy)
    return math.hypot(dx, dy)


def rows_of(run: dict) -> list[dict]:
    return [row for row in (run.get("series") or []) if isinstance(row, dict)]


def fusion_geometry(run: dict) -> dict:
    """Geometry of the last logged step at which the two seeded bodies are still separate."""
    series = rows_of(run)
    params = run.get("params") or {}
    spots = str(params.get("init_spots") or "")
    radius = sep = None
    if ":" in spots:
        try:
            radius, sep = (float(part) for part in spots.split(":", 1))
        except ValueError:
            radius = sep = None
    if not radius:
        return {"radius": None, "sep": None}
    out = {"radius": radius, "sep": sep, "seed": params.get("seed"), "ended_as_one": None,
           "g_fusion": None, "d_fusion": None, "r_prev": None, "r_first": None, "n_steps_logged": len(series)}
    if not series:
        return out
    # the seeded pair: the two largest components while they are separate
    prev = None
    first_r = None
    for row in series:
        comps = [c for c in (row.get("components_log") or []) if c.get("area")]
        comps.sort(key=lambda c: -int(c["area"]))
        if len(comps) >= 2:
            if first_r is None:
                first_r = math.sqrt(int(comps[0]["area"]) / math.pi)
            prev = (row, comps[:2])
            continue
        if prev is not None and len(comps) == 1:
            step_row, (c1, c2) = prev
            r1 = math.sqrt(int(c1["area"]) / math.pi)
            r2 = math.sqrt(int(c2["area"]) / math.pi)
            d = periodic_distance(float(c1["cx"]), float(c1["cy"]), float(c2["cx"]), float(c2["cy"]))
            out.update({"ended_as_one": True, "g_fusion": round(d - r1 - r2, 2), "d_fusion": round(d, 2),
                        "r_prev": round((r1 + r2) / 2.0, 2), "r_first": round(first_r, 2) if first_r else None,
                        "fusion_step": int(step_row.get("step", 0))})
            return out
    # never became one body: report the last separation of the two largest bodies
    if prev is not None:
        step_row, (c1, c2) = prev
        r1 = math.sqrt(int(c1["area"]) / math.pi)
        r2 = math.sqrt(int(c2["area"]) / math.pi)
        d = periodic_distance(float(c1["cx"]), float(c1["cy"]), float(c2["cx"]), float(c2["cy"]))
        out.update({"ended_as_one": False, "g_fusion": round(d - r1 - r2, 2), "d_fusion": round(d, 2),
                    "r_prev": round((r1 + r2) / 2.0, 2), "r_first": round(first_r, 2) if first_r else None})
    return out


def collect(patterns: list[str]) -> list[dict]:
    rows = []
    for pattern in patterns:
        for path in sorted(glob.glob(str(L1 / pattern))):
            if any(tag in Path(path).name for tag in ("series_index", "compact", "summary", "aggregate")):
                continue
            run = json.loads(Path(path).read_text(encoding="utf-8"))
            geo = fusion_geometry(run)
            if geo.get("radius") is None:
                # older artifacts name the initial condition differently; skip rather than guess
                continue
            geo["file"] = Path(path).name
            rows.append(geo)
    return rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X157 fusion geometry")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    rows = collect(["x136_*_s*.json", "x142_*_s*.json", "x140_*_s*.json", "x138_*_s*.json",
                    "x147_*_s*.json", "x150_*_s*.json", "x151_*_s*.json", "x153_*_s*.json", "x154_*_s*.json"])
    if not rows:
        print("[x157] no artifacts matched")
        return 1
    by_arm: dict[str, dict] = {}
    for geo in rows:
        key = f"r{geo['radius']:.1f}_sep{geo['sep']:.1f}"
        arm = by_arm.setdefault(key, {"radius": geo["radius"], "sep": geo["sep"], "runs": 0, "fused": 0,
                                      "g_fusion": [], "r_first": [], "r_prev": []})
        arm["runs"] += 1
        if geo["ended_as_one"]:
            arm["fused"] += 1
            if geo["g_fusion"] is not None:
                arm["g_fusion"].append(geo["g_fusion"])
            if geo["r_prev"] is not None:
                arm["r_prev"].append(geo["r_prev"])
        if geo["r_first"] is not None:
            arm["r_first"].append(geo["r_first"])
    for arm in by_arm.values():
        for key in ("g_fusion", "r_first", "r_prev"):
            vals = arm.pop(key)
            arm[f"{key}_median"] = round(float(np.median(vals)), 2) if vals else None
            arm[f"{key}_min"] = round(float(np.min(vals)), 2) if vals else None
            arm[f"{key}_max"] = round(float(np.max(vals)), 2) if vals else None
            arm[f"{key}_n"] = len(vals)
        arm["fused_share"] = round(arm["fused"] / arm["runs"], 3) if arm["runs"] else None
        arm["nominal_gap"] = round(arm["sep"] - 2 * arm["radius"], 2)

    by_radius: dict[str, dict] = {}
    for radius in sorted({round(geo["radius"], 1) for geo in rows}):
        fused = [geo for geo in rows if round(geo["radius"], 1) == radius and geo["ended_as_one"]]
        gaps = [geo["g_fusion"] for geo in fused if geo["g_fusion"] is not None]
        prev_r = [geo["r_prev"] for geo in fused if geo["r_prev"] is not None]
        first_r = [geo["r_first"] for geo in rows if round(geo["radius"], 1) == radius and geo["r_first"]]
        by_radius[f"r{radius:.1f}"] = {
            "runs": len([g for g in rows if round(g["radius"], 1) == radius]),
            "fused": len(fused),
            "g_fusion_median": round(float(np.median(gaps)), 2) if gaps else None,
            "g_fusion_min": round(float(np.min(gaps)), 2) if gaps else None,
            "g_fusion_max": round(float(np.max(gaps)), 2) if gaps else None,
            "r_at_fusion_median": round(float(np.median(prev_r)), 2) if prev_r else None,
            "r_at_first_step_median": round(float(np.median(first_r)), 2) if first_r else None,
        }

    all_gaps = [geo["g_fusion"] for geo in rows if geo["ended_as_one"] and geo["g_fusion"] is not None]
    verdict = (
        f"Fusion happens when the two bodies' SURFACES are "
        f"{float(np.median(all_gaps)):.1f} cells apart (median over {len(all_gaps)} fusing runs, "
        f"range {float(np.min(all_gaps)):.1f} to {float(np.max(all_gaps)):.1f}), and the bodies are "
        f"{float(np.median([g['r_prev'] for g in rows if g['ended_as_one'] and g['r_prev']])):.1f} cells in radius "
        f"at that moment, not the {sorted({round(g['radius'], 1) for g in rows})} they started with. The nominal "
        f"surface gap of the design (separation minus twice the initial radius) is therefore not the gap at which the "
        f"medium fuses two bodies; the claim must be restated in the geometry measured at contact."
        if all_gaps else "no fusing runs found"
    )

    per_run = [{"radius": g["radius"], "sep": g["sep"], "seed": g["seed"], "fused": g["ended_as_one"],
                "g_fusion": g["g_fusion"], "r_first": g["r_first"], "r_prev": g["r_prev"]} for g in rows]
    out = {"kind": "l1_field_x157_gap_geometry", "experiment": "X157",
           "contact_gap_median": round(float(np.median(all_gaps)), 2) if all_gaps else None,
           "contact_gap_min": round(float(np.min(all_gaps)), 2) if all_gaps else None,
           "contact_gap_max": round(float(np.max(all_gaps)), 2) if all_gaps else None,
           "contact_gap_n": len(all_gaps),
           "runs_geometry": per_run,
           "question": "at what surface gap does the medium actually fuse two bodies?",
           "method": "for each run: the last logged step with two components gives their areas and centres; "
                     "r = sqrt(A/pi); g = periodic centre distance - r1 - r2",
           "arms": by_arm, "by_radius": by_radius, "n_runs": len(rows),
           "n_fused": len(all_gaps), "verdict": verdict}
    print(f"[x157] runs {len(rows)}, fusing {len(all_gaps)}")
    for key, arm in sorted(by_arm.items()):
        print(f"[x157] {key}: fused {arm['fused']}/{arm['runs']}, nominal gap {arm['nominal_gap']}, "
              f"g at fusion median {arm['g_fusion_median']} [{arm['g_fusion_min']}, {arm['g_fusion_max']}]")
    print(f"[x157] {verdict}")
    if args.write:
        OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
        print(f"[x157] written {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
