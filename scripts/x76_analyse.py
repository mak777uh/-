"""x76_analyse.py — ten worlds at F = 0.033: sampling accident or a genuinely weak initial memory?

Same machinery as X73-X75, applied to the replicated cell. Reports pooled Spearman at lags 1–3, the per-world ρ₁ table (the part
that tells an average of different worlds from a property of the cell), the shuffle null, and the half-life.

Criteria: `reports/2026-11-02-x76-033-replication-plan.md`.

Run:
    python scripts/x76_analyse.py --write
"""
from __future__ import annotations

import argparse
import json
import math
import random
import statistics as st
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x76_033.json"

sys.path.insert(0, str(ROOT / "scripts"))
from x73_depth import ancestors, build  # noqa: E402
from x72c_analyse import spearman  # noqa: E402

LAGS = (1, 2, 3)
SHUFFLE = 2000
PATTERN = "x76_f033_pattern_s*.json"
BAND = (0.40, 0.60)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X76 replication of the 0.033 cell")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    rng = random.Random(76)

    per_lag = {k: {"pairs": [], "worlds": {}} for k in LAGS}
    for path in sorted(L1.glob(PATTERN)):
        w = build(path)
        seed = path.stem.split("_s")[-1]
        for k in LAGS:
            pairs = []
            for uid in w["peaks"]:
                anc = ancestors(uid, w["parent"], k)
                if anc is None or anc not in w["peaks"]:
                    continue
                pairs.append((w["peaks"][anc], w["peaks"][uid]))
            per_lag[k]["pairs"].extend(pairs)
            r = spearman([a for a, _ in pairs], [b for _, b in pairs])
            per_lag[k]["worlds"][seed] = {"pairs": len(pairs), "rho": round(r, 3) if r is not None else None}

    out = {}
    for k in LAGS:
        pairs = per_lag[k]["pairs"]
        rho = spearman([a for a, _ in pairs], [b for _, b in pairs])
        draws = []
        if pairs:
            anc = [a for a, _ in pairs]
            desc = [b for _, b in pairs]
            for _ in range(SHUFFLE):
                sh = anc[:]
                rng.shuffle(sh)
                v = spearman(sh, desc)
                if v is not None:
                    draws.append(v)
        draws.sort()
        out[k] = {"pairs": len(pairs), "rho": round(rho, 3) if rho is not None else None,
                  "shuffle_p95": round(draws[int(0.95 * len(draws)) - 1], 3) if draws else None,
                  "worlds": per_lag[k]["worlds"]}

    r1, r2, r3 = (out[k]["rho"] for k in LAGS)
    lam = half = None
    if r1 and r2 and r3 and r1 > 0:
        ratios = [x / y for x, y in ((r2, r1), (r3, r2)) if x > 0 and y > 0]
        if ratios:
            lam = math.exp(sum(math.log(x) for x in ratios) / len(ratios))
            half = math.log(0.5) / math.log(lam) if 0 < lam < 1 else None

    world_rhos = [w["rho"] for w in out[1]["worlds"].values() if w["rho"] is not None]
    above_045 = sum(1 for r in world_rhos if r > 0.45)
    res = {"kind": "l1_field_x76_033", "experiment": "X76",
           "command": "python scripts/x76_analyse.py --write",
           "prereg": "reports/2026-11-02-x76-033-replication-plan.md",
           "band": BAND, "lags": out,
           "lambda": round(lam, 3) if lam else None,
           "half_life": round(half, 2) if half else None,
           "worlds": len(world_rhos), "worlds_rho1_above_045": above_045,
           "world_rhos": sorted(round(r, 3) for r in world_rhos)}

    void = (out[2]["pairs"] < 400) or ((out[1]["shuffle_p95"] or 0) > 0.10)
    if void:
        verdict = "void: too few lag-2 pairs or the shuffle null is too strong"
    elif BAND[0] <= (r1 or 0) <= BAND[1]:
        verdict = "ordinary cell: pooled rho1 is inside the registered band, X75's void was sampling"
    elif (r1 or 0) < BAND[0] and above_045 < 2:
        verdict = "genuinely weak start: pooled rho1 below the band and no world reaches 0.45"
    else:
        verdict = "inconclusive"
    res["verdict"] = verdict

    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[x76] written: {OUT.name}")

    print(f"  pairs {out[1]['pairs']}/{out[2]['pairs']}/{out[3]['pairs']}  "
          f"rho {r1}/{r2}/{r3}  shuffle {out[1]['shuffle_p95']}  lambda={res['lambda']} half={res['half_life']}")
    print(f"  per-world rho1: {res['world_rhos']} (above 0.45: {above_045}/{len(world_rhos)})")
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
