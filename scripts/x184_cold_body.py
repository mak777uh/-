"""x184_cold_body.py — X184: the same arm run at five chosen levels of the local inflow at the colder body.

X183 showed that the block's rate ladder collapses in the local inflow at the **colder of the two bodies**, not at the pair's
midpoint (AUC 0.898 within nominal levels against 0.213 for the midpoint). The two bodies sit at `+/-(SEP/2)` from the jittered
centre, so both of their `G` values, and their minimum, are computable before the run. This runner selects seeds by that minimum.
Radius 3, gap 10, F = 0.030, 2000 steps, six seeds per level, five levels.

Pre-registration: reports/2026-11-04-x184-cold-body-plan.md.
Run: python scripts/x184_cold_body.py --write
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
FIELDS = ROOT / "_hourly" / "x184_fields"
RADIUS = 3.0
GAP = 10
SEP = 2 * RADIUS + GAP
FLOW = "0.030"
STEPS = 2000
GRID = 96
HETERO_SCALE = 12.0
PER_LEVEL = 6
# five levels of the midpoint pattern value; the extremes are more than 0.5 apart, as the plan requires
LEVELS = [0.0155, 0.020, 0.025, 0.030, 0.036]
TOLERANCE = 0.002

COMMON = [
    "--steps", str(STEPS), "--grid", "96", "--dt", "1.0",
    "--Du", "0.16", "--Dv", "0.08", "--k", "0.06", "--eps", "0.0",
    "--hetero-scale", "12.0", "--hetero-period", "0.0", "--hetero-amp", "0.5",
    "--hetero-signal", "lab/streams/const_ones.json",
    "--sample-every", "10", "--threshold", "0.2",
    "--freq-dep", "0.0", "--bin-width", "0.2", "--beta", "0.0", "--s-ref", "1.0", "--mutation", "0.15",
    "--overlap", "0.5", "--split-new-uid", "--init-jitter",
    "--save-fields-every", "10", "--save-fields-at", "10",
]


def site_of(seed: int) -> tuple[float, float, float, float]:
    """(mid x, mid y, G at the colder body, F_local at the colder body) for the site this seed seeds at."""
    g = GRID
    jr = np.random.default_rng(int(seed) + 9187)
    jx, jy = (int(v) for v in jr.integers(-g // 4, g // 4 + 1, size=2))
    cx, cy = g / 2.0 + jx, g / 2.0 + jy
    ky = 2.0 * math.pi / max(2.0, HETERO_SCALE)

    def gat(x, y):
        return (math.sin(ky * (int(round(y)) % g)) * math.cos(ky * (int(round(x)) % g)) + 1.0) / 2.0

    g_cold = min(gat(cx - SEP / 2.0, cy), gat(cx + SEP / 2.0, cy))
    f_local = float(FLOW) * (1.0 + 0.5 * (2.0 * g_cold - 1.0))
    return cx, cy, g_cold, f_local


def pick_seeds(start: int = 8000, stop: int = 90000) -> dict:
    """First PER_LEVEL seeds whose site lands in each level's band."""
    chosen: dict[float, list[int]] = {lv: [] for lv in LEVELS}
    used: set[int] = set()
    for seed in range(start, stop):
        _, _, _, f_local = site_of(seed)
        for lv in LEVELS:
            if len(chosen[lv]) < PER_LEVEL and seed not in used and abs(f_local - lv) <= TOLERANCE:
                chosen[lv].append(seed)
                used.add(seed)
                break
        if all(len(chosen[lv]) >= PER_LEVEL for lv in LEVELS):
            break
    return chosen


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    FIELDS.mkdir(parents=True, exist_ok=True)

    chosen = pick_seeds()
    index = {"kind": "x184_cold_body", "flow": FLOW, "radius": RADIUS, "gap": GAP, "sep": SEP, "steps": STEPS,
             "levels": LEVELS, "tolerance": TOLERANCE, "per_level": PER_LEVEL,
             "prediction": {"coldest_share": [0.05, 0.40], "warmest_share": [0.45, 0.95], "trend": "positive, one-sided p < 0.05"},
             "selected": {str(lv): {"seeds": chosen[lv],
                                    "sites": [{"seed": s, "mid_x": round(site_of(s)[0], 2),
                                               "mid_y": round(site_of(s)[1], 2), "G_cold": round(site_of(s)[2], 4),
                                               "F_local_cold": round(site_of(s)[3], 5)}
                                              for s in chosen[lv]]}
                          for lv in LEVELS},
             "runs": []}

    for lv in LEVELS:
        for seed in chosen[lv]:
            tag = f"F{int(round(lv * 1000)):03d}_s{seed}"
            out = L1 / f"x184_{tag}.json"
            fdir = FIELDS / tag
            if out.exists() and out.stat().st_size > 0 and any(fdir.glob("*.npy")):
                index["runs"].append({"level": lv, "seed": seed, "status": "skipped (exists)"})
                continue
            fdir.mkdir(parents=True, exist_ok=True)
            cmd = [PY, str(TRACK), *COMMON, "--device", args.device, "--F", FLOW, "--seed", str(seed),
                   "--out", str(out), "--save-fields", str(fdir), "--init-spots", f"{RADIUS:g}:{SEP:g}"]
            t0 = time.time()
            p = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=8000)
            dt = round(time.time() - t0, 1)
            status = "ok" if p.returncode == 0 else "failed"
            index["runs"].append({"level": lv, "seed": seed, "status": status, "seconds": dt,
                                  "dumps": len(list(fdir.glob("*.npy"))),
                                  **({"tail": (p.stderr or p.stdout or "")[-300:]} if status == "failed" else {})})
            print(f"[x184] level {lv} {tag}: {status} {dt}")
    if args.write:
        (L1 / "x184_series_index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1) + "\n",
                                                   encoding="utf-8")
        print("[x184] index written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
