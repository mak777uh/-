"""x70_series.py — X70: size heredity in the neutral world.

Preregistered in `reports/2026-11-01-x70-size-heredity-plan.md`. The world has no trait feedback (`beta = 0`, `eps = 0`),
so the field is identical across identity rules; the only thing being measured is whether a daughter's peak area
resembles its parent's.

`--split-new-uid` gives daughters their own identities, which is what makes the peak-to-peak comparison possible at all.

Run:
    python scripts/x70_series.py
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

COMMON = [
    "--steps", "6000", "--grid", "96", "--dt", "1.0", "--device", "cuda",
    "--Du", "0.16", "--Dv", "0.08", "--F", "0.035", "--k", "0.06", "--eps", "0.0",
    "--hetero-scale", "12.0", "--hetero-period", "0.0",
    "--sample-every", "1000", "--threshold", "0.2",
    "--freq-dep", "0.0", "--bin-width", "0.2", "--beta", "0.0", "--s-ref", "1.0", "--mutation", "0.15",
    "--overlap", "0.5", "--split-new-uid",
]

ARMS = {
    "pattern": ["--hetero-amp", "0.5", "--hetero-signal", "lab/streams/const_ones.json"],
    "homog": ["--hetero-amp", "0.0"],
}


def run_one(arm: str, seed: int) -> dict:
    out = L1 / f"x70_{arm}_s{seed}.json"
    if out.exists():
        return {"arm": arm, "seed": seed, "status": "skipped (exists)"}
    cmd = [PY, str(TRACK), *COMMON, *ARMS[arm], "--seed", str(seed), "--out", str(out)]
    last = {"arm": arm, "seed": seed, "status": "failed"}
    for attempt in (1, 2):
        t0 = time.time()
        try:
            proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True,
                                  encoding="utf-8", errors="replace", timeout=900)
        except subprocess.TimeoutExpired:
            last = {"arm": arm, "seed": seed, "status": "timeout", "attempt": attempt}
            continue
        dt = time.time() - t0
        if proc.returncode != 0:
            last = {"arm": arm, "seed": seed, "status": "failed", "attempt": attempt,
                    "seconds": round(dt, 1), "tail": (proc.stderr or proc.stdout or "")[-300:]}
            continue
        return {"arm": arm, "seed": seed, "status": "ok", "seconds": round(dt, 1)}
    return last


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X70: size heredity")
    ap.add_argument("--seeds", default="171-175")
    args = ap.parse_args(argv)
    lo, _, hi = args.seeds.partition("-")
    seeds = list(range(int(lo), int(hi or lo) + 1))

    rows = []
    for seed in seeds:
        for arm in ("pattern", "homog"):
            r = run_one(arm, seed)
            rows.append(r)
            print(f"[x70] {arm:<7} seed {seed}: {r['status']} {r.get('seconds', '')} {r.get('tail', '')}", flush=True)
            if r["status"] in ("failed", "timeout"):
                (L1 / "x70_series_index.json").write_text(
                    json.dumps({"kind": "x70_series_index", "rows": rows}, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8", newline="\n")
                return 1
    (L1 / "x70_series_index.json").write_text(
        json.dumps({"kind": "x70_series_index", "rows": rows}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="\n")
    print(f"[x70] done: {len(rows)} runs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
