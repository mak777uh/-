"""x150_series.py — X150: a third radius (6.0) at surface gaps 6, 7 and 8.

Radius 6 discs, separations 18, 19 and 20 cells, five seeds each, at the same inflow as the rest of the block. The
prediction registered in reports/2026-11-03-x150-radius6-plan.md: 5/5 mutual coalescence at gap 6, mixed at gap 7, and
median times 29 / 39 / 49 logged steps in the all-coalescing arms.

Run:
    python scripts/x150_series.py
    python scripts/x150_series.py --seeds 601,602
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

RADIUS = 6.0
ARMS = ((6, 18), (7, 19), (8, 20))
SEEDS = (601, 602, 603, 604, 605)
FLOW = "0.030"

COMMON = [
    "--steps", "6000", "--grid", "96", "--dt", "1.0", "--device", "cuda",
    "--Du", "0.16", "--Dv", "0.08", "--k", "0.06", "--eps", "0.0",
    "--hetero-scale", "12.0", "--hetero-period", "0.0", "--hetero-amp", "0.5",
    "--hetero-signal", "lab/streams/const_ones.json",
    "--sample-every", "10", "--threshold", "0.2",
    "--freq-dep", "0.0", "--bin-width", "0.2", "--beta", "0.0", "--s-ref", "1.0", "--mutation", "0.15",
    "--overlap", "0.5", "--split-new-uid", "--init-jitter",
]


def run_one(seed: int, gap: int, sep: int, out: Path) -> dict:
    if out.exists() and out.stat().st_size > 0:
        return {"seed": seed, "gap": gap, "status": "skipped (exists)"}
    cmd = [PY, str(TRACK), *COMMON, "--F", FLOW, "--seed", str(seed), "--out", str(out),
           "--init-spots", f"{RADIUS}:{sep}"]
    last = {"seed": seed, "gap": gap, "status": "failed"}
    for attempt in (1, 2):
        t0 = time.time()
        try:
            proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True,
                                  encoding="utf-8", errors="replace", timeout=4000)
        except subprocess.TimeoutExpired:
            last.update({"status": "timeout", "attempt": attempt})
            continue
        dt = time.time() - t0
        if proc.returncode != 0:
            last.update({"status": "failed", "attempt": attempt, "seconds": round(dt, 1),
                         "tail": (proc.stderr or proc.stdout or "")[-300:]})
            continue
        return {"seed": seed, "gap": gap, "status": "ok", "seconds": round(dt, 1)}
    return last


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X150 radius 6 at gaps 6-8")
    ap.add_argument("--seeds", default="")
    args = ap.parse_args(argv)
    seeds = [int(s) for s in args.seeds.split(",") if s.strip()] or list(SEEDS)
    index = L1 / "x150_series_index.json"
    rows = []
    for gap, sep in ARMS:
        for seed in seeds:
            out = L1 / f"x150_g{gap}_r60_s{seed}.json"
            r = run_one(seed, gap, sep, out)
            rows.append(r)
            print(f"[x150] R6 gap {gap} seed {seed}: {r['status']} {r.get('seconds', '')} "
                  f"{r.get('tail', '')}", flush=True)
            index.write_text(json.dumps({"kind": "x150_series_index", "rows": rows},
                                        ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            if r["status"] in ("failed", "timeout"):
                return 1
    print(f"[x150] done: {len(rows)} runs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
