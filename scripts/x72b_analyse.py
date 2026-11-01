"""x72b_analyse.py — branch concordance at the multistability boundary, read from local spectra.

Reads `x72b_pattern_s*.json` and the fields in `_x72b_fields/` (written every 50 steps), computes the local wavelength in a
48-cell window around each structure, classifies it into X71's two branches, and compares parent–daughter branch agreement
with a nearest-distance surrogate and a within-world permutation null.

Criteria: `reports/2026-11-01-x72b-branch-heredity-plan.md`. Primary readout: 48-cell window, split at 10.4 cells. A 64-cell
window is computed as a robustness check and is reported separately, never as the primary.

Run:
    python scripts/x72b_analyse.py --write
"""
from __future__ import annotations

import argparse
import json
import math
import random
import statistics as st
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
FIELDS = L1 / "_x72b_fields"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x72b_branch.json"

sys.path.insert(0, str(ROOT / "scripts"))
from x60_analyse import radial_profile  # noqa: E402

GRID = 96
WIN_PRIMARY = 48
WIN_CHECK = 64
SPLIT = 10.4             # cells, fixed in the preregistration
SHUFFLE_DRAWS = 2000
BAND = 0.15
CONTROL_CORR = 0.5
CONTROL_SPREAD = 3.3     # cells, the gap between 12.0 and 8.73


def wrap_slice(centre: float, half: int, n: int = GRID):
    i = int(round(centre))
    idx = [(i + d) % n for d in range(-half, half + 1)]
    return np.ix_(idx, idx)


def local_lambda(v: np.ndarray, cx: float, cy: float, win: int) -> float | None:
    half = win // 2
    sub = v[np.ix_([(int(round(cy)) + d) % GRID for d in range(-half, half + 1)],
                   [(int(round(cx)) + d) % GRID for d in range(-half, half + 1)])]
    prof = radial_profile(sub)
    if not prof:
        return None
    q = max(prof, key=prof.get)
    if q <= 0:
        return None
    return win / float(q)


def branch(lam: float | None) -> str | None:
    if lam is None:
        return None
    return "wide" if lam >= SPLIT else "narrow"


def snapshots_with_fields(path: Path, win: int):
    d = json.loads(path.read_text(encoding="utf-8"))
    tag = path.stem
    out = []
    for s in d.get("series") or []:
        step = int(s["step"])
        f = FIELDS / f"{tag}_t{step}.npy"
        if not f.is_file():
            out.append((step, s.get("components_log") or [], {}, None))
            continue
        v = np.load(f)
        log = [c for c in (s.get("components_log") or []) if c.get("cx") is not None]
        lams = {}
        for c in log:
            lam = local_lambda(v, c["cx"], c["cy"], win)
            if lam is not None:
                lams[int(c["uid"])] = lam
        out.append((step, log, lams, v))
    out.sort(key=lambda x: x[0])
    return out


def events_for_world(path: Path, win: int) -> tuple[list[dict], dict]:
    d = json.loads(path.read_text(encoding="utf-8"))
    first = {int(u["uid"]): int(u["first"]) for u in (d.get("uid_outcomes") or []) if u.get("first") is not None}
    snaps = snapshots_with_fields(path, win)

    out = []
    for p_uid, c_uid in (d.get("uid_pairs") or []):
        p_uid, c_uid = int(p_uid), int(c_uid)
        if c_uid not in first:
            continue
        t_birth = first[c_uid]
        prev = [(t, lams) for t, log, lams, _ in snaps if t < t_birth and p_uid in lams]
        nxt = [(t, log, lams) for t, log, lams, _ in snaps if t >= t_birth and c_uid in lams]
        if not prev or not nxt:
            continue
        _, m_prev = prev[-1]
        _, log_child, m_child = nxt[0]
        pb = branch(m_prev.get(p_uid))
        cb = branch(m_child.get(c_uid))
        if pb is None or cb is None:
            continue
        pos_c = next((c for c in log_child if int(c["uid"]) == c_uid), None)
        if pos_c is None:
            continue
        cands = []
        for c in log_child:
            uid = int(c["uid"])
            if uid in (p_uid, c_uid) or uid not in m_child:
                continue
            dxy = math.hypot(min(abs(c["cx"] - pos_c["cx"]), GRID - abs(c["cx"] - pos_c["cx"])),
                             min(abs(c["cy"] - pos_c["cy"]), GRID - abs(c["cy"] - pos_c["cy"])))
            cands.append((dxy, branch(m_child[uid])))
        cands.sort()
        out.append({"parent": pb, "child": cb, "surrogate": cands[0][1] if cands else None,
                    "lambda_parent": round(m_prev[p_uid], 2), "lambda_child": round(m_child[c_uid], 2)})

    # instrument control: median local wavelength vs the global peak of the same snapshot
    pairs = []
    for step, log, lams, v in snaps:
        if v is None or len(lams) < 3:
            continue
        prof = radial_profile(v)
        if not prof:
            continue
        q_glob = max(prof, key=prof.get)
        if q_glob <= 0:
            continue
        pairs.append((st.median(lams.values()), GRID / float(q_glob)))
    control = {"points": len(pairs)}
    if len(pairs) >= 5:
        xs = [a for a, _ in pairs]
        ys = [b for _, b in pairs]
        mx, my = st.mean(xs), st.mean(ys)
        sx, sy = st.pstdev(xs), st.pstdev(ys)
        control.update({
            "corr_local_vs_global": round(sum((a - mx) * (b - my) for a, b in pairs) / len(pairs) / (sx * sy), 3)
            if sx and sy else None,
            "local_spread_cells": round(sx, 2),
            "global_wavelengths": sorted({round(y, 1) for y in ys}),
        })
    control["usable"] = bool(control.get("corr_local_vs_global") is not None
                             and abs(control["corr_local_vs_global"]) >= CONTROL_CORR
                             and (control.get("local_spread_cells") or 0) >= CONTROL_SPREAD / 2)
    return out, control


def concordance(pairs: list[tuple[str, str]]) -> float | None:
    if not pairs:
        return None
    return sum(1 for a, b in pairs if a == b) / len(pairs)


def analyse(evs: list[dict], rng: random.Random) -> dict:
    par = [(e["parent"], e["child"]) for e in evs]
    sur = [(e["surrogate"], e["child"]) for e in evs if e["surrogate"]]
    obs, sur_c = concordance(par), concordance(sur)
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
    wide = sum(1 for e in evs if e["parent"] == "wide") / len(evs) if evs else None
    return {"events": len(evs), "wide_share": round(wide, 3) if wide is not None else None,
            "concordance_parent": round(obs, 3) if obs is not None else None,
            "concordance_surrogate": round(sur_c, 3) if sur_c is not None else None,
            "difference": round(obs - sur_c, 3) if (obs is not None and sur_c is not None) else None,
            "shuffle_p95": round(draws[int(0.95 * len(draws)) - 1], 3) if draws else None,
            "shuffle_median": round(st.median(draws), 3) if draws else None}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X72b branch concordance")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    rng = random.Random(72)

    res = {"kind": "l1_field_x72b_branch", "experiment": "X72b",
           "command": "python scripts/x72b_analyse.py --write",
           "prereg": "reports/2026-11-01-x72b-branch-heredity-plan.md",
           "window_primary": WIN_PRIMARY, "window_check": WIN_CHECK,
           "split_cells": SPLIT, "band": BAND, "primary": {}, "robustness": {}}

    for key, win in (("primary", WIN_PRIMARY), ("robustness", WIN_CHECK)):
        worlds, pooled, controls = {}, [], {}
        for f in sorted(L1.glob("x72b_pattern_s*.json")):
            evs, ctl = events_for_world(Path(f), win)
            worlds[Path(f).stem.split("_s")[-1]] = analyse(evs, rng)
            controls[Path(f).stem.split("_s")[-1]] = ctl
            pooled.extend(evs)
        res[key] = {"worlds": worlds, "pooled": analyse(pooled, rng),
                    "controls": controls, "usable_worlds": sum(1 for c in controls.values() if c.get("usable"))}

    pat = res["primary"]
    pooled = pat["pooled"]
    usable = pat["usable_worlds"]
    wide = pooled["wide_share"]
    hits = [w for w in pat["worlds"].values() if (w["difference"] or 0) >= BAND]
    enough_events = sum(1 for w in pat["worlds"].values() if w["events"] >= 100) >= 3
    if usable < 3 or not enough_events or wide is None or not (0.25 <= wide <= 0.75):
        verdict = ("void: the local-spectrum readout failed its control (or too few events), so no concordance number "
                   "counts")
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
        print(f"[x72b] written: {OUT.name}")

    for key in ("primary", "robustness"):
        p = res[key]
        print(f"  {key} (win={res['window_primary'] if key == 'primary' else res['window_check']}): "
              f"usable_worlds={p['usable_worlds']} pooled n={p['pooled']['events']} wide={p['pooled']['wide_share']} "
              f"parent={p['pooled']['concordance_parent']} surrogate={p['pooled']['concordance_surrogate']} "
              f"diff={p['pooled']['difference']} shuffle_p95={p['pooled']['shuffle_p95']}")
        for seed, w in p["worlds"].items():
            print(f"      s{seed}: n={w['events']:3d} wide={w['wide_share']} parent={w['concordance_parent']} "
                  f"surrogate={w['concordance_surrogate']} diff={w['difference']}")
        for seed, c in p["controls"].items():
            print(f"      control s{seed}: {c}")
    print("  verdict:", verdict, "| worlds above band:", len(hits))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
