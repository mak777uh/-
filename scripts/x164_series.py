"""x164_series.py — X164: does the fusion crossing depend on the size RATIO?

Asymmetric pairs (radius 3 and radius 6) at four surface gaps, plus the two symmetric controls of the block.
Pre-registration: reports/2026-11-04-x164-asymmetric-pairs-plan.md.

Run:
    python scripts/x164_series.py --write
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

# (label, r1, r2, surface gap)
ARMS = (
    ("asym_g4", 3.0, 6.0, 4),
    ("asym_g6", 3.0, 6.0, 6),
    ("asym_g8", 3.0, 6.0, 8),
    ("asym_g10", 3.0, 6.0, 10),
    ("sym_r3_g8", 3.0, 3.0, 8),
    ("sym_r6_g8", 6.0, 6.0, 8),
)
SEEDS = (931, 932, 933, 934, 935)
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


def name(label: str, seed: int) -> str:
    return f"x164_{label}_s{seed}"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--seeds", default="")
    ap.add_argument("--arms", default="")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    seeds = [int(s) for s in args.seeds.split(",") if s.strip()] or list(SEEDS)
    arms = ARMS
    if args.arms:
        wanted = set(a.strip() for a in args.arms.split(",") if a.strip())
        arms = [a for a in ARMS if a[0] in wanted]

    L1.mkdir(parents=True, exist_ok=True)
    index = {"kind": "x164_series", "steps": STEPS, "flow": FLOW, "seeds": seeds,
             "arms": [{"label": l, "r1": r1, "r2": r2, "gap": g, "sep": r1 + r2 + g} for l, r1, r2, g in arms],
             "runs": []}
    for label, r1, r2, gap in arms:
        sep = r1 + r2 + gap
        for seed in seeds:
            out = L1 / (name(label, seed) + ".json")
            if out.exists() and out.stat().st_size > 0:
                index["runs"].append({"arm": label, "seed": seed, "status": "skipped (exists)"})
                print(f"[x164] {name(label, seed)}: skipped")
                continue
            spots = f"{r1}:{sep}:{r2}"
            cmd = [PY, str(TRACK), *COMMON, "--device", args.device, "--F", FLOW, "--seed", str(seed),
                   "--out", str(out), "--init-spots", spots]
            t0 = time.time()
            p = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=5000)
            dt = round(time.time() - t0, 1)
            if p.returncode != 0:
                res = {"arm": label, "seed": seed, "status": "failed", "seconds": dt,
                       "tail": (p.stderr or p.stdout or "")[-300:]}
            else:
                res = {"arm": label, "seed": seed, "status": "ok", "seconds": dt}
            index["runs"].append(res)
            print(f"[x164] {name(label, seed)}: {res['status']} {dt}")
    if args.write:
        (L1 / "x164_series_index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1) + "\n",
                                                   encoding="utf-8")
        print("[x164] index written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
