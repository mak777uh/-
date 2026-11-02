"""x105_series.py — dense logging for the maze cell (X105).

Preregistered in `reports/2026-11-02-x105-dense-logging-plan.md`, committed before this ran.  Flags are X100's exactly
(`scripts/x100_series.py`), with one change: `--sample-every 10` instead of 50, so a structure that lives 89 steps is logged
nine times instead of once.  Seeds 301-310, two cells, twenty runs, ~105 s each.

Note the X85 rule: `--sample-every` is a physical parameter (trait draws happen per logged step), so these are new worlds, not
X100 at a finer resolution.  The comparison inside the series is cell against cell at the same density.

Run:
    python scripts/x105_series.py
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
FIELDS = L1 / "_x105_fields"

CELLS = {"f030": "0.030", "f040": "0.040"}

COMMON = [
    "--steps", "6000", "--grid", "96", "--dt", "1.0", "--device", "cuda",
    "--Du", "0.16", "--Dv", "0.08", "--k", "0.06", "--eps", "0.0",
    "--hetero-scale", "12.0", "--hetero-period", "0.0", "--hetero-amp", "0.5",
    "--save-fields", str(FIELDS), "--save-fields-every", "50",
    "--hetero-signal", "lab/streams/const_ones.json",
    "--sample-every", "10", "--threshold", "0.2",
    "--freq-dep", "0.0", "--bin-width", "0.2", "--beta", "0.0", "--s-ref", "1.0", "--mutation", "0.15",
    "--overlap", "0.5", "--split-new-uid", "--init-jitter",
]


def run_one(flow_tag: str, seed: int) -> dict:
    out = L1 / f"x105_{flow_tag}_s{seed}.json"
    if out.exists():
        return {"cell": flow_tag, "seed": seed, "status": "skipped (exists)"}
    cmd = [PY, str(TRACK), *COMMON, "--F", CELLS[flow_tag], "--seed", str(seed), "--out", str(out)]
    last = {"cell": flow_tag, "seed": seed, "status": "failed"}
    for attempt in (1, 2):
        t0 = time.time()
        try:
            proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True,
                                  encoding="utf-8", errors="replace", timeout=3000)
        except subprocess.TimeoutExpired:
            last.update({"status": "timeout", "attempt": attempt})
            continue
        dt = time.time() - t0
        if proc.returncode != 0:
            last.update({"status": "failed", "attempt": attempt, "seconds": round(dt, 1),
                         "tail": (proc.stderr or proc.stdout or "")[-300:]})
            continue
        return {"cell": flow_tag, "seed": seed, "status": "ok", "seconds": round(dt, 1)}
    return last


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X105: dense logging")
    ap.add_argument("--seeds", default="301-310")
    args = ap.parse_args(argv)
    lo, _, hi = args.seeds.partition("-")
    seeds = list(range(int(lo), int(hi or lo) + 1))

    index = L1 / "x105_series_index.json"
    rows = []
    for flow_tag in CELLS:
        for seed in seeds:
            r = run_one(flow_tag, seed)
            rows.append(r)
            print(f"[x105] {flow_tag} seed {seed}: {r['status']} {r.get('seconds', '')} {r.get('tail', '')}", flush=True)
            index.write_text(json.dumps({"kind": "x105_series_index", "rows": rows}, ensure_ascii=False, indent=2) + "\n",
                             encoding="utf-8", newline="\n")
            if r["status"] in ("failed", "timeout"):
                return 1
    print(f"[x105] done: {len(rows)} runs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
