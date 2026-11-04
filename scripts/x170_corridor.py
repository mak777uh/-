"""x170_corridor.py — X170: the field between two bodies at contact, at three inflow rates.

Surface gap 10 (SEP = 2R + gap = 16), radius 3, five seeds per rate, 2 000 steps, the field dumped every ten steps.
Pre-registration: reports/2026-11-04-x170-corridor-plan.md.
Run: python scripts/x170_corridor.py --write
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
FIELDS = ROOT / "_hourly" / "x170_fields"
RADIUS = 3.0
FLOWS = ("0.026", "0.030", "0.036")
SEEDS = tuple(range(971, 986))
GAP = 10
STEPS = 2000

COMMON = [
    "--steps", str(STEPS), "--grid", "96", "--dt", "1.0",
    "--Du", "0.16", "--Dv", "0.08", "--k", "0.06", "--eps", "0.0",
    "--hetero-scale", "12.0", "--hetero-period", "0.0", "--hetero-amp", "0.5",
    "--hetero-signal", "lab/streams/const_ones.json",
    "--sample-every", "10", "--threshold", "0.2",
    "--freq-dep", "0.0", "--bin-width", "0.2", "--beta", "0.0", "--s-ref", "1.0", "--mutation", "0.15",
    "--overlap", "0.5", "--split-new-uid", "--init-jitter",
    "--save-fields-every", "10", "--save-fields-at", "10",
]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    FIELDS.mkdir(parents=True, exist_ok=True)
    index = {"kind": "x170_corridor", "gap": GAP, "sep": 2 * RADIUS + GAP, "flows": list(FLOWS),
             "seeds": list(SEEDS), "steps": STEPS, "runs": []}
    for flow in FLOWS:
        for seed in SEEDS:
            tag = f"F{int(float(flow) * 1000)}_s{seed}"
            out = L1 / f"x170_{tag}.json"
            fdir = FIELDS / tag
            if out.exists() and out.stat().st_size > 0 and any(fdir.glob("*.npy")):
                index["runs"].append({"flow": flow, "seed": seed, "status": "skipped (exists)"})
                continue
            fdir.mkdir(parents=True, exist_ok=True)
            cmd = [PY, str(TRACK), *COMMON, "--device", args.device, "--F", flow, "--seed", str(seed),
                   "--out", str(out), "--save-fields", str(fdir),
                   "--init-spots", f"{RADIUS}:{2 * RADIUS + GAP:g}"]
            t0 = time.time()
            p = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=5000)
            dt = round(time.time() - t0, 1)
            status = "ok" if p.returncode == 0 else "failed"
            index["runs"].append({"flow": flow, "seed": seed, "status": status, "seconds": dt,
                                  "dumps": len(list(fdir.glob("*.npy"))),
                                  **({"tail": (p.stderr or p.stdout or "")[-300:]} if status == "failed" else {})})
            print(f"[x170] {tag}: {status} {dt}")
    if args.write:
        (L1 / "x170_series_index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1) + "\n",
                                                   encoding="utf-8")
        print("[x170] index written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
