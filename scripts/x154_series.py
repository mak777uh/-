"""x154_series.py — X154: the mixing curve at radius 6, ten seeds per arm.

    gap 6.5  separation 18.5  seeds 601-610  (ten new runs)
    gap 7.0  separation 19.0  seeds 606-610  (five new runs; 601-605 exist in X150)
    gap 8.0  separation 20.0  seeds 606-610  (five new runs; 601-605 exist in X150)

Gap 7.5 is reused whole from X153 (ten seeds).

    python scripts/x154_series.py [--arm g65|g70|g80]
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

RADIUS = 6.0
FLOW = "0.030"

ARMS = {
    "g65": {"name": "x154_g65_r60", "sep": 18.5, "gap": 6.5, "seeds": tuple(range(601, 611))},
    "g70": {"name": "x154_g70_r60", "sep": 19.0, "gap": 7.0, "seeds": tuple(range(606, 611))},
    "g80": {"name": "x154_g80_r60", "sep": 20.0, "gap": 8.0, "seeds": tuple(range(606, 611))},
}

COMMON = [
    "--steps", "6000", "--grid", "96", "--dt", "1.0", "--device", "cuda",
    "--Du", "0.16", "--Dv", "0.08", "--k", "0.06", "--eps", "0.0",
    "--hetero-scale", "12.0", "--hetero-period", "0.0", "--hetero-amp", "0.5",
    "--hetero-signal", "lab/streams/const_ones.json",
    "--sample-every", "10", "--threshold", "0.2",
    "--freq-dep", "0.0", "--bin-width", "0.2", "--beta", "0.0", "--s-ref", "1.0", "--mutation", "0.15",
    "--overlap", "0.5", "--split-new-uid", "--init-jitter",
]


def run_one(arm: dict, seed: int, out: Path) -> dict:
    if out.exists() and out.stat().st_size > 0:
        return {"seed": seed, "status": "skipped (exists)"}
    cmd = [PY, str(TRACK), *COMMON, "--F", FLOW, "--seed", str(seed), "--out", str(out),
           "--init-spots", f"{RADIUS}:{arm['sep']}"]
    last = {"seed": seed, "status": "failed"}
    for attempt in (1, 2):
        t0 = time.time()
        try:
            proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True,
                                  encoding="utf-8", errors="replace", timeout=4000)
        except subprocess.TimeoutExpired:
            last = {"seed": seed, "status": "timeout", "attempt": attempt}
            continue
        dt = time.time() - t0
        if proc.returncode != 0:
            last = {"seed": seed, "status": "failed", "attempt": attempt, "seconds": round(dt, 1),
                    "tail": (proc.stderr or proc.stdout or "")[-300:]}
            continue
        return {"seed": seed, "status": "ok", "seconds": round(dt, 1)}
    return last


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X154 mixing curve")
    ap.add_argument("--arm", default="", help="g65, g70 or g80 (default: all)")
    args = ap.parse_args(argv)
    keys = [args.arm] if args.arm else list(ARMS)
    index = L1 / "x154_series_index.json"
    rows = []
    for key in keys:
        arm = ARMS[key]
        for seed in arm["seeds"]:
            out = L1 / f"{arm['name']}_s{seed}.json"
            r = run_one(arm, seed, out)
            r.update({"arm": key, "gap": arm["gap"], "sep": arm["sep"]})
            rows.append(r)
            print(f"[x154] {key} gap {arm['gap']} seed {seed}: {r['status']} {r.get('seconds', '')} "
                  f"{r.get('tail', '')}", flush=True)
            index.write_text(json.dumps({"kind": "x154_series_index", "rows": rows},
                                        ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            if r["status"] in ("failed", "timeout"):
                return 1
    print(f"[x154] done: {len(rows)} runs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
