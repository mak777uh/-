"""e6q_series.py — E6q: turn the niches off.

The sentence E6p produced is *selection is easy, coexistence is a property of the environment*. The direct test is to
remove the environment: same two regimes, homogeneous inflow instead of the heterogeneous field.

    ctrl_h    beta = 0.0, freq_dep = 0, hetero_amp = 0.0
    survfd_h  beta = 0.2, freq_dep = 1, hetero_amp = 0.0

Prediction, written before the data: if coexistence needs niches, `survfd_h` should end with **fewer than 2.5**
structures (the heterogeneous `survfd` median from E6p) and fixate in more seeds; if it keeps 2.5 or more, the niches are
not what holds the structures and the sentence is wrong.

Preregistration: `reports/2026-11-01-e6q-no-niches-plan.md`.

Run:
    python scripts/e6q_series.py
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
    "--Du", "0.16", "--Dv", "0.08", "--F", "0.035", "--k", "0.06",
    "--sample-every", "1000", "--threshold", "0.2",
    "--eps", "0.0", "--bin-width", "0.2", "--s-ref", "1.0", "--mutation", "0.15",
    "--hetero-amp", "0.0",
]

ARMS = {
    "ctrl_h": ["--beta", "0.0", "--freq-dep", "0.0"],
    "survfd_h": ["--beta", "0.2", "--freq-dep", "1.0"],
}


def run_one(arm: str, seed: int) -> dict:
    out = L1 / f"e6q_{arm}_s{seed}.json"
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
        return {"arm": arm, "seed": seed, "status": "ok", "seconds": round(dt, 1), "attempt": attempt}
    return last


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="E6q: same regimes, no niches")
    ap.add_argument("--seeds", default="171-180")
    args = ap.parse_args(argv)
    lo, _, hi = args.seeds.partition("-")
    seeds = list(range(int(lo), int(hi or lo) + 1))
    rows = []
    for seed in seeds:
        for arm in ("ctrl_h", "survfd_h"):
            r = run_one(arm, seed)
            rows.append(r)
            print(f"[e6q] {arm:<9} seed {seed}: {r['status']} {r.get('seconds', '')} {r.get('tail', '')}", flush=True)
            if r["status"] in ("failed", "timeout"):
                (L1 / "e6q_series_index.json").write_text(
                    json.dumps({"kind": "e6q_series_index", "rows": rows}, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8", newline="\n")
                return 1
    (L1 / "e6q_series_index.json").write_text(
        json.dumps({"kind": "e6q_series_index", "rows": rows}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="\n")
    print(f"[e6q] done: {len(rows)} runs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
