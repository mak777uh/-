"""x193_phase_census_r3.py — X193: the phase census at radius 3 gap 10, the smaller-body arm.

X192 censused the phase classes at radius 6 gap 9 and found the bridge decided by the phase at fixed inflow, with the outcome
following it (logistic slope 6.094, z 5.76). The same census at the smaller bodies asks whether the phase decides there too and
whether the sign of the inflow-outcome relation is reversed, as X190 found at radius 3 (0 of 5 cold fused against 3 of 5 warm).

Pre-registration: reports/2026-11-04-x193-phase-census-r3-plan.md.
Run: python scripts/x193_phase_census_r3.py --write
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
FIELDS = ROOT / "_hourly" / "x193_fields"
FLOW = "0.030"
STEPS = 400
GRID = 96
SCALE = 12.0
RADIUS, GAP = 3.0, 10.0
SEP = 2 * RADIUS + GAP
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


def site_flow(key) -> float:
    g, k, f = GRID, 2.0 * math.pi / SCALE, float(FLOW)
    jx, jy = key
    cx, cy = g / 2.0 + jx, g / 2.0 + jy

    def gat(x, y):
        return (math.sin(k * (int(round(y)) % g)) * math.cos(k * (int(round(x)) % g)) + 1.0) / 2.0

    return f * (1 + 0.5 * (2 * min(gat(cx - SEP / 2.0, cy), gat(cx + SEP / 2.0, cy)) - 1))


def census():
    """One representative seed per phase class (first seed whose jitter lands on that phase)."""
    classes = {}
    for seed in range(SCAN):
        key = jitter(seed)
        ph = (key[0] % 12, key[1] % 12)
        if ph in classes:
            continue
        classes[ph] = {"phase": list(ph), "jitter": list(key), "seed": seed, "f_local": round(site_flow(key), 5)}
    return dict(sorted(classes.items()))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    FIELDS.mkdir(parents=True, exist_ok=True)
    classes = census()
    index = {"kind": "x193_phase_census_r3", "flow": float(FLOW), "radius": RADIUS, "gap": GAP, "sep": SEP,
             "steps": STEPS, "save_at": SAVE_AT, "classes": list(classes.values()),
             "prediction": "as at radius 6: the ratio depends on the phase beyond the inflow (spread at least 0.05 at the most crowded "
                           "value) and the outcome follows the bridge at fixed inflow (above-median ratio worlds fuse at least 0.3 more "
                           "often); and the sign of the inflow-outcome relation is REVERSED, with the top inflow value fusing more often "
                           "than the bottom",
             "runs": []}
    for ci, c in enumerate(classes.values()):
        tag = f"c{ci:03d}"
        out = L1 / f"x193_{tag}.json"
        fdir = FIELDS / tag
        if out.exists() and out.stat().st_size > 0:
            index["runs"].append({**c, "class_index": ci, "tag": tag, "status": "skipped (exists)"})
            continue
        cmd = [PY, str(TRACK), *COMMON, "--device", args.device, "--F", FLOW, "--seed", str(c["seed"]),
               "--out", str(out), "--init-spots", f"{RADIUS:g}:{SEP:g}",
               "--save-fields", str(fdir), "--save-fields-at", SAVE_AT]
        t0 = time.time()
        p = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=12000)
        status = "ok" if p.returncode == 0 else "failed"
        index["runs"].append({**c, "class_index": ci, "tag": tag, "status": status,
                              "seconds": round(time.time() - t0, 1),
                              **({"tail": (p.stderr or p.stdout or "")[-300:]} if status == "failed" else {})})
        if ci % 12 == 0 or status != "ok":
            print(f"[x193] {tag} {c['phase']} F_local {c['f_local']}: {status} ({round(time.time() - t0, 1)} s)")
    if args.write:
        (L1 / "x193_series_index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1) + "\n",
                                                   encoding="utf-8")
        ok = sum(1 for r in index["runs"] if r["status"] in ("ok", "skipped (exists)"))
        print(f"[x193] index written: {ok} of {len(classes)} classes ran")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
