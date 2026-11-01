"""x66_series.py — X66: the grid map with the time step held fixed.

Preregistered in `reports/2026-11-01-x66-grid-map-plan.md`. Two new points, same `dt = 0.5`, same physical time, same
inflow in physical units:

    96  : Δx = 1.000, Du = 0.16,   Dv = 0.08
    108 : Δx = 0.889, Du = 0.2025, Dv = 0.10125

The existing 120 (X65) and 144 (X64) points already use `dt = 0.5`, so together these make a four-point map in which
resolution is the only variable that changes.

Run:
    python scripts/x66_series.py
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
FIELDS = L1 / "x66_fields"

BASE = [
    "--steps", "12000", "--dt", "0.5", "--device", "cuda",
    "--F", "0.035", "--k", "0.06", "--eps", "0.0",
    "--hetero-period", "0.0", "--sample-every", "1000", "--threshold", "0.2",
    "--freq-dep", "1.0", "--bin-width", "0.2", "--beta", "0.2", "--s-ref", "1.0", "--mutation", "0.15",
    "--save-fields-at", "4000,8000,12000",
]

GRIDS = {
    "g096": ["--grid", "96", "--Du", "0.16", "--Dv", "0.08", "--hetero-scale", "12.0"],
    "g108": ["--grid", "108", "--Du", "0.2025", "--Dv", "0.10125", "--hetero-scale", "13.5"],
}

ARMS = {
    "pattern": ["--hetero-amp", "0.5", "--hetero-signal", "lab/streams/const_ones.json"],
    "homog": ["--hetero-amp", "0.0"],
}


def run_one(grid: str, arm: str, seed: int) -> dict:
    out = L1 / f"x66_{grid}_{arm}_s{seed}.json"
    if out.exists():
        return {"grid": grid, "arm": arm, "seed": seed, "status": "skipped (exists)"}
    cmd = [PY, str(TRACK), *BASE, *GRIDS[grid], *ARMS[arm], "--seed", str(seed),
           "--save-fields", str(FIELDS), "--out", str(out)]
    last = {"grid": grid, "arm": arm, "seed": seed, "status": "failed"}
    for attempt in (1, 2):
        t0 = time.time()
        try:
            proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True,
                                  encoding="utf-8", errors="replace", timeout=1800)
        except subprocess.TimeoutExpired:
            last = {"grid": grid, "arm": arm, "seed": seed, "status": "timeout", "attempt": attempt}
            continue
        dt = time.time() - t0
        if proc.returncode != 0:
            last = {"grid": grid, "arm": arm, "seed": seed, "status": "failed", "attempt": attempt,
                    "seconds": round(dt, 1), "tail": (proc.stderr or proc.stdout or "")[-300:]}
            continue
        return {"grid": grid, "arm": arm, "seed": seed, "status": "ok", "seconds": round(dt, 1)}
    return last


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X66: grid map at fixed dt")
    ap.add_argument("--seeds", default="171-175")
    args = ap.parse_args(argv)
    lo, _, hi = args.seeds.partition("-")
    seeds = list(range(int(lo), int(hi or lo) + 1))

    FIELDS.mkdir(parents=True, exist_ok=True)
    rows = []
    for grid in ("g096", "g108"):
        for seed in seeds:
            for arm in ("homog", "pattern"):
                r = run_one(grid, arm, seed)
                rows.append(r)
                print(f"[x66] {grid} {arm:<7} seed {seed}: {r['status']} {r.get('seconds', '')} {r.get('tail', '')}",
                      flush=True)
                if r["status"] in ("failed", "timeout"):
                    (L1 / "x66_series_index.json").write_text(
                        json.dumps({"kind": "x66_series_index", "rows": rows}, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8", newline="\n")
                    return 1
    (L1 / "x66_series_index.json").write_text(
        json.dumps({"kind": "x66_series_index", "rows": rows}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="\n")
    print(f"[x66] done: {len(rows)} runs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
