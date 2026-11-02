"""x88_series.py — the high-inflow (percolating) arm at twenty worlds per cell (X88).

Preregistered in `reports/2026-11-02-x88-percolating-arm-plan.md`, committed before this ran. Flags identical to X87 (split on,
50-step logging, field at 6000) so the half-lives are comparable with X87's 1.82 / 1.16 / 1.07.

Run:
    python scripts/x88_series.py
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
FIELDS = L1 / "_x88_fields"

FLOWS = {"f040": "0.040", "f045": "0.045", "f050": "0.050"}

COMMON = [
    "--steps", "6000", "--grid", "96", "--dt", "1.0", "--device", "cuda",
    "--Du", "0.16", "--Dv", "0.08", "--k", "0.06", "--eps", "0.0",
    "--hetero-scale", "12.0", "--hetero-period", "0.0", "--hetero-amp", "0.5",
    "--save-fields", str(FIELDS), "--save-fields-at", "6000",
    "--hetero-signal", "lab/streams/const_ones.json",
    "--sample-every", "50", "--threshold", "0.2",
    "--freq-dep", "0.0", "--bin-width", "0.2", "--beta", "0.0", "--s-ref", "1.0", "--mutation", "0.15",
    "--overlap", "0.5", "--split-new-uid", "--init-jitter",
]


def run_one(flow: str, seed: int) -> dict:
    out = L1 / f"x88_{flow}_pattern_s{seed}.json"
    if out.exists():
        return {"flow": flow, "seed": seed, "status": "skipped (exists)"}
    cmd = [PY, str(TRACK), *COMMON, "--F", FLOWS[flow], "--seed", str(seed), "--out", str(out)]
    last = {"flow": flow, "seed": seed, "status": "failed"}
    for attempt in (1, 2):
        t0 = time.time()
        try:
            proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True,
                                  encoding="utf-8", errors="replace", timeout=2400)
        except subprocess.TimeoutExpired:
            last = {"flow": flow, "seed": seed, "status": "timeout", "attempt": attempt}
            continue
        dt = time.time() - t0
        if proc.returncode != 0:
            last = {"flow": flow, "seed": seed, "status": "failed", "attempt": attempt,
                    "seconds": round(dt, 1), "tail": (proc.stderr or proc.stdout or "")[-300:]}
            continue
        return {"flow": flow, "seed": seed, "status": "ok", "seconds": round(dt, 1)}
    return last


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X88: percolating arm")
    ap.add_argument("--seeds", default="241-260")
    args = ap.parse_args(argv)
    lo, _, hi = args.seeds.partition("-")
    seeds = list(range(int(lo), int(hi or lo) + 1))

    rows = []
    for flow in FLOWS:
        for seed in seeds:
            r = run_one(flow, seed)
            rows.append(r)
            print(f"[x88] {flow} seed {seed}: {r['status']} {r.get('seconds', '')} {r.get('tail', '')}", flush=True)
        if r["status"] in ("failed", "timeout"):
            (L1 / "x88_series_index.json").write_text(
                json.dumps({"kind": "x88_series_index", "rows": rows}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8", newline="\n")
            return 1
    (L1 / "x88_series_index.json").write_text(
        json.dumps({"kind": "x88_series_index", "rows": rows}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="\n")
    print(f"[x88] done: {len(rows)} runs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
