"""x187_large_radius.py — X187: why do the largest bodies read the opposite sign?

X186 found the per-cell association between the outcome and the local inflow at the colder body to be positive in 9 of 11 cells -
as the law predicts - with the exceptions at the largest radius measured (r_eff 5.86: gap 7 slope -0.132, gap 9 slope -0.478).
The hypothesis this item tests is that at that size a WARM medium nucleates bodies of its own inside and around the pair, so the
component count never falls to one even though the fronts meet: the pair would then coalesce less the warmer its surroundings,
which is the observed sign.

Design: two arms, radius 6 gap 9 (the flipped cell) and radius 3 gap 10 (a cell with the law's sign), each at two levels of the
local inflow at the COLDER of the two seeded bodies, six seeds per level, 2 000 steps. The readout is the count of components
that appear between and around the pair (excluding the two seeded ones) at the sample where the component count is smallest,
plus the share.

Pre-registration: reports/2026-11-04-x187-nucleation-plan.md.
Run: python scripts/x187_large_radius.py --write
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
FIELDS = ROOT / "_hourly" / "x187_fields"
FLOW = "0.030"
STEPS = 3000
GRID = 96
SCALE = 12.0
PER_LEVEL = 6
ARMS = [("r6_g9", 6.0, 9.0), ("r3_g10", 3.0, 10.0)]
LEVELS = {"cold": 0.019, "warm": 0.030}
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


def site_of(seed: int, sep: float) -> tuple[float, float, float]:
    """(mid x, mid y, G at the colder body) — the arithmetic field_track.py uses for --init-spots."""
    g = GRID
    jr = np.random.default_rng(int(seed) + 9187)
    jx, jy = (int(v) for v in jr.integers(-g // 4, g // 4 + 1, size=2))
    cx, cy = g / 2.0 + jx, g / 2.0 + jy
    k = 2.0 * math.pi / SCALE

    def gat(x, y):
        return (math.sin(k * (int(round(y)) % g)) * math.cos(k * (int(round(x)) % g)) + 1.0) / 2.0

    g_cold = min(gat(cx - sep / 2.0, cy), gat(cx + sep / 2.0, cy))
    return cx, cy, g_cold


def pick(sep: float, target: float, start: int, stop: int) -> list[int]:
    out = []
    for seed in range(start, stop):
        if abs(float(FLOW) * (1 + 0.5 * (2 * site_of(seed, sep)[2] - 1)) - target) <= TOLERANCE:
            out.append(seed)
            if len(out) >= PER_LEVEL:
                break
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    FIELDS.mkdir(parents=True, exist_ok=True)

    plan = {}
    base = {"r6_g9": 40000, "r3_g10": 50000}
    for name, rad, gap in ARMS:
        sep = 2 * rad + gap
        plan[name] = {"radius": rad, "gap": gap, "sep": sep,
                      "groups": {lvl: pick(sep, tgt, base[name], base[name] + 30000)
                                 for lvl, tgt in LEVELS.items()}}
    index = {"kind": "x187_large_radius", "flow": FLOW, "steps": STEPS, "arms": plan, "tolerance": TOLERANCE,
             "prediction": {"r6_g9": "warm level coalesces LESS and shows MORE extra components around the pair",
                            "r3_g10": "warm level coalesces MORE and shows no such extra components"},
             "runs": []}

    for name, rad, gap in ARMS:
        sep = 2 * rad + gap
        for lvl, seeds in plan[name]["groups"].items():
            for seed in seeds:
                tag = f"{name}_{lvl}_s{seed}"
                out = L1 / f"x187_{tag}.json"
                if out.exists() and out.stat().st_size > 0:
                    index["runs"].append({"arm": name, "level": lvl, "seed": seed, "status": "skipped (exists)"})
                    continue
                cmd = [PY, str(TRACK), *COMMON, "--device", args.device, "--F", FLOW, "--seed", str(seed),
                       "--out", str(out), "--init-spots", f"{rad:g}:{sep:g}"]
                t0 = time.time()
                p = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8",
                                   errors="replace", timeout=12000)
                status = "ok" if p.returncode == 0 else "failed"
                index["runs"].append({"arm": name, "level": lvl, "seed": seed, "status": status,
                                      "seconds": round(time.time() - t0, 1),
                                      **({"tail": (p.stderr or p.stdout or "")[-300:]} if status == "failed" else {})})
                print(f"[x187] {tag}: {status}")
    if args.write:
        (L1 / "x187_series_index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1) + "\n",
                                                   encoding="utf-8")
        print("[x187] index written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
