"""x71_series.py — does one inflow support two morphologies? (preregistered in reports/2026-11-01-x71-multistability-plan.md)

Sweep the inflow F at fixed k and measure the selected wavelength per world. X70 found a graded one-generation memory of
form; multistability would turn it into a discrete, inheritable branch, which is the falsifier the external answers asked
for. The manipulation is F, the positive control is that the peak position moves monotonically across the sweep, and the
refusal rule is that an immobile or single-peaked readout means the question cannot be answered at this resolution.

Worlds are made different by `--init-jitter`: in a neutral world (`beta = 0`) the seed does not move the geometry, so the
five "seeds" of earlier arms were one world copied five times (`docs/design-checks.md`).

    F in {0.030, 0.035, 0.040, 0.045, 0.050} x {pattern, homog} x seeds 171-175 = 50 runs

Each run saves the v field at step 6000 (`_x71_fields/`), which is all the analysis needs.

Run:
    python scripts/x71_series.py
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
FIELDS = L1 / "_x71_fields"

COMMON = [
    "--steps", "6000", "--grid", "96", "--dt", "1.0", "--device", "cuda",
    "--Du", "0.16", "--Dv", "0.08", "--k", "0.06", "--eps", "0.0",
    "--hetero-scale", "12.0", "--hetero-period", "0.0",
    "--sample-every", "1000", "--threshold", "0.2",
    "--freq-dep", "0.0", "--bin-width", "0.2", "--beta", "0.0", "--s-ref", "1.0", "--mutation", "0.15",
    "--overlap", "0.5", "--init-jitter",
    "--save-fields", str(FIELDS), "--save-fields-at", "6000",
]

FLOWS = {"f025": "0.025", "f030": "0.030", "f035": "0.035", "f040": "0.040", "f045": "0.045",
         "f050": "0.050", "f055": "0.055"}
ARMS = {
    "pattern": ["--hetero-amp", "0.5", "--hetero-signal", "lab/streams/const_ones.json"],
    "homog": ["--hetero-amp", "0.0"],
}


def run_one(flow: str, arm: str, seed: int) -> dict:
    out = L1 / f"x71_{flow}_{arm}_s{seed}.json"
    if out.exists():
        return {"flow": flow, "arm": arm, "seed": seed, "status": "skipped (exists)"}
    cmd = [PY, str(TRACK), *COMMON, "--F", FLOWS[flow], *ARMS[arm], "--seed", str(seed), "--out", str(out)]
    last = {"flow": flow, "arm": arm, "seed": seed, "status": "failed"}
    for attempt in (1, 2):
        t0 = time.time()
        try:
            proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True,
                                  encoding="utf-8", errors="replace", timeout=900)
        except subprocess.TimeoutExpired:
            last = {"flow": flow, "arm": arm, "seed": seed, "status": "timeout", "attempt": attempt}
            continue
        dt = time.time() - t0
        if proc.returncode != 0:
            last = {"flow": flow, "arm": arm, "seed": seed, "status": "failed", "attempt": attempt,
                    "seconds": round(dt, 1), "tail": (proc.stderr or proc.stdout or "")[-300:]}
            continue
        return {"flow": flow, "arm": arm, "seed": seed, "status": "ok", "seconds": round(dt, 1)}
    return last


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X71: multistability scan of (F, k)")
    ap.add_argument("--seeds", default="171-175")
    args = ap.parse_args(argv)
    lo, _, hi = args.seeds.partition("-")
    seeds = list(range(int(lo), int(hi or lo) + 1))

    rows = []
    for flow in FLOWS:
        for arm in ("pattern", "homog"):
            for seed in seeds:
                r = run_one(flow, arm, seed)
                rows.append(r)
                print(f"[x71] {flow} {arm:<7} seed {seed}: {r['status']} {r.get('seconds', '')} {r.get('tail', '')}",
                      flush=True)
                if r["status"] in ("failed", "timeout"):
                    (L1 / "x71_series_index.json").write_text(
                        json.dumps({"kind": "x71_series_index", "rows": rows}, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8", newline="\n")
                    return 1
    (L1 / "x71_series_index.json").write_text(
        json.dumps({"kind": "x71_series_index", "rows": rows}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="\n")
    print(f"[x71] done: {len(rows)} runs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
