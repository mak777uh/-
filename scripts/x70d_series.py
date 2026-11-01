"""x70d_series.py — X70 re-run with dense component logging, for the stratified spatial control.

The first spatial control could only use 50–95 of 925 division events, because the artifacts log one snapshot per 1000
steps: a daughter's birth almost never coincides with a logged snapshot, so the structures present at her birth were
mostly unknown. This series repeats X70 with `--sample-every 50` and nothing else changed.

Why this is not a new experiment: logging is a recording branch (`field_track.py` writes `series` after the step and does
not touch the RNG), so the trajectory must be identical. The anchor checks exactly that — the seven rows that the old
artifacts kept (steps 1000…6000) must match the new run bit-for-bit.

Run:
    python scripts/x70d_series.py
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
    "--sample-every", "50", "--threshold", "0.2",
    "--freq-dep", "0.0", "--bin-width", "0.2", "--beta", "0.0", "--s-ref", "1.0", "--mutation", "0.15",
    "--overlap", "0.5", "--split-new-uid",
]

# Поле пишется каждые 200 шагов: пространственный контроль должен знать не только соседей, но и саму среду в точке
# рождения дочери (локальный приток, локальная занятость). Запись поля не трогает ГПСЧ (field_track.py §546).
FIELDS = ROOT / "morphogenesis" / "experiments" / "L1_field" / "_x70d_fields"
SAVE_AT = ",".join(str(s) for s in range(200, 6001, 200))

ARMS = {
    "pattern": ["--hetero-amp", "0.5", "--hetero-signal", "lab/streams/const_ones.json"],
    "homog": ["--hetero-amp", "0.0"],
}


def run_one(arm: str, seed: int) -> dict:
    out = L1 / f"x70d_{arm}_s{seed}.json"
    if out.exists():
        return {"arm": arm, "seed": seed, "status": "skipped (exists)"}
    cmd = [PY, str(TRACK), *COMMON, *ARMS[arm], "--seed", str(seed), "--out", str(out),
           "--save-fields", str(FIELDS), "--save-fields-at", SAVE_AT]
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
        return {"arm": arm, "seed": seed, "status": "ok", "seconds": round(dt, 1)}
    return last


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X70 dense-log re-run")
    ap.add_argument("--seeds", default="171-175")
    args = ap.parse_args(argv)
    lo, _, hi = args.seeds.partition("-")
    seeds = list(range(int(lo), int(hi or lo) + 1))

    rows = []
    for seed in seeds:
        for arm in ("pattern", "homog"):
            r = run_one(arm, seed)
            rows.append(r)
            print(f"[x70d] {arm:<7} seed {seed}: {r['status']} {r.get('seconds', '')} {r.get('tail', '')}", flush=True)
            if r["status"] in ("failed", "timeout"):
                (L1 / "x70d_series_index.json").write_text(
                    json.dumps({"kind": "x70d_series_index", "rows": rows}, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8", newline="\n")
                return 1
    (L1 / "x70d_series_index.json").write_text(
        json.dumps({"kind": "x70d_series_index", "rows": rows}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="\n")
    print(f"[x70d] done: {len(rows)} runs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
