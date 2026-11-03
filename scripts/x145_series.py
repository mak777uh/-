"""x145_series.py — X145: one radius-3 disc and nothing else (`--init-spots 3:0`).

The whole mixing-length block seeds two discs. This seeds one: with SEP = 0 the flag's two centres coincide and the
initial condition is a single disc of radius 3, the same construction `x140_sep0_s*` (radius 4.5) and `x138_sep0_s*`
(radius 6) already use as a control. The question is when this disc first splits, because that time is the candidate
explanation of where mutual coalescence ends.

Run:
    python scripts/x145_series.py
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

RADIUS = 3
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


def run_one(seed: int, out: Path) -> dict:
    if out.exists() and out.stat().st_size > 0:
        return {"seed": seed, "status": "skipped (exists)"}
    cmd = [PY, str(TRACK), *COMMON, "--F", FLOW, "--seed", str(seed), "--out", str(out),
           "--init-spots", f"{RADIUS}:0"]
    last = {"seed": seed, "status": "failed"}
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
        return {"seed": seed, "status": "ok", "seconds": round(dt, 1)}
    return last


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X145 lone disc")
    ap.add_argument("--seeds", default="")
    args = ap.parse_args(argv)
    seeds = [int(s) for s in args.seeds.split(",") if s.strip()] or list(SEEDS)
    index = L1 / "x145_series_index.json"
    rows = []
    for seed in seeds:
        out = L1 / f"x145_lone_r30_s{seed}.json"
        r = run_one(seed, out)
        rows.append(r)
        print(f"[x145] lone disc seed {seed}: {r['status']} {r.get('seconds', '')} {r.get('tail', '')}", flush=True)
        index.write_text(json.dumps({"kind": "x145_series_index", "rows": rows},
                                    ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if r["status"] in ("failed", "timeout"):
            return 1
    print(f"[x145] done: {len(rows)} runs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
