"""x72_analyse.py — at the multistable boundary, does a daughter take her parent's branch?

Reads the X70 replication worlds (`x70r_pattern_s*.json`, already in git, 50-step component log) and asks whether a
daughter's **branch** — wide spacing (>= 10.4 cells, X71's 12.0-cell branch) or narrow (< 10.4, the 8.73-cell branch) —
agrees with her parent's more often than with a non-parent structure at the same distance.

Criteria are in `reports/2026-11-01-x72-branch-heredity-plan.md`, committed before this script was written.

Run:
    python scripts/x72_analyse.py --write
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import random
import statistics as st
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x72_branch.json"
FIELDS = L1 / "_x70r_fields"

sys.path.insert(0, str(ROOT / "scripts"))
from x60_analyse import radial_profile  # noqa: E402

GRID = 96
BRANCH_SPLIT = 10.4      # cells; midpoint of X71's 12.0 and 8.73 branches, fixed in the preregistration
SHUFFLE_DRAWS = 2000
BAND = 0.15              # required parent-minus-surrogate concordance


def wrap_d(a, b, n=GRID):
    dx = min(abs(a[0] - b[0]), n - abs(a[0] - b[0]))
    dy = min(abs(a[1] - b[1]), n - abs(a[1] - b[1]))
    return math.hypot(dx, dy)


def snapshot_spacing(comps: list[dict]) -> dict[int, float]:
    """Nearest-neighbour centroid distance per uid: the local spacing, our proxy for the local wavelength."""
    out = {}
    for i, a in enumerate(comps):
        best = None
        for j, b in enumerate(comps):
            if i == j or a.get("cx") is None or b.get("cx") is None:
                continue
            d = wrap_d((a["cx"], a["cy"]), (b["cx"], b["cy"]))
            best = d if best is None else min(best, d)
        if best is not None:
            out[int(a["uid"])] = best
    return out


def branch(spacing: float | None) -> str | None:
    if spacing is None:
        return None
    return "wide" if spacing >= BRANCH_SPLIT else "narrow"


def events_for_world(path: Path) -> list[dict]:
    d = json.loads(path.read_text(encoding="utf-8"))
    peaks = {int(u["uid"]): int(u["peak"]) for u in (d.get("uid_outcomes") or []) if u.get("peak")}
    first = {int(u["uid"]): int(u["first"]) for u in (d.get("uid_outcomes") or []) if u.get("first") is not None}
    snaps = []
    for s in d.get("series") or []:
        comps = [c for c in (s.get("components_log") or []) if c.get("cx") is not None]
        snaps.append((int(s.get("step") or 0), comps, snapshot_spacing(comps)))
    snaps.sort()

    out = []
    for p_uid, c_uid in (d.get("uid_pairs") or []):
        p_uid, c_uid = int(p_uid), int(c_uid)
        if c_uid not in first:
            continue
        t_birth = first[c_uid]
        prev = [(t, m) for t, comps, m in snaps if t < t_birth and p_uid in m]
        nxt = [(t, comps, m) for t, comps, m in snaps if t >= t_birth and c_uid in m]
        if not prev or not nxt:
            continue
        t_prev, m_prev = prev[-1]
        t_child, comps_child, m_child = nxt[0]
        p_branch = branch(m_prev.get(p_uid))
        c_branch = branch(m_child.get(c_uid))
        if p_branch is None or c_branch is None:
            continue
        pos_c = next((c for c in comps_child if int(c["uid"]) == c_uid), None)
        if pos_c is None:
            continue
        cands = []
        for c in comps_child:
            uid = int(c["uid"])
            if uid in (p_uid, c_uid):
                continue
            b = branch(m_child.get(uid))
            if b is None:
                continue
            cands.append((wrap_d((pos_c["cx"], pos_c["cy"]), (c["cx"], c["cy"])), b))
        cands.sort()
        out.append({"parent": p_branch, "child": c_branch,
                    "surrogate": cands[0][1] if cands else None,
                    "spacing_parent": round(m_prev[p_uid], 2), "spacing_child": round(m_child[c_uid], 2),
                    "birth": t_birth, "gap_prev": t_birth - t_prev, "gap_next": t_child - t_birth})
    return out


def proxy_check(path: Path) -> dict:
    """Does the nearest-neighbour spacing track the wavelength at all?

    The branch variable is a class of local spacing, so it is only usable if spacing moves with the global peak position:
    X71's branches are 12.0 and 8.73 cells. If the spacing sits at the same value in both, the proxy measures component
    density instead of wavelength and every concordance number computed from it is meaningless. This check runs before the
    verdict is read, so a failed instrument cannot be mistaken for a biological null.
    """
    d = json.loads(path.read_text(encoding="utf-8"))
    tag = path.stem
    pts = []
    for s in d.get("series") or []:
        comps = [c for c in (s.get("components_log") or []) if c.get("cx") is not None]
        if len(comps) < 3:
            continue
        f = FIELDS / f"{tag}_t{int(s['step'])}.npy"
        if not f.is_file():
            continue
        sp = []
        for i, a in enumerate(comps):
            best = min((wrap_d((a["cx"], a["cy"]), (b["cx"], b["cy"]))
                        for j, b in enumerate(comps) if i != j), default=None)
            if best:
                sp.append(best)
        prof = radial_profile(np.load(f))
        if not prof:
            continue
        q = float(max(prof, key=prof.get))
        pts.append((st.median(sp), q))
    if len(pts) < 5:
        return {"points": len(pts), "corr": None, "spacing_sd": None, "usable": False}
    xs = [a for a, _ in pts]
    ys = [b for _, b in pts]
    mx, my = st.mean(xs), st.mean(ys)
    sx, sy = st.pstdev(xs), st.pstdev(ys)
    corr = (sum((a - mx) * (b - my) for a, b in pts) / len(pts) / (sx * sy)) if sx and sy else None
    return {"points": len(pts), "corr": round(corr, 3) if corr is not None else None,
            "spacing_median": round(st.median(xs), 2), "spacing_sd": round(sx, 2),
            "q_values": sorted({int(y) for y in ys}),
            "usable": bool(corr is not None and abs(corr) >= 0.5 and sx >= 1.0)}


def concordance(pairs: list[tuple[str, str]]) -> float | None:
    if not pairs:
        return None
    return sum(1 for a, b in pairs if a == b) / len(pairs)


def analyse(evs: list[dict], rng: random.Random) -> dict:
    par = [(e["parent"], e["child"]) for e in evs]
    sur = [(e["surrogate"], e["child"]) for e in evs if e["surrogate"]]
    obs = concordance(par)
    sur_c = concordance(sur)
    parents = [a for a, _ in par]
    childs = [b for _, b in par]
    draws = []
    for _ in range(SHUFFLE_DRAWS):
        sh = parents[:]
        rng.shuffle(sh)
        v = concordance(list(zip(sh, childs)))
        if v is not None:
            draws.append(v)
    draws.sort()
    share_wide = sum(1 for e in evs if e["parent"] == "wide") / len(evs) if evs else None
    return {
        "events": len(evs),
        "parent_wide_share": round(share_wide, 3) if share_wide is not None else None,
        "concordance_parent": round(obs, 3) if obs is not None else None,
        "concordance_surrogate": round(sur_c, 3) if sur_c is not None else None,
        "difference": round(obs - sur_c, 3) if (obs is not None and sur_c is not None) else None,
        "shuffle_p95": round(draws[int(0.95 * len(draws)) - 1], 3) if draws else None,
        "shuffle_median": round(st.median(draws), 3) if draws else None,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X72 branch concordance at the multistable boundary")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    rng = random.Random(72)

    res = {"kind": "l1_field_x72_branch", "experiment": "X72",
           "command": "python scripts/x72_analyse.py --write",
           "prereg": "reports/2026-11-01-x72-branch-heredity-plan.md",
           "branch_split_cells": BRANCH_SPLIT, "band": BAND, "arms": {}}

    for arm in ("pattern", "homog"):
        worlds = {}
        for f in sorted(L1.glob(f"x70r_{arm}_s*.json")):
            worlds[Path(f).stem.split("_s")[-1]] = analyse(events_for_world(Path(f)), rng)
        pooled_evs = [e for f in sorted(L1.glob(f"x70r_{arm}_s*.json")) for e in events_for_world(Path(f))]
        res["arms"][arm] = {"worlds": worlds, "pooled": analyse(pooled_evs, rng)}

    res["proxy_check"] = {Path(f).stem: proxy_check(Path(f)) for f in sorted(L1.glob("x70r_pattern_s*.json"))}
    usable = [v for v in res["proxy_check"].values() if v.get("usable")]

    pat = res["arms"]["pattern"]
    pooled = pat["pooled"]
    wide = pooled["parent_wide_share"]
    sensitive = (pooled["events"] > 0 and wide is not None and 0.25 <= wide <= 0.75)
    hits = [w for w in pat["worlds"].values() if (w["difference"] or 0) >= BAND]
    if len(usable) < 3:
        verdict = ("inconclusive: the nearest-neighbour spacing does not track the wavelength branch, so the branch "
                   "variable is not measurable from the component log alone (this is an instrument failure, not a null)")
    elif not sensitive:
        verdict = "insensitive: one branch holds nearly all events, the readout cannot separate them"
    elif (pooled["difference"] or 0) >= BAND and len(hits) >= 4 and pooled["concordance_parent"] > (pooled["shuffle_p95"] or 0):
        verdict = "supports branch heredity"
    elif (pooled["difference"] or 0) <= 0 or len(hits) < 2:
        verdict = "not supported"
    else:
        verdict = "inconclusive"
    res["verdict"] = verdict
    res["worlds_above_band"] = len(hits)

    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[x72] written: {OUT.name}")

    for arm in ("pattern", "homog"):
        a = res["arms"][arm]
        print(f"  {arm}: pooled events={a['pooled']['events']} wide_share={a['pooled']['parent_wide_share']} "
              f"parent={a['pooled']['concordance_parent']} surrogate={a['pooled']['concordance_surrogate']} "
              f"diff={a['pooled']['difference']} shuffle_p95={a['pooled']['shuffle_p95']}")
        for seed, w in a["worlds"].items():
            print(f"      s{seed}: n={w['events']:3d} wide={w['parent_wide_share']} "
                  f"parent={w['concordance_parent']} surrogate={w['concordance_surrogate']} diff={w['difference']}")
    print("  verdict:", verdict, "| worlds above band:", len(hits))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
