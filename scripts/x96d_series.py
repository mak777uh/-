"""x96d_series.py — X96d: does the second species move the orientation? Three seeds, two cells, four diffusion lengths.

Preregistered in `reports/2026-11-02-x96d-orientation-plan.md`, committed before this ran. `gamma = 0.05` is fixed by the pilot (the
coupling the medium absorbs); `Dw` runs to 0.64, four times Dv, which the pilot never reached.

Thirty runs: 3 seeds x 2 inflows x (4 Dw + 1 control). Each saves the field at step 6000 so the wavenumber and symmetry readouts come
from the same object as the run.

Run:
    python scripts/x96d_series.py
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
FIELDS = L1 / "_x96d_fields"

CELLS = {"f030": "0.030", "f040": "0.040"}
SEEDS = (411, 412, 413)
DWS = ("0.08", "0.16", "0.32", "0.64")
GAMMA = "0.05"

BASE = [
    "--steps", "6000", "--grid", "96", "--dt", "1.0", "--device", "cuda",
    "--Du", "0.16", "--Dv", "0.08", "--k", "0.06", "--eps", "0.0",
    "--hetero-scale", "12.0", "--hetero-period", "0.0", "--hetero-amp", "0.5",
    "--hetero-signal", "lab/streams/const_ones.json",
    "--sample-every", "50", "--threshold", "0.2",
    "--freq-dep", "0.0", "--bin-width", "0.2", "--beta", "0.0", "--s-ref", "1.0", "--mutation", "0.15",
    "--overlap", "0.5", "--split-new-uid", "--init-jitter",
]


def run_one(cell: str, flow: str, seed: int, dw: str | None) -> dict:
    tag = f"x96d_{cell}" if dw is None else f"x96d_{cell}_dw{dw.replace('.', '')}"
    out = L1 / f"{tag}_s{seed}.json"
    if out.exists():
        return {"cell": cell, "tag": tag, "seed": seed, "Dw": dw, "status": "skipped (exists)"}
    cmd = [PY, str(TRACK), *BASE, "--F", flow,
           "--save-fields", str(FIELDS), "--save-fields-at", "6000",
           "--seed", str(seed), "--out", str(out)]
    if dw is not None:
        cmd += ["--second-species", "--Dw", dw, "--gamma", GAMMA, "--beta-w", "0.05"]
    t0 = time.time()
    try:
        proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=3000)
        ok = proc.returncode == 0
        tail = (proc.stderr or proc.stdout or "")[-200:]
    except subprocess.TimeoutExpired:
        ok, tail = False, "timeout"
    return {"cell": cell, "tag": tag, "seed": seed, "Dw": dw,
            "status": "ok" if ok else "failed", "seconds": round(time.time() - t0, 1), "tail": tail}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X96d orientation series")
    ap.add_argument("--limit", type=int, default=0, help="stop after N runs (smoke test)")
    args = ap.parse_args(argv)

    FIELDS.mkdir(parents=True, exist_ok=True)
    index = L1 / "x96d_series_index.json"
    rows: list[dict] = []
    for cell, flow in CELLS.items():
        for seed in SEEDS:
            for dw in (None, *DWS):
                if args.limit and len(rows) >= args.limit:
                    print(f"[x96d] limit reached at {len(rows)} runs")
                    return 0
                r = run_one(cell, flow, seed, dw)
                rows.append(r)
                print(f"[x96d] {r['tag']} seed {seed}: {r['status']} {r.get('seconds', '')}", flush=True)
                index.write_text(json.dumps({"kind": "x96d_series_index", "rows": rows}, ensure_ascii=False, indent=2) + "\n",
                                 encoding="utf-8", newline="\n")
                if r["status"] == "failed":
                    return 1
    print(f"[x96d] done: {len(rows)} runs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
