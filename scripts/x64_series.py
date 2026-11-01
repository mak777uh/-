"""x64_series.py — X64: a real refinement (grid 144, dt 0.5, Du scaled by 1/dx^2 AND dt scaled with it).

Preregistered in `reports/2026-11-01-x64-real-refinement-plan.md`. The previous attempt (X58-lite) changed the physics
because the code has no Δx and the quantity that matters is `dt·Du·Δx²`. Here:

    96  : Δx = 1.000, Du = 0.16, dt = 1.0
    144 : Δx = 0.667, Du = 0.36, dt = 0.5   (dt·Du = 0.18 <= 0.25 stability bound)
    physical time kept at 6000 by running 12000 steps

The homogeneous arm must pattern at the same physical wavelength, 12 units = 18 cells at this Δx.

Run:
    python scripts/x64_series.py
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
TRACK = ROOT / "scripts" / "field_track.py"
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
FIELDS = L1 / "x64_fields"

COMMON = [
    "--steps", "12000", "--grid", "144", "--dt", "0.5", "--device", "cuda",
    "--Du", "0.36", "--Dv", "0.18", "--F", "0.035", "--k", "0.06", "--eps", "0.0",
    "--hetero-scale", "18.0", "--hetero-period", "0.0",
    "--sample-every", "1000", "--threshold", "0.2",
    "--freq-dep", "1.0", "--bin-width", "0.2", "--beta", "0.2", "--s-ref", "1.0", "--mutation", "0.15",
    "--save-fields-at", "4000,8000,12000",
]

ARMS = {
    "pattern": ["--hetero-amp", "0.5", "--hetero-signal", "lab/streams/const_ones.json"],
    "homog": ["--hetero-amp", "0.0"],
}


def run_one(arm: str, seed: int) -> dict:
    out = L1 / f"x64_{arm}_s{seed}.json"
    if out.exists():
        return {"arm": arm, "seed": seed, "status": "skipped (exists)"}
    cmd = [PY, str(TRACK), *COMMON, *ARMS[arm], "--seed", str(seed),
           "--save-fields", str(FIELDS), "--out", str(out)]
    last = {"arm": arm, "seed": seed, "status": "failed"}
    for attempt in (1, 2):
        t0 = time.time()
        try:
            proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True,
                                  encoding="utf-8", errors="replace", timeout=1800)
        except subprocess.TimeoutExpired:
            last = {"arm": arm, "seed": seed, "status": "timeout", "attempt": attempt}
            continue
        dt = time.time() - t0
        if proc.returncode != 0:
            last = {"arm": arm, "seed": seed, "status": "failed", "attempt": attempt,
                    "seconds": round(dt, 1), "tail": (proc.stderr or proc.stdout or "")[-300:]}
            continue
        return {"arm": arm, "seed": seed, "status": "ok", "seconds": round(dt, 1), "attempt": attempt}
    return last


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X64: grid 144 refinement")
    ap.add_argument("--seeds", default="171-175")
    args = ap.parse_args(argv)
    lo, _, hi = args.seeds.partition("-")
    seeds = list(range(int(lo), int(hi or lo) + 1))

    FIELDS.mkdir(parents=True, exist_ok=True)
    rows = []
    for seed in seeds:
        for arm in ("homog", "pattern"):
            r = run_one(arm, seed)
            rows.append(r)
            print(f"[x64] {arm:<7} seed {seed}: {r['status']} {r.get('seconds', '')} {r.get('tail', '')}", flush=True)
            if r["status"] in ("failed", "timeout"):
                (L1 / "x64_series_index.json").write_text(
                    json.dumps({"kind": "x64_series_index", "rows": rows}, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8", newline="\n")
                return 1
    (L1 / "x64_series_index.json").write_text(
        json.dumps({"kind": "x64_series_index", "rows": rows}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="\n")
    print(f"[x64] done: {len(rows)} runs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
