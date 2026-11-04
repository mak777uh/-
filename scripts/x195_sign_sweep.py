"""x195_sign_sweep.py — X195: the phase census at two intermediate radii, to locate the change of sign.

X193 (radius 3, gap 10) and X192 (radius 6, gap 9) find the same mechanism - the bridge at fixed inflow decides the outcome - with
opposite signs of the inflow-outcome relation: the fusion share rises with the inflow at radius 3 (Spearman +0.413 over classes,
+0.515 over value means) and falls at radius 6 (-0.378, -0.833). This runs the same census at radius 4 gap 12 and radius 5 gap 10,
both with a centre separation of 20 cells, so the inflow band matches and only the body size changes.

Pre-registration: reports/2026-11-04-x195-sign-sweep-plan.md.
Run: python scripts/x195_sign_sweep.py --write
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
FIELDS = ROOT / "_hourly" / "x195_fields"
FLOW = "0.030"
STEPS = 400
GRID = 96
SCALE = 12.0
ARMS = [("r4_g12", 4.0, 12.0), ("r5_g10", 5.0, 10.0)]
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
    index = {"kind": "x195_sign_sweep", "flow": float(FLOW), "steps": STEPS, "save_at": SAVE_AT,
             "arms": [{"name": n, "radius": r, "gap": g, "sep": r * 2 + g} for n, r, g in ARMS],
             "prediction": "the phase decides the bridge at fixed inflow and the outcome follows it at both intermediate radii; the sign "
                           "of the inflow-outcome relation moves monotonically from positive at radius 3 to negative at radius 6, so radius 4 "
                           "leans positive and radius 5 leans negative",
             "runs": []}
    for name, radius, gap in ARMS:
        sep = 2 * radius + gap
        (FIELDS / name).mkdir(parents=True, exist_ok=True)
        classes = census(sep)
        index.setdefault("classes_per_arm", {})[name] = list(classes.values())
        for ci, c in enumerate(classes.values()):
            tag = f"{name}_c{ci:03d}"
            out = L1 / f"x195_{tag}.json"
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
                print(f"[x195] {name} c{ci:03d} {c['phase']} F_local {c['f_local']}: {status} ({round(time.time() - t0, 1)} s)")
    if args.write:
        (L1 / "x195_series_index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1) + "\n",
                                                   encoding="utf-8")
        counts = {a["name"]: sum(1 for r in index["runs"] if r["arm"] == a["name"] and r["status"] in ("ok", "skipped (exists)"))
                  for a in index["arms"]}
        print(f"[x195] index written: {counts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
