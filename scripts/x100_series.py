"""x100_series.py — heredity with a size that needs no excursion cut (X100).

Preregistered in `reports/2026-11-02-x100-cutfree-plan.md`, committed before this ran. Flags identical to X87/X88 plus
--save-fields-every 50, so every logged snapshot has a field and a structure can be measured at its own peak.

Run:
    python scripts/x100_series.py
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
FIELDS = L1 / "_x100_fields"

CELLS = {"f030": "0.030", "f040": "0.040"}

COMMON = [
    "--steps", "6000", "--grid", "96", "--dt", "1.0", "--device", "cuda",
    "--Du", "0.16", "--Dv", "0.08", "--k", "0.06", "--eps", "0.0",
    "--hetero-scale", "12.0", "--hetero-period", "0.0", "--hetero-amp", "0.5",
    "--save-fields", str(FIELDS), "--save-fields-every", "50",
    "--hetero-signal", "lab/streams/const_ones.json",
    "--sample-every", "50", "--threshold", "0.2",
    "--freq-dep", "0.0", "--bin-width", "0.2", "--beta", "0.0", "--s-ref", "1.0", "--mutation", "0.15",
    "--overlap", "0.5", "--split-new-uid", "--init-jitter",
]


def run_one(flow_tag: str, seed: int) -> dict:
    out = L1 / f"x100_{flow_tag}_s{seed}.json"
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
    ap = argparse.ArgumentParser(description="X100: cut-free size")
    ap.add_argument("--seeds", default="291-300")
    args = ap.parse_args(argv)
    lo, _, hi = args.seeds.partition("-")
    seeds = list(range(int(lo), int(hi or lo) + 1))

    rows = []
    for flow_tag in CELLS:
        for seed in seeds:
            r = run_one(flow_tag, seed)
            rows.append(r)
            print(f"[x100] {flow_tag} seed {seed}: {r['status']} {r.get('seconds', '')} {r.get('tail', '')}", flush=True)
        if r["status"] in ("failed", "timeout"):
            (L1 / "x100_series_index.json").write_text(
                json.dumps({"kind": "x100_series_index", "rows": rows}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8", newline="\n")
            return 1
    (L1 / "x100_series_index.json").write_text(
        json.dumps({"kind": "x100_series_index", "rows": rows}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="\n")
    print(f"[x100] done: {len(rows)} runs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
