"""x168b_series.py — X168b: the inflow matrix on one seed set and one run length.

Cells: F = 0.030 at gaps 8, 10, 11, 12 (the matched baseline) and F = 0.026 / 0.036 at gaps 8, 12, 14 (controls + brackets).
Seeds 961-965, 2 000 steps each.
Pre-registration: reports/2026-11-04-x168b-inflow-matrix-plan.md.
Run: python scripts/x168b_series.py --write
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

MATRIX = {
    "0.026": (8, 12, 14),
    "0.030": (8, 10, 11, 12),
    "0.036": (8, 12, 14),
}
SEEDS = (961, 962, 963, 964, 965)
STEPS = 2000

COMMON = [
    "--steps", str(STEPS), "--grid", "96", "--dt", "1.0",
    "--Du", "0.16", "--Dv", "0.08", "--k", "0.06", "--eps", "0.0",
    "--hetero-scale", "12.0", "--hetero-period", "0.0", "--hetero-amp", "0.5",
    "--hetero-signal", "lab/streams/const_ones.json",
    "--sample-every", "10", "--threshold", "0.2",
    "--freq-dep", "0.0", "--bin-width", "0.2", "--beta", "0.0", "--s-ref", "1.0", "--mutation", "0.15",
    "--overlap", "0.5", "--split-new-uid", "--init-jitter",
]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    index = {"kind": "x168b_series", "steps": STEPS, "matrix": MATRIX, "seeds": list(SEEDS), "runs": []}
    for flow, gaps in MATRIX.items():
        for gap in gaps:
            for seed in SEEDS:
                out = L1 / f"x168b_F{int(float(flow) * 1000)}_g{gap}_s{seed}.json"
                if out.exists() and out.stat().st_size > 0:
                    index["runs"].append({"flow": flow, "gap": gap, "seed": seed, "status": "skipped (exists)"})
                    continue
                cmd = [PY, str(TRACK), *COMMON, "--device", args.device, "--F", flow, "--seed", str(seed),
                       "--out", str(out), "--init-spots", f"3:{gap}"]
                t0 = time.time()
                p = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True,
                                   encoding="utf-8", errors="replace", timeout=5000)
                dt = round(time.time() - t0, 1)
                status = "ok" if p.returncode == 0 else "failed"
                index["runs"].append({"flow": flow, "gap": gap, "seed": seed, "status": status, "seconds": dt,
                                      **({"tail": (p.stderr or p.stdout or "")[-300:]} if status == "failed" else {})})
                print(f"[x168b] F{flow} g{gap} s{seed}: {status} {dt}")
    if args.write:
        (L1 / "x168b_series_index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1) + "\n",
                                                   encoding="utf-8")
        print("[x168b] index written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
