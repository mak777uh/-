"""x82_series.py — the reach of inflow modulation: prescribed vs realised spectral share (X82).

Preregistered in `reports/2026-11-02-x82-reach-plan.md`, committed before this ran. Five cells at `F = 0.030`, five jittered worlds
each (seeds 181-185), 6000 steps, field saved at 6000:

    s0_q11    prescribed power ratio 0    (single scale — the positive control)
    s1_q11    prescribed power ratio 1    (equal power in the pattern G)
    s4_q11    prescribed power ratio 4
    s16_q11   prescribed power ratio 16
    s4_q14    prescribed power ratio 4 at q = 14 (wavelength control)

The readout is the **realised** share `P2/(P1+P2)` measured from the saved field, not a peak count.

Run:
    python scripts/x82_series.py
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
FIELDS = L1 / "_x82_fields"

# cell -> (prescribed power ratio, --hetero-scale2 in cells)
CELLS = {
    "s0_q11": (0.0, 96.0 / 11.0),
    "s1_q11": (1.0, 96.0 / 11.0),
    "s4_q11": (4.0, 96.0 / 11.0),
    "s16_q11": (16.0, 96.0 / 11.0),
    "s4_q14": (4.0, 96.0 / 14.0),
}

COMMON = [
    "--steps", "6000", "--grid", "96", "--dt", "1.0", "--device", "cuda",
    "--Du", "0.16", "--Dv", "0.08", "--k", "0.06", "--eps", "0.0",
    "--hetero-scale", "12.0", "--hetero-period", "0.0", "--hetero-amp", "0.5", "--F", "0.030",
    "--save-fields", str(FIELDS), "--save-fields-at", "6000",
    "--hetero-signal", "lab/streams/const_ones.json",
    "--sample-every", "50", "--threshold", "0.2",
    "--freq-dep", "0.0", "--bin-width", "0.2", "--beta", "0.0", "--s-ref", "1.0", "--mutation", "0.15",
    "--overlap", "0.5", "--split-new-uid", "--init-jitter",
]


def run_one(cell: str, seed: int) -> dict:
    share, scale2 = CELLS[cell]
    out = L1 / f"x82_{cell}_s{seed}.json"
    if out.exists():
        return {"cell": cell, "seed": seed, "status": "skipped (exists)"}
    cmd = [PY, str(TRACK), *COMMON, "--hetero-scale2", f"{scale2:.4f}",
           "--spectrum-share", str(share), "--seed", str(seed), "--out", str(out)]
    last = {"cell": cell, "seed": seed, "status": "failed"}
    for attempt in (1, 2):
        t0 = time.time()
        try:
            proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True,
                                  encoding="utf-8", errors="replace", timeout=2400)
        except subprocess.TimeoutExpired:
            last = {"cell": cell, "seed": seed, "status": "timeout", "attempt": attempt}
            continue
        dt = time.time() - t0
        if proc.returncode != 0:
            last = {"cell": cell, "seed": seed, "status": "failed", "attempt": attempt,
                    "seconds": round(dt, 1), "tail": (proc.stderr or proc.stdout or "")[-300:]}
            continue
        return {"cell": cell, "seed": seed, "status": "ok", "seconds": round(dt, 1)}
    return last


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X82: reach of the imposed second peak")
    ap.add_argument("--seeds", default="181-185")
    args = ap.parse_args(argv)
    lo, _, hi = args.seeds.partition("-")
    seeds = list(range(int(lo), int(hi or lo) + 1))

    rows = []
    for cell in CELLS:
        for seed in seeds:
            r = run_one(cell, seed)
            rows.append(r)
            print(f"[x82] {cell} seed {seed}: {r['status']} {r.get('seconds', '')} {r.get('tail', '')}", flush=True)
        if r["status"] in ("failed", "timeout"):
            (L1 / "x82_series_index.json").write_text(
                json.dumps({"kind": "x82_series_index", "rows": rows}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8", newline="\n")
            return 1
    (L1 / "x82_series_index.json").write_text(
        json.dumps({"kind": "x82_series_index", "rows": rows}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="\n")
    print(f"[x82] done: {len(rows)} runs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
