"""x174_gap_corridor.py — X174: the corridor at contact at three surface gaps, one size, one rate.

Radius 3, F = 0.030: gap 8 (seeds 1031-1040, ten) and gap 9 (seeds 1031-1045, fifteen), 2 000 steps, field dumps every ten
steps. The gap-10 arm is X170's.
Pre-registration: reports/2026-11-04-x174-gap-corridor-plan.md.
Run: python scripts/x174_gap_corridor.py --write
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
FIELDS = ROOT / "_hourly" / "x174_fields"
RADIUS = 3.0
FLOW = "0.030"
JOBS = ((8, tuple(range(1031, 1041))), (9, tuple(range(1031, 1046))))
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
    index = {"kind": "x174_gap_corridor", "flow": FLOW, "radius": RADIUS, "steps": STEPS,
             "arms": [{"gap": g, "seeds": list(s)} for g, s in JOBS], "runs": []}
    for gap, seeds in JOBS:
        sep = 2 * RADIUS + gap
        for seed in seeds:
            tag = f"g{gap}_s{seed}"
            out = L1 / f"x174_{tag}.json"
            fdir = FIELDS / tag
            if out.exists() and out.stat().st_size > 0 and any(fdir.glob("*.npy")):
                index["runs"].append({"gap": gap, "seed": seed, "status": "skipped (exists)"})
                continue
            fdir.mkdir(parents=True, exist_ok=True)
            cmd = [PY, str(TRACK), *COMMON, "--device", args.device, "--F", FLOW, "--seed", str(seed),
                   "--out", str(out), "--save-fields", str(fdir), "--init-spots", f"{RADIUS:g}:{sep:g}"]
            t0 = time.time()
            p = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=8000)
            dt = round(time.time() - t0, 1)
            status = "ok" if p.returncode == 0 else "failed"
            index["runs"].append({"gap": gap, "seed": seed, "status": status, "seconds": dt,
                                  "dumps": len(list(fdir.glob("*.npy"))),
                                  **({"tail": (p.stderr or p.stdout or "")[-300:]} if status == "failed" else {})})
            print(f"[x174] {tag}: {status} {dt}")
    if args.write:
        (L1 / "x174_series_index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1) + "\n",
                                                   encoding="utf-8")
        print("[x174] index written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
