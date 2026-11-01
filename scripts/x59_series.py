"""x59_series.py — X59: is transmission a dose-response in the inflow amplitude?

Preregistered in `reports/2026-11-01-x59-amplitude-dose-plan.md`. Three amplitudes, everything else fixed: the trait
channel, the mutation, the seeds, the grid. If the sentence "transmission tracks the geometry of the field" is right, the
division count falls monotonically with the amplitude, and the spectrum sharpens as it does.

    a50   --hetero-amp 0.5   (the configuration behind the 311-split arm; positive control)
    a25   --hetero-amp 0.25
    a10   --hetero-amp 0.1

Fields saved at t = 2000, 4000, 6000 for the spectral half of the check.

Run:
    python scripts/x59_series.py
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
FIELDS = L1 / "x59_fields"

COMMON = [
    "--steps", "6000", "--grid", "96", "--dt", "1.0", "--device", "cuda",
    "--Du", "0.16", "--Dv", "0.08", "--F", "0.035", "--k", "0.06", "--eps", "0.0",
    "--hetero-signal", "lab/streams/const_ones.json", "--hetero-scale", "12.0", "--hetero-period", "0.0",
    "--sample-every", "1000", "--threshold", "0.2",
    "--freq-dep", "1.0", "--bin-width", "0.2", "--beta", "0.2", "--s-ref", "1.0", "--mutation", "0.15",
    "--save-fields-at", "2000,4000,6000",
]

ARMS = {
    "a50": ["--hetero-amp", "0.5"],
    "a25": ["--hetero-amp", "0.25"],
    "a10": ["--hetero-amp", "0.1"],
}


def run_one(arm: str, seed: int) -> dict:
    out = L1 / f"x59_{arm}_s{seed}.json"
    if out.exists():
        return {"arm": arm, "seed": seed, "status": "skipped (exists)"}
    cmd = [PY, str(TRACK), *COMMON, *ARMS[arm], "--seed", str(seed),
           "--save-fields", str(FIELDS), "--out", str(out)]
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
        return {"arm": arm, "seed": seed, "status": "ok", "seconds": round(dt, 1), "attempt": attempt}
    return last


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X59: amplitude dose-response")
    ap.add_argument("--seeds", default="171-175")
    args = ap.parse_args(argv)
    lo, _, hi = args.seeds.partition("-")
    seeds = list(range(int(lo), int(hi or lo) + 1))

    FIELDS.mkdir(parents=True, exist_ok=True)
    rows = []
    for seed in seeds:
        for arm in ("a50", "a25", "a10"):
            r = run_one(arm, seed)
            rows.append(r)
            print(f"[x59] {arm} seed {seed}: {r['status']} {r.get('seconds', '')} {r.get('tail', '')}", flush=True)
            if r["status"] in ("failed", "timeout"):
                (L1 / "x59_series_index.json").write_text(
                    json.dumps({"kind": "x59_series_index", "rows": rows}, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8", newline="\n")
                return 1
    (L1 / "x59_series_index.json").write_text(
        json.dumps({"kind": "x59_series_index", "rows": rows}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="\n")
    print(f"[x59] done: {len(rows)} runs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
