"""
X196 answered the either-or: the gap switches fusion, the size shifts it. It did so with three arms and a five-row table whose two
middle points came from different radii, so the shape of the switch is still interpolated. This runs the switch itself at a fixed
size - radius 4 at gaps 8, 9, 10, 11 and 12 - and repeats the three largest gaps at radius 6, so the size shift is a comparison
between two curves at matched gaps rather than between two points.

Pre-registration: reports/2026-11-05-x198-gap-curve-plan.md.
Run: python scripts/x198_gap_curve.py --write
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
TRACK = ROOT / "scripts" / "field_track.py"
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
FIELDS = ROOT / "_hourly" / "x198_fields"
FLOW = "0.030"
STEPS = 400
GRID = 96
SCALE = 12.0
ARMS = [("r4_g8", 4.0, 8.0), ("r4_g9", 4.0, 9.0), ("r4_g10", 4.0, 10.0), ("r4_g11", 4.0, 11.0),
        ("r4_g12", 4.0, 12.0), ("r6_g8", 6.0, 8.0), ("r6_g9", 6.0, 9.0), ("r6_g10", 6.0, 10.0)]
SAVE_AT = "40,60,80,100,140,200,300"
SCAN = 400000

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


def site_flow(key, sep: float) -> float:
    g, k, f = GRID, 2.0 * math.pi / SCALE, float(FLOW)
    jx, jy = key
    cx, cy = g / 2.0 + jx, g / 2.0 + jy

    def gat(x, y):
        return (math.sin(k * (int(round(y)) % g)) * math.cos(k * (int(round(x)) % g)) + 1.0) / 2.0

    return f * (1 + 0.5 * (2 * min(gat(cx - sep / 2.0, cy), gat(cx + sep / 2.0, cy)) - 1))


def census(sep: float):
    """One representative seed per phase class (first seed whose jitter lands on that phase)."""
    classes = {}
    for seed in range(SCAN):
        key = jitter(seed)
        ph = (key[0] % 12, key[1] % 12)
        if ph in classes:
            continue
        classes[ph] = {"phase": list(ph), "jitter": list(key), "seed": seed, "f_local": round(site_flow(key, sep), 5)}
    return dict(sorted(classes.items()))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    index = {"kind": "x198_gap_curve", "flow": float(FLOW), "steps": STEPS, "save_at": SAVE_AT,
             "arms": [{"name": n, "radius": r, "gap": g, "sep": r * 2 + g} for n, r, g in ARMS],
             "prediction": "the phase decides the bridge at fixed inflow in each arm; the fusion share at fixed radius 4 does not fall as the gap "
                           "closes (12 -> 10 -> 8), so the window closes by bringing the bodies together; and radius 6 at gap 8 fuses at least as "
                           "often as radius 6 at gap 9, so with the separation held at 20 the larger body still fuses and the size is not the barrier",
             "runs": []}
    for name, radius, gap in ARMS:
        sep = 2 * radius + gap
        (FIELDS / name).mkdir(parents=True, exist_ok=True)
        classes = census(sep)
        index.setdefault("classes_per_arm", {})[name] = list(classes.values())
        for ci, c in enumerate(classes.values()):
            tag = f"{name}_c{ci:03d}"
            out = L1 / f"x198_{tag}.json"
            fdir = FIELDS / name / f"c{ci:03d}"
            if out.exists() and out.stat().st_size > 0:
                index["runs"].append({**c, "arm": name, "radius": radius, "gap": gap, "sep": sep,
                                      "class_index": ci, "tag": tag, "status": "skipped (exists)"})
                continue
            cmd = [PY, str(TRACK), *COMMON, "--device", args.device, "--F", FLOW, "--seed", str(c["seed"]),
                   "--out", str(out), "--init-spots", f"{radius:g}:{sep:g}",
                   "--save-fields", str(fdir), "--save-fields-at", SAVE_AT]
            t0 = time.time()
            p = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8",
                               errors="replace", timeout=12000)
            status = "ok" if p.returncode == 0 else "failed"
            index["runs"].append({**c, "arm": name, "radius": radius, "gap": gap, "sep": sep,
                                  "class_index": ci, "tag": tag, "status": status,
                                  "seconds": round(time.time() - t0, 1),
                                  **({"tail": (p.stderr or p.stdout or "")[-300:]} if status == "failed" else {})})
            if ci % 24 == 0 or status != "ok":
                print(f"[x198] {name} c{ci:03d} {c['phase']} F_local {c['f_local']}: {status} ({round(time.time() - t0, 1)} s)")
    if args.write:
        (L1 / "x198_series_index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1) + "\n",
                                                   encoding="utf-8")
        counts = {a["name"]: sum(1 for r in index["runs"] if r["arm"] == a["name"] and r["status"] in ("ok", "skipped (exists)"))
                  for a in index["arms"]}
        print(f"[x198] index written: {counts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
