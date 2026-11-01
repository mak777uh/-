"""x60_series.py — X60: the twenty field runs that keep their snapshots.

Preregistered in `reports/2026-11-01-x60-fields-and-masks-plan.md`. The anchor passed on 1 November 04:20: the
`--save-fields` flag is inert (bit-for-bit identical series with and without it, `anchor_x60/`), so this series differs
from `x18` only in what it writes to disk.

Two arms, paired by seed, exactly the `x18` design:

    heterogeneous   --hetero-amp 0.5 --hetero-signal lab/streams/const_ones.json
    homogeneous     --hetero-amp 0.0 --hetero-signal None

Each run writes `x60_<arm>_s<seed>.json` and three arrays `x60_<arm>_s<seed>_t{2000,4000,6000}.npy` (float32, 96×96).

Run:
    python scripts/x60_series.py --limit 2          # pilot: one seed, both arms
    python scripts/x60_series.py                    # the whole series
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
FIELDS = L1 / "x60_fields"

COMMON = [
    "--steps", "6000", "--grid", "96", "--dt", "1.0", "--device", "cuda",
    "--Du", "0.16", "--Dv", "0.08", "--F", "0.035", "--k", "0.06", "--eps", "0.0",
    "--hetero-scale", "12.0", "--hetero-period", "0.0",
    "--sample-every", "1000", "--threshold", "0.2",
    "--freq-dep", "1.0", "--bin-width", "0.2", "--beta", "0.2", "--s-ref", "1.0", "--mutation", "0.15",
    "--save-fields-at", "2000,4000,6000",
]

ARMS = {
    "pattern": ["--hetero-amp", "0.5", "--hetero-signal", "lab/streams/const_ones.json"],
    "homog": ["--hetero-amp", "0.0"],
}


def run_one(arm: str, seed: int) -> dict:
    out = L1 / f"x60_{arm}_s{seed}.json"
    if out.exists():
        return {"arm": arm, "seed": seed, "status": "skipped (exists)"}
    cmd = [PY, str(TRACK), *COMMON, *ARMS[arm],
           "--seed", str(seed), "--save-fields", str(FIELDS), "--out", str(out)]
    # Таймаут на прогон: 6000 шагов идут ~100 с, 900 с — это уже зависание (01.11: один homog-прогон
    # встал намертво на CUDA и держал серию 10 минут). Один повтор, потом честный failed в индексе.
    for attempt in (1, 2):
        t0 = time.time()
        try:
            proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True,
                                  encoding="utf-8", errors="replace", timeout=900)
        except subprocess.TimeoutExpired:
            dt = time.time() - t0
            last = {"arm": arm, "seed": seed, "status": "timeout", "seconds": round(dt, 1),
                    "attempt": attempt}
            continue
        dt = time.time() - t0
        if proc.returncode != 0:
            last = {"arm": arm, "seed": seed, "status": "failed", "seconds": round(dt, 1),
                    "attempt": attempt, "tail": (proc.stderr or proc.stdout or "")[-400:]}
            continue
        return {"arm": arm, "seed": seed, "status": "ok", "seconds": round(dt, 1), "attempt": attempt,
                "out": str(out.relative_to(ROOT))}
    return last
    return {"arm": arm, "seed": seed, "status": "ok", "seconds": round(dt, 1), "out": str(out.relative_to(ROOT))}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X60 series: field runs that keep v")
    ap.add_argument("--seeds", default="171-180")
    ap.add_argument("--limit", type=int, default=0, help="run only the first N seeds (pilot)")
    args = ap.parse_args(argv)

    lo, _, hi = args.seeds.partition("-")
    seeds = list(range(int(lo), int(hi or lo) + 1))
    if args.limit:
        seeds = seeds[: args.limit]

    FIELDS.mkdir(parents=True, exist_ok=True)
    rows = []
    for seed in seeds:
        for arm in ("pattern", "homog"):
            r = run_one(arm, seed)
            rows.append(r)
            print(f"[x60] {arm:<8} seed {seed}: {r['status']} {r.get('seconds', '')} {r.get('tail', '')}",
                  flush=True)
            if r["status"] == "failed":
                break
    (L1 / "x60_series_index.json").write_text(
        json.dumps({"kind": "x60_series_index", "rows": rows}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="\n")
    failed = [r for r in rows if r["status"] == "failed"]
    print(f"[x60] done: {len(rows)} runs, {len(failed)} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
