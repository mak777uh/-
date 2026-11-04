"""x158_series.py — X158: the missing arms that turn the X157 band into a measured crossing.

Radius 4.5 at design gaps 10 and 11, radius 6 at gaps 9, 10 and 11, radius 3 at gaps 10 and 11 (the last two re-run at
seeds that were never used), ten seeds each, one inflow, CPU. The pre-registration, the positive control and the refusal
rule are in reports/2026-11-04-x158-crossing-plan.md.

Run:
    python scripts/x158_series.py
    python scripts/x158_series.py --seeds 701,702 --device cuda
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

ARMS = (
    (3.0, 10, 16),
    (3.0, 11, 17),
    (4.5, 10, 19),
    (4.5, 11, 20),
    (6.0, 9, 21),
    (6.0, 10, 22),
    (6.0, 11, 23),
)
SEEDS = tuple(range(701, 711))
FLOW = "0.030"

COMMON = [
    "--steps", "6000", "--grid", "96", "--dt", "1.0",
    "--Du", "0.16", "--Dv", "0.08", "--k", "0.06", "--eps", "0.0",
    "--hetero-scale", "12.0", "--hetero-period", "0.0", "--hetero-amp", "0.5",
    "--hetero-signal", "lab/streams/const_ones.json",
    "--sample-every", "10", "--threshold", "0.2",
    "--freq-dep", "0.0", "--bin-width", "0.2", "--beta", "0.0", "--s-ref", "1.0", "--mutation", "0.15",
    "--overlap", "0.5", "--split-new-uid", "--init-jitter",
]


def tag(radius: float) -> str:
    return f"r{int(round(radius * 10))}"


def run_one(seed: int, radius: float, gap: int, sep: int, out: Path, device: str) -> dict:
    if out.exists() and out.stat().st_size > 0:
        return {"seed": seed, "radius": radius, "gap": gap, "status": "skipped (exists)"}
    cmd = [PY, str(TRACK), *COMMON, "--device", device, "--F", FLOW, "--seed", str(seed),
           "--out", str(out), "--init-spots", f"{radius}:{sep}"]
    last = {"seed": seed, "radius": radius, "gap": gap, "status": "failed"}
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
        return {"seed": seed, "radius": radius, "gap": gap, "status": "ok", "seconds": round(dt, 1)}
    return last


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X158: the crossing, at three radii")
    ap.add_argument("--seeds", default="")
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--radii", default="", help="comma-separated radii to run, for parallel radius groups")
    ap.add_argument("--index-tag", default="", help="suffix for the index file when jobs run in parallel")
    args = ap.parse_args(argv)
    seeds = [int(s) for s in args.seeds.split(",") if s.strip()] or list(SEEDS)
    wanted = {float(v) for v in args.radii.split(",") if v.strip()}
    arms = [a for a in ARMS if not wanted or a[0] in wanted]
    index = L1 / ("x158_series_index" + (f"_{args.index_tag}" if args.index_tag else "") + ".json")
    rows = []
    for radius, gap, sep in arms:
        for seed in seeds:
            out = L1 / f"x158_g{gap}_{tag(radius)}_s{seed}.json"
            r = run_one(seed, radius, gap, sep, out, args.device)
            rows.append(r)
            print(f"[x158] r{radius} gap {gap} seed {seed}: {r['status']} {r.get('seconds', '')} "
                  f"{r.get('tail', '')}", flush=True)
            index.write_text(json.dumps({"kind": "x158_series_index", "rows": rows},
                                        ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            if r["status"] in ("failed", "timeout"):
                return 1
    print(f"[x158] done: {len(rows)} runs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
