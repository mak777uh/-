"""
X201 — edge-distance intervention (pre-registration: reports/2026-11-05-x201-edge-intervention-plan.md).

At fixed geometry, fixed phase (mod 12) and identical parameters, place the same pair at several distances from the domain
edge and read whether fusion moves with distance. Reuses field_track.py / X198 COMMON; no world/physics changes.

Run:  python scripts/x201_edge_intervention.py --device cpu --write
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
TRACK = ROOT / "scripts" / "field_track.py"
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
POND = ROOT / "morphogenesis" / "experiments" / "E09_pond"
FLOW = "0.030"
STEPS = 400
GRID = 96
SCAN = 300000

GEOMS = [("r4_g10", 4.0, 10.0), ("r4_g9", 4.0, 9.0)]
# phases prioritised from X200's disagreeing worlds (g10 then g9)
PHASES = {
    "r4_g10": [((3, 1), (9, 1)), ((3, 2), (9, 2)), ((3, 4), (9, 4)), ((3, 7), (9, 7)),
               ((2, 1), (8, 1)), ((2, 3), (8, 3))],
    "r4_g9": [((4, 2), (10, 2)), ((4, 3), (10, 3)), ((4, 8), (10, 8)), ((4, 9), (10, 9)),
              ((2, 2), (8, 2)), ((2, 8), (8, 8))],
}
BINS = [("near", 0, 14), ("mid", 15, 22), ("far", 23, 999)]
SEEDS_PER = 4

COMMON = [
    "--steps", str(STEPS), "--grid", "96", "--dt", "1.0",
    "--Du", "0.16", "--Dv", "0.08", "--k", "0.06", "--eps", "0.0",
    "--hetero-scale", "12.0", "--hetero-period", "0.0", "--hetero-amp", "0.5",
    "--hetero-signal", "lab/streams/const_ones.json",
    "--sample-every", "10", "--threshold", "0.2",
    "--freq-dep", "0.0", "--bin-width", "0.2", "--beta", "0.0", "--s-ref", "1.0", "--mutation", "0.15",
    "--overlap", "0.5", "--split-new-uid", "--init-jitter",
]


def jitter(seed: int):
    jr = np.random.default_rng(int(seed) + 9187)
    return tuple(int(v) for v in jr.integers(-GRID // 4, GRID // 4 + 1, size=2))


def phase_and_edge(radius: float, sep: float, seed: int):
    jx, jy = jitter(seed)
    cx, cy = GRID / 2.0 + jx, GRID / 2.0 + jy
    x0, x1 = cx - sep / 2.0, cx + sep / 2.0
    b0 = (int(round(x0)), int(round(cy)))
    b1 = (int(round(x1)), int(round(cy)))
    ph = tuple(sorted(((b0[0] % 12, b0[1] % 12), (b1[0] % 12, b1[1] % 12))))
    edge = min(b0[0], b0[1], GRID - 1 - b0[0], GRID - 1 - b0[1],
               b1[0], b1[1], GRID - 1 - b1[0], GRID - 1 - b1[1])
    return ph, edge, (jx, jy), b0, b1


def which_bin(edge: int):
    for name, lo, hi in BINS:
        if lo <= edge <= hi:
            return name
    return None


def census_phase_bins(radius: float, sep: float, target_phases: list):
    found = {tuple(tuple(p) for p in ph): {b[0]: [] for b in BINS} for ph in target_phases}
    targets = set(found)
    for seed in range(SCAN):
        ph, edge, key, b0, b1 = phase_and_edge(radius, sep, seed)
        if ph not in targets:
            continue
        bname = which_bin(edge)
        if bname and len(found[ph][bname]) < SEEDS_PER:
            found[ph][bname].append({"seed": seed, "edge": edge, "jitter": list(key),
                                     "b0": list(b0), "b1": list(b1)})
        if all(len(found[ph][bn]) >= SEEDS_PER for ph in targets for bn, _, _ in BINS):
            break
    return found


def fused_from(out_path: Path):
    d = json.loads(out_path.read_text(encoding="utf-8"))
    series = d.get("series") or []
    if not series:
        return None
    counts = [len(r[1]) if isinstance(r, list) and len(r) > 1 and isinstance(r[1], list) else 0 for r in series]
    return int(min(counts) == 1)


def run_one(name: str, radius: float, gap: float, ph, bname: str, rep: int, seed: int, device: str):
    sep = 2 * radius + gap
    tag = f"x201_{name}_p{ph[0][0]}{ph[0][1]}_{ph[1][0]}{ph[1][1]}_{bname}_r{rep}_s{seed}"
    out = L1 / f"{tag}.json"
    if out.exists() and out.stat().st_size > 0:
        fus = fused_from(out)
        return {"tag": tag, "arm": name, "radius": radius, "gap": gap, "sep": sep, "phase": ph,
                "bin": bname, "rep": rep, "seed": seed, "status": "skipped (exists)", "fused": fus}
    cmd = [PY, str(TRACK), *COMMON, "--device", device, "--F", FLOW, "--seed", str(seed),
           "--out", str(out), "--init-spots", f"{radius:g}:{sep:g}"]
    t0 = time.time()
    p = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=3600)
    fus = fused_from(out) if p.returncode == 0 and out.exists() else None
    status = "ok" if p.returncode == 0 else "failed"
    rec = {"tag": tag, "arm": name, "radius": radius, "gap": gap, "sep": sep, "phase": ph,
           "bin": bname, "rep": rep, "seed": seed, "status": status, "fused": fus,
           "seconds": round(time.time() - t0, 1)}
    if status == "failed":
        rec["tail"] = (p.stderr or p.stdout or "")[-300:]
    return rec


def analyse(runs):
    ok = [r for r in runs if r.get("status") in ("ok", "skipped (exists)") and r.get("fused") is not None]
    by = defaultdict(lambda: defaultdict(list))
    for r in ok:
        by[(r["arm"], tuple(tuple(x) for x in r["phase"]))][r["bin"]].append(r["fused"])
    by_arm = defaultdict(lambda: defaultdict(list))
    for r in ok:
        by_arm[r["arm"]][r["bin"]].extend([r["fused"]])
    arm_stats = {}
    for arm, bins in by_arm.items():
        shares = {b: (statistics.fmean(v) if v else None) for b, v in bins.items()}
        n = {b: len(v) for b, v in bins.items()}
        near = shares.get("near"); far = shares.get("far")
        diff = (round(far - near, 4) if near is not None and far is not None else None)
        # phase consistency: phases with data in both near & far
        phase_dirs = []
        for (a, ph), bmap in by.items():
            if a != arm or "near" not in bmap or "far" not in bmap:
                continue
            dn = statistics.fmean(bmap["near"]) - statistics.fmean(bmap["far"])
            if dn != 0:
                phase_dirs.append(1 if dn > 0 else -1)
        same_dir = 0
        if phase_dirs:
            from collections import Counter
            c = Counter(phase_dirs); same_dir = c.most_common(1)[0][1]
        arm_stats[arm] = {"n": n, "shares": {k: (round(v, 4) if v is not None else None) for k, v in shares.items()},
                          "far_minus_near": diff, "c1": bool(diff is not None and abs(diff) >= 0.25),
                          "phases_both_bins_nonzero_same_dir": same_dir, "c2": same_dir >= 2}
    return {"runs_ok": len(ok), "by_arm": arm_stats}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--max-runs", type=int, default=0, help="cap total runs (0 = all)")
    args = ap.parse_args(argv)

    plan_runs = []
    for name, radius, gap in GEOMS:
        sep = 2 * radius + gap
        targets = [tuple(tuple(p) for p in ph) for ph in PHASES[name][:4]]
        found = census_phase_bins(radius, sep, targets)
        feasible = [ph for ph in targets if sum(1 for b in found[ph] if found[ph][b]) >= 2]
        use = feasible[:4]
        print(f"[x201] {name} feasible phases {len(feasible)}/{len(targets)} -> using {len(use)}")
        for ph in use:
            for bname, _, _ in BINS:
                for rep, cand in enumerate(found[ph][bname][:SEEDS_PER]):
                    plan_runs.append((name, radius, gap, ph, bname, rep, cand["seed"], cand))
    if args.max_runs:
        plan_runs = plan_runs[:args.max_runs]
    print(f"[x201] planned runs: {len(plan_runs)}")

    results = []
    for i, (name, radius, gap, ph, bname, rep, seed, cand) in enumerate(plan_runs):
        rec = run_one(name, radius, gap, ph, bname, rep, seed, args.device)
        rec["edge"] = cand["edge"]
        rec["jitter"] = cand["jitter"]
        results.append(rec)
        if rec["status"] != "skipped (exists)" or i % 20 == 0:
            print(f"[x201] {i+1}/{len(plan_runs)} {rec['tag']} fused={rec['fused']} edge={rec['edge']} {rec['status']}")

    analysis = analyse(results)
    print(json.dumps(analysis, ensure_ascii=False, indent=1))
    if args.write:
        agg = {"kind": "x201_edge_intervention", "flow": float(FLOW), "steps": STEPS, "grid": GRID,
               "bins": [{"name": n, "lo": lo, "hi": hi} for n, lo, hi in BINS],
               "geoms": [{"name": n, "radius": r, "gap": g, "sep": 2 * r + g} for n, r, g in GEOMS],
               "planned": len(plan_runs), "runs": results, "analysis": analysis}
        out = POND / "l1_field_x201_edge_intervention.json"
        out.write_text(json.dumps(agg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
        print(f"[x201] wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
