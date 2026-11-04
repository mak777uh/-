"""x182_local_inflow.py — X182: the same arm run at five chosen levels of the seeded site's local inflow.

`--init-spots R:SEP` places the pair at a site jittered by `default_rng(seed + 9187).integers(-g//4, g//4+1, size=2)`, and the
medium's fixed pattern makes the inflow there `F_local = F * 2G` with
`G = (sin(2*pi*y/12) * cos(2*pi*x/12) + 1) / 2`. Both are computable before the run, so seeds can be **selected by the level of
`G` they seed at**. Radius 3, gap 10, F = 0.030, 2000 steps, six seeds per level, five levels.

Pre-registration: reports/2026-11-04-x182-local-inflow-plan.md.
Run: python scripts/x182_local_inflow.py --write
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
FIELDS = ROOT / "_hourly" / "x182_fields"
RADIUS = 3.0
GAP = 10
SEP = 2 * RADIUS + GAP
FLOW = "0.030"
STEPS = 2000
GRID = 96
HETERO_SCALE = 12.0
PER_LEVEL = 6
# five levels of the midpoint pattern value; the extremes are more than 0.5 apart, as the plan requires
LEVELS = [0.08, 0.28, 0.50, 0.70, 0.90]
TOLERANCE = 0.05

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


def site_of(seed: int) -> tuple[float, float, float]:
    """(mid x, mid y, G) of the site this seed seeds at — the same arithmetic field_track.py uses."""
    g = GRID
    jr = np.random.default_rng(int(seed) + 9187)
    jx, jy = (int(v) for v in jr.integers(-g // 4, g // 4 + 1, size=2))
    cx, cy = g / 2.0 + jx, g / 2.0 + jy
    ky = 2.0 * math.pi / max(2.0, HETERO_SCALE)
    gr = (math.sin(ky * (cy % g)) * math.cos(ky * (cx % g)) + 1.0) / 2.0
    return cx, cy, gr


def pick_seeds(start: int = 3000, stop: int = 60000) -> dict:
    """First PER_LEVEL seeds whose site lands in each level's band."""
    chosen: dict[float, list[int]] = {lv: [] for lv in LEVELS}
    used: set[int] = set()
    for seed in range(start, stop):
        _, _, gr = site_of(seed)
        for lv in LEVELS:
            if len(chosen[lv]) < PER_LEVEL and seed not in used and abs(gr - lv) <= TOLERANCE:
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
    index = {"kind": "x182_local_inflow", "flow": FLOW, "radius": RADIUS, "gap": GAP, "sep": SEP, "steps": STEPS,
             "levels": LEVELS, "tolerance": TOLERANCE, "per_level": PER_LEVEL,
             "prediction": {"bottom_share": [0.5, 1.0], "top_share": [0.0, 0.35], "trend": "negative, one-sided p < 0.05"},
             "selected": {str(lv): {"seeds": chosen[lv],
                                    "sites": [{"seed": s, "mid_x": round(site_of(s)[0], 2),
                                               "mid_y": round(site_of(s)[1], 2), "G": round(site_of(s)[2], 4)}
                                              for s in chosen[lv]]}
                          for lv in LEVELS},
             "runs": []}

    for lv in LEVELS:
        for seed in chosen[lv]:
            tag = f"L{int(round(lv * 100)):03d}_s{seed}"
            out = L1 / f"x182_{tag}.json"
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
            print(f"[x182] level {lv} {tag}: {status} {dt}")
    if args.write:
        (L1 / "x182_series_index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1) + "\n",
                                                   encoding="utf-8")
        print("[x182] index written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
