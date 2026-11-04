"""x165_series.py — X165: three bodies in a row, at gaps 8, 10 and 12.

Pre-registration: reports/2026-11-04-x165-three-bodies-plan.md.
Run: python scripts/x165_series.py --write
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

ARMS = (8, 10, 12)
RADIUS = 3.0
N = 3
SEEDS = (981, 982, 983, 984, 985)
FLOW = "0.030"
STEPS = 6000

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
    ap.add_argument("--seeds", default="")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    seeds = [int(s) for s in args.seeds.split(",") if s.strip()] or list(SEEDS)
    index = {"kind": "x165_series", "steps": STEPS, "flow": FLOW, "n": N, "radius": RADIUS,
             "gaps": list(ARMS), "seeds": seeds, "runs": []}
    for gap in ARMS:
        for seed in seeds:
            out = L1 / f"x165_row3_g{gap}_s{seed}.json"
            if out.exists() and out.stat().st_size > 0:
                index["runs"].append({"gap": gap, "seed": seed, "status": "skipped (exists)"})
                print(f"[x165] g{gap} s{seed}: skipped")
                continue
            cmd = [PY, str(TRACK), *COMMON, "--device", args.device, "--F", FLOW, "--seed", str(seed),
                   "--out", str(out), "--init-row", f"{N}:{RADIUS}:{gap}"]
            t0 = time.time()
            p = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=5000)
            dt = round(time.time() - t0, 1)
            status = "ok" if p.returncode == 0 else "failed"
            index["runs"].append({"gap": gap, "seed": seed, "status": status, "seconds": dt,
                                  **({"tail": (p.stderr or p.stdout or "")[-300:]} if status == "failed" else {})})
            print(f"[x165] g{gap} s{seed}: {status} {dt}")
    if args.write:
        (L1 / "x165_series_index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1) + "\n",
                                                   encoding="utf-8")
        print("[x165] index written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
