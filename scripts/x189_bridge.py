"""x189_bridge.py — X189: is the bridge between the bodies weaker when the site is warm?

X187 and X188 both failed to explain why the local-inflow law flips sign at the largest size, and X188's registered refusal rule
moves the question to the field level. X170 had already measured, by nominal rate, that the field between two bodies at contact is
**less filled the stronger the source** (0.52 / 0.48 / 0.39 of the body peak). This item asks the same question by local inflow and
by size: at radius 6 gap 9 - the arm whose sign is flipped - does a warm site leave a weaker bridge at contact than a cold one, so
that the pair touches and separates again instead of merging?

Design: two arms (radius 6 gap 9, radius 3 gap 10), two levels of the local inflow at the colder body (0.017 cold, 0.030 warm),
three seeds per group, 400 steps, the field v saved at steps 40, 60, 80, 100, 140, 200, 300 under _hourly/x189_fields.

Pre-registration: reports/2026-11-04-x189-bridge-plan.md.
Run: python scripts/x189_bridge.py --write
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
FIELDS = ROOT / "_hourly" / "x189_fields"
FLOW = "0.030"
STEPS = 400
GRID = 96
SCALE = 12.0
PER_LEVEL = 3
SAVE_AT = "40,60,80,100,140,200,300"
ARMS = [("r6_g9", 6.0, 9.0), ("r3_g10", 3.0, 10.0)]
LEVELS = {"cold": 0.017, "warm": 0.030}
TOLERANCE = 0.0025

COMMON = [
    "--steps", str(STEPS), "--grid", "96", "--dt", "1.0",
    "--Du", "0.16", "--Dv", "0.08", "--k", "0.06", "--eps", "0.0",
    "--hetero-scale", "12.0", "--hetero-period", "0.0", "--hetero-amp", "0.5",
    "--hetero-signal", "lab/streams/const_ones.json",
    "--sample-every", "10", "--threshold", "0.2",
    "--freq-dep", "0.0", "--bin-width", "0.2", "--beta", "0.0", "--s-ref", "1.0", "--mutation", "0.15",
    "--overlap", "0.5", "--split-new-uid", "--init-jitter",
]


def site_of(seed: int, sep: float):
    g = GRID
    jr = np.random.default_rng(int(seed) + 9187)
    jx, jy = (int(v) for v in jr.integers(-g // 4, g // 4 + 1, size=2))
    cx, cy = g / 2.0 + jx, g / 2.0 + jy
    k = 2.0 * math.pi / SCALE

    def gat(x, y):
        return (math.sin(k * (int(round(y)) % g)) * math.cos(k * (int(round(x)) % g)) + 1.0) / 2.0

    return cx, cy, min(gat(cx - sep / 2.0, cy), gat(cx + sep / 2.0, cy))


def pick(sep: float, target: float, start: int, stop: int) -> list[int]:
    out = []
    for seed in range(start, stop):
        if abs(float(FLOW) * (1 + 0.5 * (2 * site_of(seed, sep)[2] - 1)) - target) <= TOLERANCE:
            out.append(seed)
            if len(out) >= PER_LEVEL:
                break
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    FIELDS.mkdir(parents=True, exist_ok=True)
    base = {"r6_g9": 60000, "r3_g10": 70000}
    index = {"kind": "x189_bridge", "flow": FLOW, "steps": STEPS, "save_at": SAVE_AT,
             "prediction": "at radius 6 the warm level leaves a weaker bridge at contact (lower waist ratio) than the cold level; "
                           "at radius 3 the same direction with a smaller difference",
             "arms": {}, "runs": []}
    for name, rad, gap in ARMS:
        sep = 2 * rad + gap
        groups = {lvl: pick(sep, tgt, base[name], base[name] + 30000) for lvl, tgt in LEVELS.items()}
        index["arms"][name] = {"radius": rad, "gap": gap, "sep": sep, "groups": groups}
        for lvl, seeds in groups.items():
            for seed in seeds:
                tag = f"{name}_{lvl}_s{seed}"
                out = L1 / f"x189_{tag}.json"
                fdir = FIELDS / tag
                if out.exists() and out.stat().st_size > 0 and any(fdir.glob("*.npy")) if fdir.exists() else False:
                    index["runs"].append({"arm": name, "level": lvl, "seed": seed, "status": "skipped (exists)"})
                    continue
                cmd = [PY, str(TRACK), *COMMON, "--device", args.device, "--F", FLOW, "--seed", str(seed),
                       "--out", str(out), "--init-spots", f"{rad:g}:{sep:g}",
                       "--save-fields", str(fdir), "--save-fields-at", SAVE_AT]
                t0 = time.time()
                p = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8",
                                   errors="replace", timeout=12000)
                status = "ok" if p.returncode == 0 else "failed"
                index["runs"].append({"arm": name, "level": lvl, "seed": seed, "status": status,
                                      "seconds": round(time.time() - t0, 1),
                                      **({"tail": (p.stderr or p.stdout or "")[-300:]} if status == "failed" else {})})
                print(f"[x189] {tag}: {status} ({round(time.time() - t0, 1)} s)")
    if args.write:
        (L1 / "x189_series_index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1) + "\n",
                                                   encoding="utf-8")
        print("[x189] index written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
