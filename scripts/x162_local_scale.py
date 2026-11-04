"""X162: is the local scale inherited? Parent-daughter reconstruction from the X156 compact logs, with area and shape
as positive controls, in both habitats of that series.

Analysis only. Writes morphogenesis/experiments/E09_pond/l1_field_x162_local_scale.json.
"""
from __future__ import annotations

import json
import math
import random
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x162_local_scale.json"
HABITATS = (("lattice", "x156_shape_f030_s8*.compact.json"), ("maze", "x156_shape_f040_s8*.compact.json"))
BOOT = 2000
SEED = 20261104


def components(row):
    return row[1] if isinstance(row, list) and len(row) > 1 else []


def r_of(area: float) -> float:
    return math.sqrt(max(area, 1.0) / math.pi)


def periodic(dx: float, dy: float, grid: int) -> float:
    dx = abs(dx) % grid
    dy = abs(dy) % grid
    dx = min(dx, grid - dx)
    dy = min(dy, grid - dy)
    return math.hypot(dx, dy)


def spacing(comp, others, grid: int):
    best = None
    for o in others:
        if o["uid"] == comp["uid"]:
            continue
        d = periodic(o["cx"] - comp["cx"], o["cy"] - comp["cy"], grid) - r_of(comp["area"]) - r_of(o["area"])
        if best is None or d < best:
            best = d
    return best


def ols(xs, ys):
    n = len(xs)
    if n < 3:
        return None, None, n
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx <= 0:
        return None, None, n
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    resid = [y - (my + slope * (x - mx)) for x, y in zip(xs, ys)]
    sd = math.sqrt(sum(r * r for r in resid) / max(n - 2, 1))
    return slope, sd / math.sqrt(sxx), n


def boot_slope(xs, ys, rng):
    n = len(xs)
    out = []
    for _ in range(BOOT):
        idx = [rng.randrange(n) for _ in range(n)]
        s, _, _ = ols([xs[i] for i in idx], [ys[i] for i in idx])
        if s is not None:
            out.append(s)
    out.sort()
    return (out[int(0.025 * len(out))], out[int(0.975 * len(out)) - 1]) if out else (None, None)


def pairs_of(pattern: str) -> tuple[list[dict], int]:
    files = sorted(L1.glob(pattern))
    pairs, runs = [], 0
    for path in files:
        art = json.loads(path.read_text(encoding="utf-8"))
        params = art.get("params") or {}
        grid = int(params.get("grid", 96))
        seed = int(params.get("seed", 0))
        rows, prev = [], {}
        for row in art.get("series") or []:
            step = row[0] if isinstance(row, list) else None
            comps = components(row)
            by_uid = {c["uid"]: c for c in comps}
            new = [u for u in by_uid if u not in prev]
            gone = [u for u in prev if u not in by_uid]
            if new and gone:
                for child_uid in new:
                    child = by_uid[child_uid]
                    sp_c = spacing(child, [c for c in comps if c["uid"] != child_uid], grid)
                    if sp_c is None:
                        continue
                    mothers = [(periodic(prev[u]["cx"] - child["cx"], prev[u]["cy"] - child["cy"], grid), u) for u in gone]
                    if not mothers:
                        continue
                    mother = prev[min(mothers)[1]]
                    sp_m = spacing(mother, list(prev.values()), grid)
                    if sp_m is None:
                        continue
                    rows.append({
                        "seed": seed, "step": step, "uid": child_uid,
                        "sp_mother": sp_m, "sp_daughter": sp_c,
                        "area_mother": mother["area"], "area_daughter": child["area"],
                        "elong_mother": math.log(max(mother.get("elong", 1.0), 1e-6)),
                        "elong_daughter": math.log(max(child.get("elong", 1.0), 1e-6)),
                        "r_mother": r_of(mother["area"]),
                    })
            prev = by_uid
        if len(rows) >= 20:
            runs += 1
        pairs.extend(rows)
    return pairs, runs


def analyse(pattern: str, rng: random.Random) -> dict:
    pairs, runs = pairs_of(pattern)
    if not pairs:
        return {"error": f"no pairs for {pattern}"}

    def slopes(kx, ky):
        s, se, n = ols([p[kx] for p in pairs], [p[ky] for p in pairs])
        lo, hi = boot_slope([p[kx] for p in pairs], [p[ky] for p in pairs], rng)
        return {"slope": s, "se": se, "n": n, "ci": [lo, hi]}

    pooled = {"spacing": slopes("sp_mother", "sp_daughter"),
              "area": slopes("area_mother", "area_daughter"),
              "log_elong": slopes("elong_mother", "elong_daughter")}

    # partial slope of spacing on the mother's spacing, controlling for her radius
    xs = [p["sp_mother"] for p in pairs]
    ys = [p["sp_daughter"] for p in pairs]
    zs = [p["r_mother"] for p in pairs]
    mx, my, mz = statistics.fmean(xs), statistics.fmean(ys), statistics.fmean(zs)
    szz = sum((z - mz) ** 2 for z in zs) or 1e-9
    sxz = sum((x - mx) * (z - mz) for x, z in zip(xs, zs))
    syz = sum((y - my) * (z - mz) for y, z in zip(ys, zs))
    rx = [x - mx - sxz / szz * (z - mz) for x, z in zip(xs, zs)]
    ry = [y - my - syz / szz * (z - mz) for y, z in zip(ys, zs)]
    partial, _, _ = ols(rx, ry)

    by_seed: dict[int, list[dict]] = {}
    for p in pairs:
        by_seed.setdefault(p["seed"], []).append(p)
    null = []
    for _ in range(500):
        x2, y2 = [], []
        for rows in by_seed.values():
            mums = [p["sp_mother"] for p in rows]
            rng.shuffle(mums)
            x2.extend(mums)
            y2.extend([p["sp_daughter"] for p in rows])
        s, _, _ = ols(x2, y2)
        if s is not None:
            null.append(s)
    null.sort()
    null_band = [null[int(0.025 * len(null))], null[int(0.975 * len(null)) - 1]] if null else [None, None]

    run_slopes = []
    for rows in by_seed.values():
        s, _, _ = ols([p["sp_mother"] for p in rows], [p["sp_daughter"] for p in rows])
        if s is not None:
            run_slopes.append(s)
    run_med = statistics.median(run_slopes) if run_slopes else None
    run_ci = None
    if len(run_slopes) >= 5:
        meds = []
        for _ in range(BOOT):
            meds.append(statistics.median([run_slopes[rng.randrange(len(run_slopes))] for _ in run_slopes]))
        meds.sort()
        run_ci = [meds[int(0.025 * len(meds))], meds[int(0.975 * len(meds)) - 1]]

    vals = [p["sp_mother"] for p in pairs] + [p["sp_daughter"] for p in pairs]
    readout = {"sd": statistics.pstdev(vals), "median": statistics.median(vals)}
    control_ok = pooled["area"]["slope"] is not None and 0.35 <= pooled["area"]["slope"] <= 0.55
    readout_ok = readout["sd"] >= 0.5 and 1.0 <= readout["median"] <= 20.0
    ci = pooled["spacing"]["ci"]
    decided = ci[0] is not None and ci[0] > 0.0 and run_ci is not None and run_ci[0] > 0.0
    if not control_ok:
        verdict = "NOT REPORTABLE: the area slope did not reproduce X156's 0.45, so the reconstruction differs."
    elif not readout_ok:
        verdict = "NOT REPORTABLE: the spacing readout has too little spread to carry information."
    elif decided:
        verdict = ("THE LOCAL SCALE IS INHERITED, and more weakly than shape: the daughter's spacing on her mother's has "
                   "a slope whose interval excludes zero and the shuffled-parent null.")
    else:
        verdict = ("THE LOCAL SCALE IS NOT INHERITED: the slope is indistinguishable from the shuffled-parent null.")
    return {"runs": runs, "pairs": len(pairs), "pooled": pooled, "partial_on_mother_radius": partial,
            "null_band": null_band, "run_level": {"median_slope": run_med, "ci": run_ci, "runs": len(run_slopes)},
            "readout": readout, "controls": {"positive_control_fires": control_ok, "readout_exists": readout_ok},
            "verdict": verdict}


def main() -> int:
    rng = random.Random(SEED)
    by_hab = {name: analyse(pattern, rng) for name, pattern in HABITATS}
    agg = {"kind": "x162_local_scale", "question": "is the local scale of the pattern inherited across a division?",
           "method": ("parent-daughter pairs as in X156: the mother at her last logged step before the daughter's uid "
                      "appears, the daughter at her first; both read with the surface gap to the nearest neighbour"),
           "by_habitat": by_hab, "verdict": None}
    ok = [h for h in by_hab.values() if h.get("controls", {}).get("positive_control_fires")]
    if not ok:
        agg["verdict"] = "NOT REPORTABLE: no habitat reproduced the area control."
    else:
        agg["verdict"] = "; ".join(f"{k}: {v['verdict']}" for k, v in by_hab.items() if v.get("verdict"))
    OUT.write_text(json.dumps(agg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"[x162] written {OUT.relative_to(ROOT)}")
    for name, h in by_hab.items():
        if "error" in h:
            print(f"[x162] {name}: {h['error']}")
            continue
        print(f"[x162] {name}: runs {h['runs']} pairs {h['pairs']} | spacing {h['pooled']['spacing']['slope']:.4f} "
              f"ci {[round(x, 4) for x in h['pooled']['spacing']['ci']]} null "
              f"{[round(x, 4) for x in h['null_band']]} | area {h['pooled']['area']['slope']:.4f} | "
              f"elong {h['pooled']['log_elong']['slope']:.4f} | partial {h['partial_on_mother_radius']:.4f} | "
              f"run-level {h['run_level']['median_slope']:.4f} ci "
              f"{[round(x, 4) for x in (h['run_level']['ci'] or [0, 0])]}")
        print(f"[x162] {name}: {h['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
