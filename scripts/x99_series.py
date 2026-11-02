"""x99_series.py — the memory map at two other excursion cuts (X99).

Preregistered in `reports/2026-11-02-x99-threshold-memory-plan.md`, committed before this ran. Two inflows, two thresholds, ten worlds
each; flags otherwise identical to X87/X88 so the half-lives are comparable with the committed 0.20 values (1.16 at 0.030, 2.08 at 0.040).

Run:
    python scripts/x99_series.py
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
FIELDS = L1 / "_x99_fields"

CELLS = {
    ("f030", "015"): ("0.030", "0.15"),
    ("f030", "025"): ("0.030", "0.25"),
    ("f040", "015"): ("0.040", "0.15"),
    ("f040", "025"): ("0.040", "0.25"),
}

COMMON = [
    "--steps", "6000", "--grid", "96", "--dt", "1.0", "--device", "cuda",
    "--Du", "0.16", "--Dv", "0.08", "--k", "0.06", "--eps", "0.0",
    "--hetero-scale", "12.0", "--hetero-period", "0.0", "--hetero-amp", "0.5",
    "--save-fields", str(FIELDS), "--save-fields-at", "6000",
    "--hetero-signal", "lab/streams/const_ones.json",
    "--sample-every", "50",
    "--freq-dep", "0.0", "--bin-width", "0.2", "--beta", "0.0", "--s-ref", "1.0", "--mutation", "0.15",
    "--overlap", "0.5", "--split-new-uid", "--init-jitter",
]


def run_one(flow_tag: str, thr_tag: str, seed: int) -> dict:
    flow, thr = CELLS[(flow_tag, thr_tag)]
    out = L1 / f"x99_{flow_tag}_thr{thr_tag}_s{seed}.json"
    if out.exists():
        return {"cell": f"{flow_tag}_thr{thr_tag}", "seed": seed, "status": "skipped (exists)"}
    cmd = [PY, str(TRACK), *COMMON, "--F", flow, "--threshold", thr, "--seed", str(seed), "--out", str(out)]
    last = {"cell": f"{flow_tag}_thr{thr_tag}", "seed": seed, "status": "failed"}
    for attempt in (1, 2):
        t0 = time.time()
        try:
            proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True,
                                  encoding="utf-8", errors="replace", timeout=2400)
        except subprocess.TimeoutExpired:
            last.update({"status": "timeout", "attempt": attempt})
            continue
        dt = time.time() - t0
        if proc.returncode != 0:
            last.update({"status": "failed", "attempt": attempt, "seconds": round(dt, 1),
                         "tail": (proc.stderr or proc.stdout or "")[-300:]})
            continue
        return {"cell": f"{flow_tag}_thr{thr_tag}", "seed": seed, "status": "ok", "seconds": round(dt, 1)}
    return last


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X99: memory at two excursion cuts")
    ap.add_argument("--seeds", default="281-290")
    args = ap.parse_args(argv)
    lo, _, hi = args.seeds.partition("-")
    seeds = list(range(int(lo), int(hi or lo) + 1))

    rows = []
    for (flow_tag, thr_tag) in CELLS:
        for seed in seeds:
            r = run_one(flow_tag, thr_tag, seed)
            rows.append(r)
            print(f"[x99] {r['cell']} seed {seed}: {r['status']} {r.get('seconds', '')} {r.get('tail', '')}", flush=True)
        if r["status"] in ("failed", "timeout"):
            (L1 / "x99_series_index.json").write_text(
                json.dumps({"kind": "x99_series_index", "rows": rows}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8", newline="\n")
            return 1
    (L1 / "x99_series_index.json").write_text(
        json.dumps({"kind": "x99_series_index", "rows": rows}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="\n")
    print(f"[x99] done: {len(rows)} runs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
