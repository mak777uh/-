"""X168c: the inflow test again, with the gap converted to a centre separation correctly.

The bug: `--init-spots R:SEP` takes the CENTRE separation, so a surface gap g needs SEP = 2R + g. X168 and X168b passed the
surface gap itself (3:11 meant centre 11, i.e. surface gap 5), so their "gap-11" arms were gap-5 arms and every one of them
fused, as a gap of 5 must.

Arms: F in (0.026, 0.030, 0.036) x surface gaps (8, 10, 11) x seeds 961-965, 2 000 steps, SEP computed correctly.
Plus the length control: F = 0.030 at surface gaps 10 and 11, seeds 961-965, 6 000 steps, so the 2 000-step arms can be
compared with the X158 baseline at the same length.
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
GAPS = (8, 10, 11)
SEEDS = (961, 962, 963, 964, 965)
STEPS = 2000
LENGTH_GAPS = (10, 11)
LENGTH_STEPS = 6000

COMMON = [
    "--grid", "96", "--dt", "1.0",
    "--Du", "0.16", "--Dv", "0.08", "--k", "0.06", "--eps", "0.0",
    "--hetero-scale", "12.0", "--hetero-period", "0.0", "--hetero-amp", "0.5",
    "--hetero-signal", "lab/streams/const_ones.json",
    "--sample-every", "10", "--threshold", "0.2",
    "--freq-dep", "0.0", "--bin-width", "0.2", "--beta", "0.0", "--s-ref", "1.0", "--mutation", "0.15",
    "--overlap", "0.5", "--split-new-uid", "--init-jitter",
]


def sep_for(gap: float) -> float:
    """Surface gap to centre separation - the conversion that X168 got wrong."""
    return 2.0 * RADIUS + float(gap)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--length-only", action="store_true")
    args = ap.parse_args(argv)
    index = {"kind": "x168c_series", "radius": RADIUS, "flows": list(FLOWS), "gaps": list(GAPS),
             "seeds": list(SEEDS), "steps": STEPS,
             "length_control": {"gaps": list(LENGTH_GAPS), "steps": LENGTH_STEPS,
                                "flows": ["0.030"]},
             "conversion": "surface gap g -> SEP = 2R + g", "runs": []}
    jobs = [] if args.length_only else [(f, g, s, STEPS) for f in FLOWS for g in GAPS for s in SEEDS]
    jobs += [("0.030", g, s, LENGTH_STEPS) for g in LENGTH_GAPS for s in SEEDS]
    for flow, gap, seed, steps in jobs:
        tag = "len" if steps == LENGTH_STEPS else f"g{gap}"
        out = L1 / f"x168c_F{int(float(flow) * 1000)}_{tag}_s{seed}.json"
        if out.exists() and out.stat().st_size > 0:
            index["runs"].append({"flow": flow, "gap": gap, "seed": seed, "steps": steps,
                                  "status": "skipped (exists)"})
            continue
        cmd = [PY, str(TRACK), *COMMON, "--steps", str(steps), "--device", args.device, "--F", flow,
               "--seed", str(seed), "--out", str(out), "--init-spots",
               f"{RADIUS}:{sep_for(gap):g}"]
        t0 = time.time()
        p = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=5000)
        dt = round(time.time() - t0, 1)
        status = "ok" if p.returncode == 0 else "failed"
        index["runs"].append({"flow": flow, "gap": gap, "seed": seed, "steps": steps, "sep": sep_for(gap),
                              "status": status, "seconds": dt,
                              **({"tail": (p.stderr or p.stdout or "")[-300:]} if status == "failed" else {})})
        print(f"[x168c] F{flow} g{gap} s{seed} ({steps} steps, sep {sep_for(gap):g}): {status} {dt}")
    if args.write:
        (L1 / "x168c_series_index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1) + "\n",
                                                    encoding="utf-8")
        print("[x168c] index written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
