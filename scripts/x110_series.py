"""x110_series.py — X110: gamma_cell by bisection. How large an autocatalysis cut does each cell survive?

Preregistered in `reports/2026-11-02-x110-gamma-cell-plan.md`, committed before this ran. Fifteen couplings per cell is too many for
thirty runs, so the grid is a bracket: gamma in {0.10, 0.15, 0.20, 0.30, 0.50} at Dw = 0.16, three seeds per cell, two inflows.
gamma_cell is reported as the largest coupling alive in at least two of three seeds — a bracket, not a calibrated constant.

Run:
    python scripts/x110_series.py
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
FIELDS = L1 / "_x110_fields"

CELLS = {"f030": "0.030", "f040": "0.040"}
SEEDS = (421, 422, 423)
GAMMAS = ("0.10", "0.15", "0.20", "0.30", "0.50")
DW = "0.16"

BASE = [
    "--steps", "6000", "--grid", "96", "--dt", "1.0", "--device", "cuda",
    "--Du", "0.16", "--Dv", "0.08", "--k", "0.06", "--eps", "0.0",
    "--hetero-scale", "12.0", "--hetero-period", "0.0", "--hetero-amp", "0.5",
    "--hetero-signal", "lab/streams/const_ones.json",
    "--sample-every", "50", "--threshold", "0.2",
    "--freq-dep", "0.0", "--bin-width", "0.2", "--beta", "0.0", "--s-ref", "1.0", "--mutation", "0.15",
    "--overlap", "0.5", "--split-new-uid", "--init-jitter",
]


def _lock(action: str, extra: list[str] | None = None) -> None:
    cmd = [PY, str(ROOT / "scripts" / "lab.py"), action,
           "--experiment", "X110_gamma_cell", "--owner", "lead"]
    if extra:
        cmd += extra
    try:
        subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=60)
    except Exception as exc:
        print(f"[x110] lock {action} failed: {exc}", flush=True)


def run_one(cell: str, flow: str, seed: int, gamma: str) -> dict:
    tag = f"x110_{cell}_g{gamma.replace('.', '')}"
    out = L1 / f"{tag}_s{seed}.json"
    if out.exists():
        return {"cell": cell, "tag": tag, "seed": seed, "gamma": gamma, "status": "skipped (exists)"}
    cmd = [PY, str(TRACK), *BASE, "--F", flow,
           "--save-fields", str(FIELDS), "--save-fields-at", "6000",
           "--seed", str(seed), "--out", str(out),
           "--second-species", "--Dw", DW, "--gamma", gamma, "--beta-w", "0.05"]
    t0 = time.time()
    try:
        proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=3000)
        ok = proc.returncode == 0
        tail = (proc.stderr or proc.stdout or "")[-200:]
    except subprocess.TimeoutExpired:
        ok, tail = False, "timeout"
    return {"cell": cell, "tag": tag, "seed": seed, "gamma": gamma,
            "status": "ok" if ok else "failed", "seconds": round(time.time() - t0, 1), "tail": tail}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X110 gamma_cell series")
    ap.add_argument("--limit", type=int, default=0, help="stop after N runs (smoke test)")
    args = ap.parse_args(argv)

    FIELDS.mkdir(parents=True, exist_ok=True)
    _lock("claim", ["--ttl-minutes", "180"])
    index = L1 / "x110_series_index.json"
    rows: list[dict] = []
    try:
        for cell, flow in CELLS.items():
            for seed in SEEDS:
                for gamma in GAMMAS:
                    if args.limit and len(rows) >= args.limit:
                        print(f"[x110] limit reached at {len(rows)} runs")
                        return 0
                    r = run_one(cell, flow, seed, gamma)
                    rows.append(r)
                    print(f"[x110] {r['tag']} seed {seed}: {r['status']} {r.get('seconds', '')}", flush=True)
                    index.write_text(json.dumps({"kind": "x110_series_index", "rows": rows},
                                                ensure_ascii=False, indent=2) + "\n",
                                     encoding="utf-8", newline="\n")
                    _lock("heartbeat")
                    if r["status"] == "failed":
                        return 1
    finally:
        _lock("release")
    print(f"[x110] done: {len(rows)} runs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
