"""x168d_series.py — X168d: ten seeds at gap 11 (and a gap-8 control) at three inflow rates.

Surface gaps, so SEP = 2R + gap: gap 8 -> 14, gap 11 -> 17.
Pre-registration: reports/2026-11-04-x168d-gap11-plan.md.
Run: python scripts/x168d_series.py --write
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
RADIUS = 3.0
FLOWS = ("0.026", "0.030", "0.036")
GAPS = (8, 11)
SEEDS = tuple(range(961, 971))
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


def sep_for(gap: float) -> float:
    return 2.0 * RADIUS + float(gap)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    index = {"kind": "x168d_series", "radius": RADIUS, "flows": list(FLOWS), "gaps": list(GAPS),
             "seeds": list(SEEDS), "steps": STEPS, "conversion": "surface gap g -> SEP = 2R + g", "runs": []}
    for flow in FLOWS:
        for gap in GAPS:
            for seed in SEEDS:
                out = L1 / f"x168d_F{int(float(flow) * 1000)}_g{gap}_s{seed}.json"
                if out.exists() and out.stat().st_size > 0:
                    index["runs"].append({"flow": flow, "gap": gap, "seed": seed, "status": "skipped (exists)"})
                    continue
                cmd = [PY, str(TRACK), *COMMON, "--device", args.device, "--F", flow, "--seed", str(seed),
                       "--out", str(out), "--init-spots", f"{RADIUS}:{sep_for(gap):g}"]
                t0 = time.time()
                p = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True,
                                   encoding="utf-8", errors="replace", timeout=5000)
                dt = round(time.time() - t0, 1)
                status = "ok" if p.returncode == 0 else "failed"
                index["runs"].append({"flow": flow, "gap": gap, "seed": seed, "sep": sep_for(gap), "status": status,
                                      "seconds": dt,
                                      **({"tail": (p.stderr or p.stdout or "")[-300:]} if status == "failed" else {})})
                print(f"[x168d] F{flow} g{gap} s{seed}: {status} {dt}")
    if args.write:
        (L1 / "x168d_series_index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1) + "\n",
                                                   encoding="utf-8")
        print("[x168d] index written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
