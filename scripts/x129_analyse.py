"""x129_analyse.py — X129: is the kin advantage only geometry? Who lives next door at the same distance.

X128b's absorptions, the same local budget and partner rule, plus the distance between the dead component's centroid and the absorber's, normalised by the two
radii (delta = d / (r_dead + r_absorber)). The decisive number is the kin share inside the contact band delta <= 1.5: if it is the same in the lattice and in the
percolating body, the family world is geometry; if it differs, the habitat chooses the neighbours.

Plan: reports/2026-11-03-x129-geometry-plan.md.

    python scripts/x129_analyse.py --write
"""
from __future__ import annotations

import argparse
import json
import math
import random
import statistics as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from field_metrics import cell_files  # noqa: E402
from x97_analyse import spearman  # noqa: E402
from x102_analyse import world_data  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x129_geometry.json"

CELLS = [
    {"tag": "f030", "flow": 0.030, "series": ("x108",), "partners": 290},
    {"tag": "f035", "flow": 0.035, "series": ("x126",), "partners": 403},
    {"tag": "f040", "flow": 0.040, "series": ("x108",), "partners": 531},
]
KNOWN_SURVIVAL = {0.030: 0.2496, 0.035: 0.2984, 0.040: 0.1372}
KNOWN_PAIRS = {0.030: 1142, 0.035: 1106, 0.040: 1195}
ABSORBED_AT = 0.50
VANISHED_AT = 0.10
PARTNER_SHARE = 0.50
REACH = 2.0
BAND = 1.5
HEREDITY_FLOOR = 0.35
TOL_SURVIVAL = 0.01
MIN_BAND = 100
RESOLUTION = 0.10
BOOTSTRAP = 2000
KIN = ("sibling", "aunt", "cousin", "distant")


def boot(vals, seed):
    if len(vals) < 5:
        return None
    rng = random.Random(seed)
    means = sorted(st.mean(rng.choice(vals) for _ in range(len(vals))) for _ in range(BOOTSTRAP))
    lo = max(0, min(len(means) - 1, int(0.025 * BOOTSTRAP)))
    hi = max(0, min(len(means) - 1, int(0.975 * BOOTSTRAP) - 1))
    return [round(means[lo], 4), round(means[hi], 4)]


def descendants(kids, uid):
    out, stack = [], [uid]
    while stack:
        node = stack.pop()
        out.append(node)
        stack.extend(kids.get(node, []))
    return out


def chain(parent, uid, depth=3):
    out = [uid]
    for _ in range(depth):
        p = parent.get(out[-1])
        if p is None or p in out:
            break
        out.append(p)
    return out


def kin_class(parent, dead, absorber):
    a, b = chain(parent, dead), chain(parent, absorber)
    if len(a) >= 2 and len(b) >= 2 and a[1] == b[1]:
        return "sibling"
    if len(a) >= 2 and len(b) >= 2 and (a[1] in b[1:] or b[1] in a[1:]):
        return "aunt"
    if len(a) >= 3 and len(b) >= 3 and a[2] == b[2]:
        return "cousin"
    if set(a[1:]) & set(b[1:]):
        return "distant"
    return "unrelated"


def cell_stats(flow: float, series, seed: int) -> dict:
    records = []          # (delta, kin_class, absorber_area, dead_area)
    heredity = []
    surv_diff = []
    pair_count = 0
    for path in cell_files(series, flow, filename=""):
        w = world_data(path)
        parent = {int(c): int(p) for c, p in w["parent"].items()}
        kids: dict[int, list[int]] = {}
        for child, par in parent.items():
            kids.setdefault(par, []).append(child)
        steps = sorted(int(s) for s in w["per_step"])
        for i in range(len(steps) - 1):
            t, t1 = steps[i], steps[i + 1]
            cur = {int(c["uid"]): c for c in (w["per_step"].get(t) or [])}
            nxt = {int(c["uid"]): c for c in (w["per_step"].get(t1) or [])}
            if not cur or not nxt:
                continue
            survivors = set(cur) & set(nxt)
            for uid, comp in cur.items():
                if uid in nxt or kids.get(uid):
                    continue
                dead_area = float(comp["area"]) or 1.0
                cx, cy = float(comp.get("cx", 0)), float(comp.get("cy", 0))
                rad = math.sqrt(dead_area / math.pi)
                near = [u for u in survivors
                        if math.hypot(float(nxt[u].get("cx", 0)) - cx, float(nxt[u].get("cy", 0)) - cy)
                        <= rad + math.sqrt(float(nxt[u]["area"]) / math.pi) + REACH]
                if not near:
                    continue
                local_growth = sum(float(nxt[u]["area"]) - float(cur[u]["area"]) for u in near)
                if local_growth / dead_area < ABSORBED_AT:
                    continue
                gains = {u: float(nxt[u]["area"]) - float(cur[u]["area"]) for u in near}
                positive = {u: g for u, g in gains.items() if g > 1e-9}
                total_pos = sum(positive.values())
                if not positive or total_pos <= 0:
                    continue
                absorber = max(positive, key=positive.get)
                if positive[absorber] / total_pos < PARTNER_SHARE:
                    continue
                o = nxt[absorber]
                d = math.hypot(float(o.get("cx", 0)) - cx, float(o.get("cy", 0)) - cy)
                r_abs = math.sqrt(float(o["area"]) / math.pi)
                delta = d / (rad + r_abs) if (rad + r_abs) > 0 else None
                if delta is None:
                    continue
                records.append((delta, kin_class(parent, uid, absorber), float(o["area"]), dead_area))

        last_step = steps[-1] if steps else None
        present = {int(c["uid"]) for c in (w["per_step"].get(last_step) or [])} if last_step else set()
        memo = {}

        def sub(u: int) -> list[int]:
            if u not in memo:
                memo[u] = descendants(kids, u)
            return memo[u]

        for mother, daughters in kids.items():
            if mother in w["peak"]:
                for d in daughters:
                    if d in w["peak"]:
                        heredity.append((w["peak"][mother]["area"], w["peak"][d]["area"]))
            if len(daughters) < 2:
                continue
            for i in range(len(daughters)):
                for j in range(i + 1, len(daughters)):
                    a, b = daughters[i], daughters[j]
                    if a not in w["peak"] or b not in w["peak"]:
                        continue
                    big, small = (a, b) if w["peak"][a]["area"] >= w["peak"][b]["area"] else (b, a)
                    pair_count += 1
                    surv_diff.append(int(any(u in present for u in sub(big))) - int(any(u in present for u in sub(small))))

    kin_rec = [r for r in records if r[1] in KIN]
    str_rec = [r for r in records if r[1] == "unrelated"]
    band = [r for r in records if r[0] <= BAND]
    band_kin = [r for r in band if r[1] in KIN]
    out_band = [r for r in records if r[0] > BAND]
    out_band_kin = [r for r in out_band if r[1] in KIN]
    rho = spearman([p[0] for p in heredity], [p[1] for p in heredity]) if heredity else None
    return {
        "partnered": len(records),
        "median_delta": round(st.median([r[0] for r in records]), 3) if records else None,
        "median_delta_kin": round(st.median([r[0] for r in kin_rec]), 3) if kin_rec else None,
        "median_delta_stranger": round(st.median([r[0] for r in str_rec]), 3) if str_rec else None,
        "band": len(band),
        "band_share": round(len(band) / len(records), 4) if records else None,
        "band_kin_share": round(len(band_kin) / len(band), 4) if band else None,
        "band_kin_share_ci": boot([1.0] * len(band_kin) + [0.0] * (len(band) - len(band_kin)), seed) if band else None,
        "out_band_kin_share": round(len(out_band_kin) / len(out_band), 4) if out_band else None,
        "kin_share_all": round(len(kin_rec) / len(records), 4) if records else None,
        "median_absorber_area_kin": round(st.median([r[2] for r in kin_rec]), 1) if kin_rec else None,
        "median_absorber_area_stranger": round(st.median([r[2] for r in str_rec]), 1) if str_rec else None,
        "rho_heredity": round(rho, 3) if rho is not None else None,
        "pairs": pair_count,
        "survival_mean": round(st.mean(surv_diff), 4) if surv_diff else None,
        "refs": {"partners": None, "survival": KNOWN_SURVIVAL[flow], "pairs": KNOWN_PAIRS[flow]},
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X129 geometry of absorption")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    cells = {}
    for i, spec in enumerate(CELLS):
        c = cell_stats(spec["flow"], spec["series"], seed=1290 + 10 * i)
        c["refs"]["partners"] = spec["partners"]
        cells[spec["tag"]] = c

    bad = []
    for tag, c in cells.items():
        ref = c["refs"]
        if c["partnered"] != ref["partners"]:
            bad.append(f"{tag}: {c['partnered']} partners against X128b's {ref['partners']}")
        if c["median_delta_kin"] is not None and c["median_delta_stranger"] is not None \
                and tag == "f030" and not (c["median_delta_kin"] < c["median_delta_stranger"]):
            bad.append(f"{tag}: kin are not nearer than strangers (sanity of the distance measure)")
        if c["rho_heredity"] is None or c["rho_heredity"] < HEREDITY_FLOOR:
            bad.append(f"{tag}: heredity {c['rho_heredity']}")
        if c["survival_mean"] is None or abs(c["survival_mean"] - ref["survival"]) > TOL_SURVIVAL:
            bad.append(f"{tag}: end-survival {c['survival_mean']} misses X126's {ref['survival']}")
        if c["pairs"] != ref["pairs"]:
            bad.append(f"{tag}: {c['pairs']} pairs against X126's {ref['pairs']}")
        if c["band"] < MIN_BAND:
            bad.append(f"{tag}: only {c['band']} partnered absorptions inside the band")

    lat, mid, maz = cells["f030"], cells["f035"], cells["f040"]
    diff = abs((lat["band_kin_share"] or 0) - (maz["band_kin_share"] or 0))
    if bad:
        verdict = "void: " + "; ".join(bad)
    elif diff < RESOLUTION:
        verdict = (f"geometry explains it: at the same contact distance the absorber is kin in {lat['band_kin_share']:.1%} of "
                   f"{lat['band']} absorptions in the lattice and {maz['band_kin_share']:.1%} of {maz['band']} in the maze — the same "
                   f"proportion within the declared {RESOLUTION:.2f}, so absorption goes to whoever is adjacent and the lattice's adjacency "
                   f"is kin by construction (median distance {lat['median_delta_kin']} radii for kin against "
                   f"{lat['median_delta_stranger']} for strangers)")
    else:
        verdict = (f"who lives next door: at the same contact distance the absorber is kin in {lat['band_kin_share']:.1%} (CI "
                   f"{lat['band_kin_share_ci']}) of {lat['band']} absorptions in the lattice against {maz['band_kin_share']:.1%} (CI "
                   f"{maz['band_kin_share_ci']}) of {maz['band']} in the maze, a difference of {diff:.1%} — the habitat decides who is "
                   f"adjacent, so kinship is a property of the world and not of the split rule alone; the middle cell sits at "
                   f"{mid['band_kin_share']:.1%} of {mid['band']}")

    res = {
        "kind": "l1_field_x129_geometry",
        "experiment": "X129",
        "command": "python scripts/x129_analyse.py --write",
        "prereg": "reports/2026-11-03-x129-geometry-plan.md",
        "definitions": {
            "delta": "centroid distance between the dead component and the absorber, divided by the sum of their radii sqrt(area/pi)",
            "band": f"partnered absorptions with delta <= {BAND} (physical contact)",
            "kin": "sibling, aunt, cousin or distant within three generations; everything else is a stranger",
        },
        "cells": cells,
        "band_kin_share_difference_lattice_vs_maze": round(diff, 4),
        "verdict": verdict,
    }
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[x129] written: {OUT.name}")
    for tag, c in cells.items():
        print(f"  {tag}: partnered={c['partnered']} band={c['band']} ({c['band_share']}) band_kin={c['band_kin_share']} "
              f"{c['band_kin_share_ci']} out_band_kin={c['out_band_kin_share']} delta_kin={c['median_delta_kin']} "
              f"delta_str={c['median_delta_stranger']} area_kin={c['median_absorber_area_kin']} "
              f"area_str={c['median_absorber_area_stranger']} heredity={c['rho_heredity']} pairs={c['pairs']} surv={c['survival_mean']}")
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
