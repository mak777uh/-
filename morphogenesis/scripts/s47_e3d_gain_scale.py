"""Run the E3c niche experiment across a scale of niche_gain and report the sweet spot.

Why: s46 (niche_gain 0.02) gave no difference at all (all three arms within 0.006) because the
niche added 0.0016/step against 0.16 eaten - a hundred times too weak. s45 (niche_gain 40)
saturated the grid. The window between "invisible" and "flooded" is wide, so it must be
MEASURED rather than guessed.

This driver calls the validated s46 script once per gain level and prints, for each level:
  - the arithmetic (contribution vs cap),
  - the three arms' favourable share,
  - the closed-minus-open gap (the actual effect of the feedback),
  - how many runs saturated.

A level is USABLE when: contribution <= cap (guard passes), no run saturates, and the gap is
larger than the spread between seeds.
"""
from __future__ import annotations
import argparse
import json
import os
import subprocess
import sys

_MORPH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(_MORPH, "scripts", "s46_e3c_niche_correct.py")
OUTDIR = os.path.join(_MORPH, "experiments", "E09_pond")


def run_level(gain, seeds, steps, extra):
    out = os.path.join(OUTDIR, f"_e3c_gain{gain}.json")
    cmd = [sys.executable, SCRIPT, "--seeds", *[str(s) for s in seeds], "--steps", str(steps),
           "--niche-gain", str(gain), "--out", out, *extra]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", cwd=_MORPH)
    if proc.returncode != 0:
        return None, (proc.stdout or "") + (proc.stderr or "")
    with open(out, encoding="utf-8") as fh:
        return json.load(fh), ""


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--gains", type=float, nargs="+", default=[0.05, 0.1, 0.2, 0.5, 1.0])
    ap.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3])
    ap.add_argument("--steps", type=int, default=600)
    ap.add_argument("--out", required=True)
    args, extra = ap.parse_known_args(argv)

    results = []
    print("gain | contribution/cap | closed | open | frozen | gap | saturated")
    for g in args.gains:
        data, err = run_level(g, args.seeds, args.steps, extra)
        if data is None:
            print(f"{g:4} | REFUSED by the arithmetic guard")
            continue
        rows = data["rows"]
        def mean(arm):
            v = [r["overall"] for r in rows if r["arm"] == arm and r["overall"] is not None]
            return sum(v) / len(v) if v else None
        c, o, f = mean("closed"), mean("open"), mean("frozen")
        sat = sum(r["saturated"] for r in rows)
        ar = data["arithmetic"]
        gap = round(c - o, 4) if (c is not None and o is not None) else None
        print(f"{g:4} | {ar['contribution']:.4f}/{ar['cap']:.4f} | {c:.3f} | {o:.3f} | {f:.3f} "
              f"| {gap:+.4f} | {sat}/{len(rows)}")
        results.append({"gain": g, "arithmetic": ar, "closed": c, "open": o, "frozen": f,
                        "gap": gap, "saturated": sat, "rows": rows})
        try:
            os.remove(os.path.join(OUTDIR, f"_e3c_gain{g}.json"))
        except OSError:
            pass

    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump({"kind": "s47_e3d_gain_scale", "steps": args.steps,
                   "seeds": args.seeds, "levels": results}, fh, ensure_ascii=False, indent=1)
    print(f"\nwritten {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
