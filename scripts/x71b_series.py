"""x71b_series.py — does the two-branch coexistence of X71 survive 24 000 steps?

Preregistered in `reports/2026-11-01-x71b-persistence-plan.md`. Same inflow as the X71 boundary cell, five jittered worlds,
fields at four horizons so the question "both modes or one winner" is answered by the same readout X71 used.

Run:
    python scripts/x71b_series.py
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
FIELDS = L1 / "_x71b_fields"

COMMON = [
    "--steps", "24000", "--grid", "96", "--dt", "1.0", "--device", "cuda",
    "--Du", "0.16", "--Dv", "0.08", "--F", "0.035", "--k", "0.06", "--eps", "0.0",
    "--hetero-scale", "12.0", "--hetero-period", "0.0", "--hetero-amp", "0.5",
    "--hetero-signal", "lab/streams/const_ones.json",
    "--sample-every", "1000", "--threshold", "0.2",
    "--freq-dep", "0.0", "--bin-width", "0.2", "--beta", "0.0", "--s-ref", "1.0", "--mutation", "0.15",
    "--overlap", "0.5", "--split-new-uid", "--init-jitter",
    "--save-fields", str(FIELDS), "--save-fields-at", "6000,12000,18000,24000",
]


def run_one(seed: int) -> dict:
    out = L1 / f"x71b_pattern_s{seed}.json"
    if out.exists():
        return {"seed": seed, "status": "skipped (exists)"}
    cmd = [PY, str(TRACK), *COMMON, "--seed", str(seed), "--out", str(out)]
    last = {"seed": seed, "status": "failed"}
    for attempt in (1, 2):
        t0 = time.time()
        try:
            proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True,
                                  encoding="utf-8", errors="replace", timeout=2400)
        except subprocess.TimeoutExpired:
            last = {"seed": seed, "status": "timeout", "attempt": attempt}
            continue
        dt = time.time() - t0
        if proc.returncode != 0:
            last = {"seed": seed, "status": "failed", "attempt": attempt,
                    "seconds": round(dt, 1), "tail": (proc.stderr or proc.stdout or "")[-300:]}
            continue
        return {"seed": seed, "status": "ok", "seconds": round(dt, 1)}
    return last


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X71b: persistence of the two-branch coexistence")
    ap.add_argument("--seeds", default="171-175")
    args = ap.parse_args(argv)
    lo, _, hi = args.seeds.partition("-")
    seeds = list(range(int(lo), int(hi or lo) + 1))

    rows = []
    for seed in seeds:
        r = run_one(seed)
        rows.append(r)
        print(f"[x71b] seed {seed}: {r['status']} {r.get('seconds', '')} {r.get('tail', '')}", flush=True)
        if r["status"] in ("failed", "timeout"):
            (L1 / "x71b_series_index.json").write_text(
                json.dumps({"kind": "x71b_series_index", "rows": rows}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8", newline="\n")
            return 1
    (L1 / "x71b_series_index.json").write_text(
        json.dumps({"kind": "x71b_series_index", "rows": rows}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="\n")
    print(f"[x71b] done: {len(rows)} runs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
