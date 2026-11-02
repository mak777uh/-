"""x81_series.py — prescribed spectrum: share of a second peak at fixed dominant (X81).

Preregistered in `reports/2026-11-02-x81-spectrum-plan.md`, committed before this ran. Four cells at `F = 0.030`:

    s0_q11     share 0.0, second peak at q = 11 (this is the single-scale reference cell)
    s05_q11    share 0.5, second peak at q = 11
    s10_q11    share 1.0, second peak at q = 11
    s10_q14    share 1.0, second peak at q = 14 (same share, different wavelength — the wavelength control)

Ten jittered worlds per cell, 6000 steps, field saved at 6000 so the *measured* power share can be checked against the prescribed
one. Phases are drawn per world inside the runner (private generator), so each seed realises a different world.

Run:
    python scripts/x81_series.py
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
FIELDS = L1 / "_x81_fields"

# cell -> (prescribed share, --hetero-scale2 in cells)
CELLS = {
    "s0_q11": (0.0, 96.0 / 11.0),
    "s05_q11": (0.5, 96.0 / 11.0),
    "s10_q11": (1.0, 96.0 / 11.0),
    "s10_q14": (1.0, 96.0 / 14.0),
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
    out = L1 / f"x81_{cell}_s{seed}.json"
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
    ap = argparse.ArgumentParser(description="X81: prescribed spectral share")
    ap.add_argument("--seeds", default="181-190")
    args = ap.parse_args(argv)
    lo, _, hi = args.seeds.partition("-")
    seeds = list(range(int(lo), int(hi or lo) + 1))

    rows = []
    for cell in CELLS:
        for seed in seeds:
            r = run_one(cell, seed)
            rows.append(r)
            print(f"[x81] {cell} seed {seed}: {r['status']} {r.get('seconds', '')} {r.get('tail', '')}", flush=True)
        if r["status"] in ("failed", "timeout"):
            (L1 / "x81_series_index.json").write_text(
                json.dumps({"kind": "x81_series_index", "rows": rows}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8", newline="\n")
            return 1
    (L1 / "x81_series_index.json").write_text(
        json.dumps({"kind": "x81_series_index", "rows": rows}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="\n")
    print(f"[x81] done: {len(rows)} runs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
