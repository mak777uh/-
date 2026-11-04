"""x178_cliff.py — X178: radius 6 at surface gap 9, F = 0.030 — thirty seeds on the cell that decides plateau or cliff.

Thirty seeds (1121-1150), 2 000 steps, field dumps every ten steps. Registered: share 0.05-0.55.
Pre-registration: reports/2026-11-04-x178-cliff-plan.md.
Run: python scripts/x178_cliff.py --write
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
FIELDS = ROOT / "_hourly" / "x178_fields"
RADIUS = 6.0
GAP = 9
FLOW = "0.030"
SEEDS = tuple(range(1121, 1151))
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
    index = {"kind": "x178_cliff", "flow": FLOW, "radius": RADIUS, "gap": GAP, "steps": STEPS,
             "seeds": list(SEEDS), "predictions": {"share": [0.05, 0.55]}, "runs": []}
    sep = 2 * RADIUS + GAP
    for seed in SEEDS:
        tag = f"s{seed}"
        out = L1 / f"x178_{tag}.json"
        fdir = FIELDS / tag
        if out.exists() and out.stat().st_size > 0 and any(fdir.glob("*.npy")):
            index["runs"].append({"seed": seed, "status": "skipped (exists)"})
            continue
        fdir.mkdir(parents=True, exist_ok=True)
        cmd = [PY, str(TRACK), *COMMON, "--device", args.device, "--F", FLOW, "--seed", str(seed),
               "--out", str(out), "--save-fields", str(fdir), "--init-spots", f"{RADIUS:g}:{sep:g}"]
        t0 = time.time()
        p = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=8000)
        dt = round(time.time() - t0, 1)
        status = "ok" if p.returncode == 0 else "failed"
        index["runs"].append({"seed": seed, "status": status, "seconds": dt, "dumps": len(list(fdir.glob("*.npy"))),
                              **({"tail": (p.stderr or p.stdout or "")[-300:]} if status == "failed" else {})})
        print(f"[x178] {tag}: {status} {dt}")
    if args.write:
        (L1 / "x178_series_index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1) + "\n",
                                                   encoding="utf-8")
        print("[x178] index written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
