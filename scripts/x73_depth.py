"""x73_depth.py — how deep is the size memory? Ancestor–descendant correlation over genealogical distance.

Re-analysis of genealogies already in git (`x72c_pattern_s171-180.json`, replicated on `x70r_pattern_s171-175.json`). For each
uid with a recorded peak area, the ancestor at lag k is reached by following `uid_pairs` upward k times; the statistic is
Spearman(ancestor peak, descendant peak).

Controls at every lag: a **stranger** (nearest structure at the descendant's birth that is not an ancestor of any order) and a
**cross-lineage shuffle** (each descendant paired with a lag-k ancestor from a different lineage in the same world, 2000 draws).

Criteria: `reports/2026-11-02-x73-depth-plan.md`.

Run:
    python scripts/x73_depth.py --write
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
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x73_depth.json"

sys.path.insert(0, str(ROOT / "scripts"))
from x72c_analyse import spearman  # noqa: E402

GRID = 96
LAGS = (1, 2, 3)
SHUFFLE = 2000


def build(path: Path) -> dict:
    d = json.loads(path.read_text(encoding="utf-8"))
    peaks = {int(u["uid"]): int(u["peak"]) for u in (d.get("uid_outcomes") or []) if u.get("peak")}
    first = {int(u["uid"]): int(u["first"]) for u in (d.get("uid_outcomes") or []) if u.get("first") is not None}
    parent = {}
    for p, c in (d.get("uid_pairs") or []):
        parent.setdefault(int(c), int(p))
    snaps = []
    for s in d.get("series") or []:
        log = [c for c in (s.get("components_log") or []) if c.get("cx") is not None]
        snaps.append((int(s["step"]), log))
    snaps.sort()
    return {"peaks": peaks, "first": first, "parent": parent, "snaps": snaps}


def ancestors(uid: int, parent: dict[int, int], k: int) -> int | None:
    cur = uid
    for _ in range(k):
        cur = parent.get(cur)
        if cur is None:
            return None
    return cur


def stranger_peak(world: dict, uid: int) -> int | None:
    """Nearest structure at the uid's first appearance that is not an ancestor of any order."""
    t0 = world["first"].get(uid)
    if t0 is None:
        return None
    chain = set()
    cur = uid
    while cur is not None:
        chain.add(cur)
        cur = world["parent"].get(cur)
    nxt = [(t, log) for t, log in world["snaps"] if t >= t0 and any(int(c["uid"]) == uid for c in log)]
    if not nxt:
        return None
    _, log_child = nxt[0]
    pos = next((c for c in log_child if int(c["uid"]) == uid), None)
    if pos is None:
        return None
    best = None
    for c in log_child:
        other = int(c["uid"])
        if other in chain or other not in world["peaks"]:
            continue
        dx = min(abs(c["cx"] - pos["cx"]), GRID - abs(c["cx"] - pos["cx"]))
        dy = min(abs(c["cy"] - pos["cy"]), GRID - abs(c["cy"] - pos["cy"]))
        dxy = math.hypot(dx, dy)
        if best is None or dxy < best[0]:
            best = (dxy, world["peaks"][other])
    return best[1] if best else None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X73 depth of size memory")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    rng = random.Random(73)

    res = {"kind": "l1_field_x73_depth", "experiment": "X73",
           "command": "python scripts/x73_depth.py --write",
           "prereg": "reports/2026-11-02-x73-depth-plan.md",
           "lags": list(LAGS), "datasets": {}}

    for name, pattern in (("x72c", "x72c_pattern_s*.json"), ("x70r", "x70r_pattern_s*.json")):
        per_lag = {k: {"pairs": [], "stranger": [], "worlds": {}} for k in LAGS}
        for path in sorted(L1.glob(pattern)):
            w = build(path)
            seed = path.stem.split("_s")[-1]
            for k in LAGS:
                pairs, strangers = [], []
                for uid in w["peaks"]:
                    anc = ancestors(uid, w["parent"], k)
                    if anc is None or anc not in w["peaks"]:
                        continue
                    pairs.append((w["peaks"][anc], w["peaks"][uid]))
                    if k == 1:
                        sp = stranger_peak(w, uid)
                        if sp is not None:
                            strangers.append((sp, w["peaks"][uid]))
                per_lag[k]["pairs"].extend(pairs)
                per_lag[k]["stranger"].extend(strangers)
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
            row = {"pairs": len(pairs),
                   "rho": round(rho, 3) if rho is not None else None,
                   "shuffle_p95": round(draws[int(0.95 * len(draws)) - 1], 3) if draws else None,
                   "worlds": per_lag[k]["worlds"]}
            if k == 1 and per_lag[k]["stranger"]:
                sp = per_lag[k]["stranger"]
                s = spearman([a for a, _ in sp], [b for _, b in sp])
                row["stranger_pairs"] = len(sp)
                row["stranger_rho"] = round(s, 3) if s is not None else None
            out[k] = row
        res["datasets"][name] = out

    d = res["datasets"]["x72c"]
    l1, l2 = d[1], d[2]
    lag1_ok = (l1["rho"] or 0) >= 0.30
    surrogate_ok = (l1.get("stranger_rho") or 0) <= 0.15
    worlds_higher = sum(1 for s, row in (l2["worlds"] or {}).items()
                        if (row["rho"] or 0) >= 0.15)
    if (l2["pairs"] or 0) < 100 or not lag1_ok or not surrogate_ok:
        verdict = "void: the genealogy check or the lag-1 control failed"
    elif (l2["rho"] or 0) >= 0.15 and worlds_higher >= 7 and (l2["rho"] or 0) > (l2["shuffle_p95"] or 0):
        verdict = "depth >= 2: the memory survives a second generation"
    elif (l2["rho"] or 0) < 0.10 and sum(1 for row in (l2["worlds"] or {}).values() if (row["rho"] or 0) < 0.10) >= 7:
        verdict = "depth 1 only: the medium resets in one generation"
    else:
        verdict = "inconclusive"
    res["verdict"] = verdict
    res["lag1_ok"] = lag1_ok
    res["surrogate_ok"] = surrogate_ok
    res["worlds_lag2_ge_015"] = worlds_higher

    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[x73] written: {OUT.name}")

    for name, out in res["datasets"].items():
        print(f"  {name}:")
        for k in LAGS:
            row = out[k]
            extra = f" stranger={row.get('stranger_rho')} (n={row.get('stranger_pairs')})" if k == 1 else ""
            print(f"    lag {k}: pairs={row['pairs']:4d} rho={row['rho']} shuffle_p95={row['shuffle_p95']}{extra}")
    print("  verdict:", verdict, "| worlds lag2>=0.15:", worlds_higher, "/10")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
