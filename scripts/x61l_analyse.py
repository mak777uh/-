"""x61l_analyse.py — four snapshots of a longer world: does the concentration grow?

Applies the preregistered criterion of `reports/2026-11-01-x61-long-horizon-plan.md`:

    selection  => peak share rises monotonically, passes 0.5 at 24 000, entropy falls below 1.8
    drift      => peak share stays in 0.35-0.45 without a monotone rise, entropy stays >= 1.9

The first snapshot (6000) is also the anchor's endpoint, so the four points are internally consistent by construction.

Run:
    python scripts/x61l_analyse.py --write
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import os
import statistics as st
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
FIELDS = L1 / "x61l_fields"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x61l_horizon.json"

STEPS = (6000, 12000, 18000, 24000)
SEEDS = range(171, 176)


def spectrum(t: int) -> dict | None:
    ps = []
    for seed in SEEDS:
        f = FIELDS / f"x61l_a50_s{seed}_t{t}.npy"
        if not f.exists():
            continue
        v = np.load(f).astype(np.float64)
        ps.append(np.abs(np.fft.fft2(v - v.mean())) ** 2)
    if not ps:
        return None
    p = np.mean(ps, axis=0)
    n = p.shape[0]
    k = np.fft.fftfreq(n) * n
    ky, kx = np.meshgrid(k, k, indexing="ij")
    r = np.round(np.sqrt(ky ** 2 + kx ** 2)).astype(int)
    prof = {rad: float(p[r == rad].mean()) for rad in range(1, 13) if (r == rad).any()}
    tot = sum(prof.values()) or 1.0
    shares = {rad: v / tot for rad, v in prof.items()}
    q = max(shares, key=shares.get)
    ent = -sum(x * math.log(x) for x in shares.values() if x > 0)
    return {"t": t, "n_seeds": len(ps), "q_peak": q, "peak_share": round(shares[q], 3),
            "entropy": round(ent, 3), "entropy_max_ln12": round(math.log(12), 3)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X61-long analysis")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    runs = {}
    for f in sorted(glob.glob(str(L1 / "x61l_a50_s*.json"))):
        seed = int(os.path.basename(f).rsplit("_s", 1)[1].split(".")[0])
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        sel = d.get("selection") or {}
        runs[seed] = {"splits": sel.get("splits"), "components": (d.get("heterogeneity") or {}).get("components_last"),
                      "s_mean_last": sel.get("s_mean_last")}
    if not runs:
        print("[x61l] нет прогонов")
        return 0

    spec = [s for s in (spectrum(t) for t in STEPS) if s]
    shares = [s["peak_share"] for s in spec]
    ents = [s["entropy"] for s in spec]
    monotone = all(b >= a for a, b in zip(shares, shares[1:])) if len(shares) >= 3 else None
    selection = bool(monotone and shares and shares[-1] > 0.5 and ents and ents[-1] < 1.8)
    drift = bool(shares and 0.35 <= shares[-1] <= 0.45 and ents and ents[-1] >= 1.9 and not monotone)

    out = {
        "kind": "l1_field_x61l_horizon",
        "experiment": "X61-long",
        "command": "python scripts/x61l_analyse.py --write",
        "prereg": "reports/2026-11-01-x61-long-horizon-plan.md",
        "spectra": spec,
        "trend": {"peak_shares": shares, "entropies": ents, "monotone_rise": monotone},
        "verdict": "selection" if selection else ("drift" if drift else "neither"),
        "runs": {str(k): v for k, v in runs.items()},
        "not_claimed": [
            "five seeds, seed-averaged spectra, no p-values",
            "the four points come from one continued run per seed, so they are not independent samples",
        ],
    }
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[x61l] written: {OUT.name}")
    for s in spec:
        print("  t=%5d  q=%2d  share=%.3f  H=%.2f/%.2f" % (s["t"], s["q_peak"], s["peak_share"], s["entropy"], s["entropy_max_ln12"]))
    print("  monotone rise:", monotone, "| verdict:", out["verdict"])
    if runs:
        print("  splits=%s components=%s s_end=%s" % (
            st.median([r["splits"] for r in runs.values() if r["splits"] is not None]),
            st.median([r["components"] for r in runs.values() if r["components"] is not None]),
            round(st.median([r["s_mean_last"] for r in runs.values() if r["s_mean_last"] is not None]), 3)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
