"""x171_corridor_sizes.py — X171: the corridor at contact at three body sizes, reference rate.

Radius 4.5 at surface gap 10 (SEP = 2R + gap = 19) and radius 6 at surface gap 9 (SEP = 21), fifteen seeds each, F = 0.030;
the radius-3 arm is X170's (gap 10, SEP 16).
Pre-registration: reports/2026-11-04-x171-corridor-sizes-plan.md.
Run: python scripts/x171_corridor_sizes.py --write
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
FIELDS = ROOT / "_hourly" / "x171_fields"
FLOW = "0.030"
SEEDS = tuple(range(971, 986))
ARMS = ((4.5, 10), (6.0, 9))
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
    index = {"kind": "x171_corridor_sizes", "flow": FLOW, "seeds": list(SEEDS),
             "arms": [{"radius": r, "gap": g, "sep": 2 * r + g} for r, g in ARMS], "steps": STEPS, "runs": []}
    for radius, gap in ARMS:
        sep = 2 * radius + gap
        for seed in SEEDS:
            tag = f"r{radius:g}_g{gap}_s{seed}"
            out = L1 / f"x171_{tag}.json"
            fdir = FIELDS / tag
            if out.exists() and out.stat().st_size > 0 and any(fdir.glob("*.npy")):
                index["runs"].append({"radius": radius, "gap": gap, "seed": seed, "status": "skipped (exists)"})
                continue
            fdir.mkdir(parents=True, exist_ok=True)
            cmd = [PY, str(TRACK), *COMMON, "--device", args.device, "--F", FLOW, "--seed", str(seed),
                   "--out", str(out), "--save-fields", str(fdir), "--init-spots", f"{radius:g}:{sep:g}"]
            t0 = time.time()
            p = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=8000)
            dt = round(time.time() - t0, 1)
            status = "ok" if p.returncode == 0 else "failed"
            index["runs"].append({"radius": radius, "gap": gap, "seed": seed, "status": status, "seconds": dt,
                                  "dumps": len(list(fdir.glob("*.npy"))),
                                  **({"tail": (p.stderr or p.stdout or "")[-300:]} if status == "failed" else {})})
            print(f"[x171] {tag}: {status} {dt}")
    if args.write:
        (L1 / "x171_series_index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1) + "\n",
                                                   encoding="utf-8")
        print("[x171] index written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
