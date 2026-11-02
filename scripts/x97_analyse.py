"""x97_analyse.py — X97: does the sister advantage reach the second generation?

X93 measured sisters in the first generation (larger sister lives longer: +0.050 at F = 0.025, +0.082 at 0.030, reversed in the maze). This asks
whether the larger sister's *line* also does better: compare the granddaughters of the larger sister with those of the smaller.

Read from X108's dense logs (`--split-new-uid`), so no new runs. Plan: reports/2026-11-02-x97-sisters-second-generation-plan.md.

    python scripts/x97_analyse.py --write
"""
from __future__ import annotations

import argparse
import json
import random
import statistics as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from field_metrics import cell_files  # noqa: E402
from x102_analyse import world_data  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x97_sisters_second_generation.json"

CELLS = {"f030": 0.030, "f040": 0.040}
MIN_SISTER_PAIRS = 100
HEREDITY_FLOOR = 0.35
BOOTSTRAP = 2000


def ranks_of(vals):
    order = sorted(range(len(vals)), key=lambda i: vals[i])
    r = [0.0] * len(vals)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and vals[order[j + 1]] == vals[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            r[order[k]] = avg
        i = j + 1
    return r


def pearson(x, y):
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    return sxy / (sxx * syy) ** 0.5 if sxx and syy else None


def spearman(x, y):
    return pearson(ranks_of(x), ranks_of(y))


def cell_stats(flow: float) -> dict:
    pairs_heredity = []
    first_gen = []          # (larger sister's area - smaller sister's area)
    second_gen = []         # (mean granddaughter area of larger - of smaller)
    second_life = []
    sister_pairs = 0
    for path in cell_files(("x108",), flow, filename=""):
        w = world_data(path)
        children: dict[int, list[int]] = {}
        for child, par in w["parent"].items():
            children.setdefault(par, []).append(child)
        for mother, daughters in children.items():
            if mother not in w["peak"]:
                continue
            for d in daughters:
                if d in w["peak"]:
                    pairs_heredity.append((w["peak"][mother]["area"], w["peak"][d]["area"]))
            if len(daughters) < 2:
                continue
            for i in range(len(daughters)):
                for j in range(i + 1, len(daughters)):
                    a, b = daughters[i], daughters[j]
                    if a not in w["peak"] or b not in w["peak"]:
                        continue
                    ga = [g for g in children.get(a, []) if g in w["peak"]]
                    gb = [g for g in children.get(b, []) if g in w["peak"]]
                    if not ga or not gb:
                        continue
                    sister_pairs += 1
                    area_a, area_b = w["peak"][a]["area"], w["peak"][b]["area"]
                    first_gen.append(area_a - area_b)
                    big, small = (ga, gb) if area_a >= area_b else (gb, ga)
                    second_gen.append(st.mean(w["peak"][g]["area"] for g in big)
                                      - st.mean(w["peak"][g]["area"] for g in small))
                    la = st.mean(w["peak"][g].get("life", 0) or 0 for g in big)
                    lb = st.mean(w["peak"][g].get("life", 0) or 0 for g in small)
                    if la or lb:
                        second_life.append(la - lb)
    rho = spearman([p[0] for p in pairs_heredity], [p[1] for p in pairs_heredity]) if pairs_heredity else None
    return {"pairs_heredity": len(pairs_heredity), "rho_heredity": round(rho, 3) if rho is not None else None,
            "sister_pairs": sister_pairs, "n_first": len(first_gen), "n_second": len(second_gen),
            "first_gen_mean": round(st.mean(first_gen), 4) if first_gen else None,
            "second_gen_mean": round(st.mean(second_gen), 4) if second_gen else None,
            "second_life_mean": round(st.mean(second_life), 4) if second_life else None,
            "_first": first_gen, "_second": second_gen}


def z_of(vals: list[float]) -> float | None:
    if len(vals) < 5:
        return None
    m = st.mean(vals)
    sd = st.stdev(vals)
    return round(m / (sd / len(vals) ** 0.5), 2) if sd else None


def bootstrap_ci(vals: list[float], seed: int = 97) -> list[float] | None:
    if len(vals) < 5:
        return None
    rng = random.Random(seed)
    means = []
    n = len(vals)
    for _ in range(BOOTSTRAP):
        means.append(st.mean(rng.choice(vals) for _ in range(n)))
    means.sort()
    return [round(means[int(0.025 * BOOTSTRAP)], 4), round(means[int(0.975 * BOOTSTRAP)], 4)]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X97 sisters, second generation")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    cells = {tag: cell_stats(flow) for tag, flow in CELLS.items()}
    out_cells = {}
    for tag, c in cells.items():
        first, second = c.pop("_first"), c.pop("_second")
        c["first_gen_z"] = z_of(first)
        c["second_gen_z"] = z_of(second)
        c["second_gen_ci"] = bootstrap_ci(second)
        out_cells[tag] = c

    control_bad = []
    for tag, c in out_cells.items():
        if c["rho_heredity"] is None or c["rho_heredity"] < HEREDITY_FLOOR:
            control_bad.append(f"{tag}: heredity {c['rho_heredity']} below {HEREDITY_FLOOR}")
        if c["sister_pairs"] < MIN_SISTER_PAIRS:
            control_bad.append(f"{tag}: {c['sister_pairs']} sister pairs with granddaughters on both branches")
    lat = out_cells["f030"]
    if not (lat["first_gen_z"] is not None and lat["first_gen_z"] >= 2 and (lat["first_gen_mean"] or 0) > 0):
        control_bad.append(f"f030: the first-generation sister effect does not reproduce its sign (mean {lat['first_gen_mean']}, "
                           f"z {lat['first_gen_z']})")

    if control_bad:
        verdict = "void: " + "; ".join(control_bad)
    else:
        ci = lat["second_gen_ci"]
        if ci and ci[0] > 0:
            verdict = (f"the sister advantage persists into the second generation: the larger sister's granddaughters are larger by "
                       f"{lat['second_gen_mean']} cells on average (bootstrap 95 % CI {ci})")
        elif ci and ci[1] < 0:
            verdict = f"the advantage reverses in the second generation: {lat['second_gen_mean']} cells (CI {ci})"
        else:
            verdict = (f"the advantage is first-generation only: the granddaughters' difference is {lat['second_gen_mean']} cells with "
                       f"CI {ci}, which contains zero, while the first-generation effect passed its control")
        maze = out_cells["f040"]
        verdict += (f"; maze: first generation {maze['first_gen_mean']} (z {maze['first_gen_z']}), second generation "
                    f"{maze['second_gen_mean']} (CI {maze['second_gen_ci']})")

    res = {
        "kind": "l1_field_x97_sisters_second_generation",
        "experiment": "X97",
        "command": "python scripts/x97_analyse.py --write",
        "prereg": "reports/2026-11-02-x97-sisters-second-generation-plan.md",
        "readout": ("paired difference in granddaughters' peak area between the larger and the smaller sister, per sister pair, with a "
                    "bootstrap 95 % interval; the first-generation difference is the positive control"),
        "cells": out_cells,
        "verdict": verdict,
    }
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[x97] written: {OUT.name}")
    for tag, c in out_cells.items():
        print(f"  {tag}: heredity={c['rho_heredity']} sister_pairs={c['sister_pairs']} first={c['first_gen_mean']} "
              f"(z {c['first_gen_z']}) second={c['second_gen_mean']} (CI {c['second_gen_ci']}, z {c['second_gen_z']})")
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
