"""x166_series.py — X166: the contact threshold at one-step resolution.

Five arms from the fusion block, re-run with `--sample-every 1` for 2 000 steps and five seeds each, so the gap at
which fusion becomes possible is read without the ten-step quantum that made the X157/X159 number an upper bound.

Arms (radius, nominal gap, centre separation):
    r3 g8 sep 14, r3 g9 sep 15, r4.5 g9 sep 18, r5.2 g7 sep ?, r6 g8 sep 20

Pre-registration: reports/2026-11-04-x166-one-step-threshold-plan.md.

Run:
    python scripts/x166_series.py --write
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

ARMS = (
    (3.0, 8, 14),
    (3.0, 9, 15),
    (4.5, 9, 18),
    (5.2, 7, 17),
    (6.0, 8, 20),
)
SEEDS = (911, 912, 913, 914, 915)
FLOW = "0.030"
STEPS = 2000

COMMON = [
    "--steps", str(STEPS), "--grid", "96", "--dt", "1.0",
    "--Du", "0.16", "--Dv", "0.08", "--k", "0.06", "--eps", "0.0",
    "--hetero-scale", "12.0", "--hetero-period", "0.0", "--hetero-amp", "0.5",
    "--hetero-signal", "lab/streams/const_ones.json",
    "--sample-every", "1", "--threshold", "0.2",
    "--freq-dep", "0.0", "--bin-width", "0.2", "--beta", "0.0", "--s-ref", "1.0", "--mutation", "0.15",
    "--overlap", "0.5", "--split-new-uid", "--init-jitter",
]


def name(radius: float, gap: int, seed: int) -> str:
    return f"x166_g{gap}_r{int(round(radius * 10))}_s{seed}"


def run_one(seed: int, radius: float, gap: int, sep: int, device: str) -> dict:
    out = L1 / (name(radius, gap, seed) + ".json")
    if out.exists() and out.stat().st_size > 0:
        return {"seed": seed, "radius": radius, "gap": gap, "status": "skipped (exists)"}
    cmd = [PY, str(TRACK), *COMMON, "--device", device, "--F", FLOW, "--seed", str(seed),
           "--out", str(out), "--init-spots", f"{radius}:{sep}"]
    t0 = time.time()
    proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=4000)
    dt = time.time() - t0
    if proc.returncode != 0:
        return {"seed": seed, "radius": radius, "gap": gap, "status": "failed",
                "seconds": round(dt, 1), "tail": (proc.stderr or proc.stdout or "")[-300:]}
    return {"seed": seed, "radius": radius, "gap": gap, "status": "ok", "seconds": round(dt, 1)}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--seeds", default="")
    ap.add_argument("--arms", default="", help="e.g. 3:8,4.5:9")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    seeds = [int(s) for s in args.seeds.split(",") if s.strip()] or list(SEEDS)
    arms = ARMS
    if args.arms:
        wanted = set()
        for part in args.arms.split(","):
            r, g = part.split(":")
            wanted.add((float(r), int(g)))
        arms = [a for a in ARMS if (a[0], a[1]) in wanted]

    L1.mkdir(parents=True, exist_ok=True)
    index = {"kind": "x166_series", "steps": STEPS, "flow": FLOW, "sample_every": 1,
             "seeds": seeds, "arms": [{"radius": r, "gap": g, "sep": s} for r, g, s in arms], "runs": []}
    for radius, gap, sep in arms:
        for seed in seeds:
            res = run_one(seed, radius, gap, sep, args.device)
            index["runs"].append(res)
            print(f"[x166] {name(radius, gap, seed)}: {res['status']} {res.get('seconds', '')}")
    if args.write:
        p = L1 / "x166_series_index.json"
        p.write_text(json.dumps(index, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"[x166] index: {p.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
