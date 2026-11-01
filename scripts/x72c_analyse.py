"""x72c_analyse.py — branch heredity with band powers: does a daughter's mixture follow her parent's?

Reads `x72c_pattern_s*.json` and the fields in `_x72c_fields/` (every 50 steps), computes per structure the fraction of local
power in the wide band (q_win 3–4, i.e. 12 cells) and the narrow band (q_win 5–6, i.e. 8.7 cells), and asks whether a
daughter's mixture resembles her parent's more than a nearest-distance stranger's.

Criteria: `reports/2026-11-01-x72c-band-power-plan.md`.

Run:
    python scripts/x72c_analyse.py --write
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
FIELDS = L1 / "_x72c_fields"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x72c_branch.json"

sys.path.insert(0, str(ROOT / "scripts"))
from x60_analyse import radial_profile  # noqa: E402

GRID = 96
WIN = 48
WIDE_BINS = (3, 4)      # q_win for 12.0 cells in a 48-cell window
NARROW_BINS = (5, 6)    # q_win for 8.7 cells
SHUFFLE = 2000
BAND = 0.15


def window_profile(v: np.ndarray, cx: float, cy: float) -> dict[float, float]:
    half = WIN // 2
    ys = [(int(round(cy)) + d) % GRID for d in range(-half, half + 1)]
    xs = [(int(round(cx)) + d) % GRID for d in range(-half, half + 1)]
    return radial_profile(v[np.ix_(ys, xs)])


def band_powers(prof: dict[int, float]) -> tuple[float, float] | None:
    if not prof:
        return None
    total = sum(prof.values())
    if total <= 0:
        return None
    wide = sum(prof.get(q, 0.0) for q in range(WIDE_BINS[0], WIDE_BINS[1] + 1))
    narrow = sum(prof.get(q, 0.0) for q in range(NARROW_BINS[0], NARROW_BINS[1] + 1))
    return wide / total, narrow / total


def rank(v: list[float]) -> list[float]:
    order = sorted(range(len(v)), key=lambda i: v[i])
    out = [0.0] * len(v)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
            j += 1
        avg = (i + j) / 2.0
        for k in range(i, j + 1):
            out[order[k]] = avg
        i = j + 1
    return out


def spearman(x: list[float], y: list[float]) -> float | None:
    if len(x) < 5:
        return None
    rx, ry = rank(x), rank(y)
    mx, my = st.mean(rx), st.mean(ry)
    sxy = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    sxx = sum((a - mx) ** 2 for a in rx)
    syy = sum((b - my) ** 2 for b in ry)
    if not sxx or not syy:
        return None
    return sxy / math.sqrt(sxx * syy)


def world_data(path: Path) -> dict:
    d = json.loads(path.read_text(encoding="utf-8"))
    first = {int(u["uid"]): int(u["first"]) for u in (d.get("uid_outcomes") or []) if u.get("first") is not None}
    snaps = []
    for s in d.get("series") or []:
        step = int(s["step"])
        f = FIELDS / f"{path.stem}_t{step}.npy"
        log = [c for c in (s.get("components_log") or []) if c.get("cx") is not None]
        if not f.is_file():
            snaps.append((step, log, {}, None))
            continue
        v = np.load(f)
        powers = {}
        for c in log:
            bp = band_powers(window_profile(v, c["cx"], c["cy"]))
            if bp:
                powers[int(c["uid"])] = bp
        snaps.append((step, log, powers, v))
    snaps.sort(key=lambda x: x[0])

    # instrument control: median local p_wide vs the global share of the wide band, over snapshots
    control = []
    for step, log, powers, v in snaps:
        if v is None or len(powers) < 3:
            continue
        gprof = radial_profile(v)
        if not gprof:
            continue
        gtotal = sum(gprof.values())
        gw = sum(gprof.get(q, 0.0) for q in range(7, 10)) / gtotal if gtotal else 0.0
        control.append((st.median(p[0] for p in powers.values()), gw))
    # Поправка 02.11: контроль по «разбросу» сначала считался как разброс МЕДИАН по времени (0.11-0.18) и валил все миры;
    # правильная величина — разброс p_wide МЕЖДУ структурами в одном срезе, потому что вопрос в том, различает ли
    # инструмент структуры друг от друга. Считаем его отдельно и сохраняем оба.
    within = []
    for step, log, powers, _v in snaps:
        if len(powers) >= 5:
            within.append(st.pstdev([p[0] for p in powers.values()]))
    ctl = {"points": len(control)}
    if within:
        ctl["within_snapshot_sd"] = round(st.median(within), 3)
        ctl["within_snapshot_sd_max"] = round(max(within), 3)
    if len(control) >= 5:
        xs = [a for a, _ in control]
        ys = [b for _, b in control]
        ctl["corr"] = round(spearman(xs, ys) or 0.0, 3)
        ctl["spread"] = round(st.pstdev(xs), 3)
        ctl["usable"] = bool(ctl["corr"] >= 0.5 and (ctl.get("within_snapshot_sd") or 0) >= 0.05)
    else:
        ctl["usable"] = False

    events = []
    for p_uid, c_uid in (d.get("uid_pairs") or []):
        p_uid, c_uid = int(p_uid), int(c_uid)
        if c_uid not in first:
            continue
        t_birth = first[c_uid]
        prev = [(t, pw) for t, _l, pw, _v in snaps if t < t_birth and p_uid in pw]
        nxt = [(t, log, pw) for t, log, pw, _v in snaps if t >= t_birth and c_uid in pw]
        if not prev or not nxt:
            continue
        _, pw_prev = prev[-1]
        _, log_child, pw_child = nxt[0]
        pos_c = next((c for c in log_child if int(c["uid"]) == c_uid), None)
        if pos_c is None:
            continue
        best = None
        for c in log_child:
            uid = int(c["uid"])
            if uid in (p_uid, c_uid) or uid not in pw_child:
                continue
            dx = min(abs(c["cx"] - pos_c["cx"]), GRID - abs(c["cx"] - pos_c["cx"]))
            dy = min(abs(c["cy"] - pos_c["cy"]), GRID - abs(c["cy"] - pos_c["cy"]))
            d = math.hypot(dx, dy)
            if best is None or d < best[0]:
                best = (d, pw_child[uid][0])
        events.append({"parent_wide": pw_prev[p_uid][0], "child_wide": pw_child[c_uid][0],
                       "surrogate_wide": best[1] if best else None})

    return {"events": events, "control": ctl}


def analyse(events: list[dict], rng: random.Random) -> dict:
    par = [e["parent_wide"] for e in events]
    ch = [e["child_wide"] for e in events]
    rho = spearman(par, ch)
    draws = []
    for _ in range(SHUFFLE):
        sh = par[:]
        rng.shuffle(sh)
        r = spearman(sh, ch)
        if r is not None:
            draws.append(r)
    draws.sort()
    minority = [e for e in events if (e["parent_wide"] >= 0.5) != (e["child_wide"] >= 0.5)]
    world_dominant = bool(st.median(par) >= 0.5) if par else None
    minority_events = [e for e in events if world_dominant is not None and (e["parent_wide"] >= 0.5) != world_dominant]
    disc = []
    sur = []
    for e in minority_events:
        disc.append((e["parent_wide"] >= 0.5) == (e["child_wide"] >= 0.5))
        if e["surrogate_wide"] is not None:
            sur.append((e["surrogate_wide"] >= 0.5) == (e["child_wide"] >= 0.5))
    return {
        "events": len(events),
        "rho": round(rho, 3) if rho is not None else None,
        "perm_p95": round(draws[int(0.95 * len(draws)) - 1], 3) if draws else None,
        "median_parent_wide": round(st.median(par), 3) if par else None,
        "median_child_wide": round(st.median(ch), 3) if ch else None,
        "minority_events": len(minority_events),
        "concordance_minority": round(sum(disc) / len(disc), 3) if disc else None,
        "concordance_surrogate": round(sum(sur) / len(sur), 3) if sur else None,
        "difference": round(sum(disc) / len(disc) - sum(sur) / len(sur), 3) if disc and sur else None,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X72c band-power heredity")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    rng = random.Random(72)

    res = {"kind": "l1_field_x72c_branch", "experiment": "X72c",
           "command": "python scripts/x72c_analyse.py --write",
           "prereg": "reports/2026-11-01-x72c-band-power-plan.md",
           "window": WIN, "wide_bins": WIDE_BINS, "narrow_bins": NARROW_BINS, "band": BAND,
           "worlds": {}, "controls": {}}

    pooled = []
    for path in sorted(L1.glob("x72c_pattern_s*.json")):
        wd = world_data(path)
        seed = path.stem.split("_s")[-1]
        res["worlds"][seed] = analyse(wd["events"], rng)
        res["controls"][seed] = wd["control"]
        pooled.extend(wd["events"])

    res["pooled"] = analyse(pooled, rng)
    usable = sum(1 for c in res["controls"].values() if c.get("usable"))
    wide_pooled = res["pooled"]["median_parent_wide"]
    positive_worlds = sum(1 for w in res["worlds"].values() if (w["rho"] or 0) > 0)
    minority_total = res["pooled"]["minority_events"]
    diff = res["pooled"]["difference"]

    if usable < 8 or wide_pooled is None or not (0.15 <= wide_pooled <= 0.85):
        verdict = "void: the local band-power readout failed its control"
    elif minority_total < 50:
        verdict = "underpowered: fewer than 50 minority events, the discrete statistic is unmeasured"
    elif (res["pooled"]["rho"] or 0) >= BAND and positive_worlds >= 8 and (diff or 0) >= BAND \
            and (res["pooled"]["rho"] or 0) > (res["pooled"]["perm_p95"] or 0):
        verdict = "supports branch heredity"
    elif (res["pooled"]["rho"] or 0) <= 0 or (diff is not None and diff < 0):
        verdict = "not supported"
    else:
        verdict = "inconclusive"
    res["verdict"] = verdict
    res["usable_worlds"] = usable
    res["positive_worlds"] = positive_worlds

    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[x72c] written: {OUT.name}")

    p = res["pooled"]
    print(f"  pooled: n={p['events']} rho={p['rho']} perm_p95={p['perm_p95']} median parent wide={p['median_parent_wide']}")
    print(f"  minority events={p['minority_events']} concordance={p['concordance_minority']} "
          f"surrogate={p['concordance_surrogate']} diff={p['difference']}")
    print(f"  controls usable={usable}/10, worlds with rho>0: {positive_worlds}/10")
    print(f"  verdict: {verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
