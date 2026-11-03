"""x135_analyse.py — X135: the mixing length in the percolating cell, plus the single-disc control.

Same readout as X134 (a seeded lineage is a subtree; absorption is one seeded uid ending into the other's reach), applied at F = 0.040, with a SEP = 0 arm that seeds
one disc and says whether a lone seeded structure survives at all.

Plan: reports/2026-11-03-x135-maze-mixing-plan.md.

    python scripts/x135_analyse.py --write
"""
from __future__ import annotations

import argparse
import json
import math
import statistics as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from x102_analyse import world_data  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x135_maze_mixing.json"
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"

REACH = 2.0
SEED_UIDS = (1, 2)
OCCUPIED_FLOOR = 0.05
LARGEST_FLOOR = 50
GRID = 96


def descendants(kids, uid):
    out, stack = [], [uid]
    while stack:
        node = stack.pop()
        out.append(node)
        stack.extend(kids.get(node, []))
    return out


def world_row(path) -> dict:
    w = world_data(path)
    parent = {int(c): int(p) for c, p in w["parent"].items()}
    kids: dict[int, list[int]] = {}
    for child, par in parent.items():
        kids.setdefault(par, []).append(child)
    steps = sorted(int(s) for s in w["per_step"])
    name = Path(path).name
    sep = int(name.split("_sep")[1].split("_")[0])
    seed = int(name.split("_s")[-1].replace(".json", ""))

    pos: dict[int, tuple[int, float, float, float]] = {}
    for t in steps:
        for c in (w["per_step"].get(t) or []):
            pos[int(c["uid"])] = (t, float(c.get("cx", 0)), float(c.get("cy", 0)), float(c["area"]))
    last_step = steps[-1]
    present = {u for u, v in pos.items() if v[0] == last_step}

    def subtree_alive(u):
        return any(x in present for x in descendants(kids, u))

    first_comps = w["per_step"].get(steps[0]) or []
    first_n = len([c for c in first_comps if float(c.get("area") or 0) >= 5.0])
    expect_first = 1 if sep == 0 else 2

    seeded = [u for u in SEED_UIDS if u in pos]
    both_seeded = len(seeded) == 2

    absorbed = None
    if sep > 0 and both_seeded:
        for dead, other in ((SEED_UIDS[0], SEED_UIDS[1]), (SEED_UIDS[1], SEED_UIDS[0])):
            if dead not in pos or kids.get(dead):
                continue
            t_end, cx, cy, area = pos[dead]
            o = pos.get(other)
            if o is None or o[0] < t_end:
                continue
            d = math.hypot(o[1] - cx, o[2] - cy)
            if d <= math.sqrt(area / math.pi) + math.sqrt(o[3] / math.pi) + REACH:
                absorbed = t_end
                break

    control_alive = None
    if sep == 0:
        control_alive = subtree_alive(SEED_UIDS[0]) if SEED_UIDS[0] in pos else False

    last_comps = w["per_step"].get(last_step) or []
    total = sum(float(c["area"]) for c in last_comps)
    largest = max((float(c["area"]) for c in last_comps), default=0.0)
    return {
        "world": name, "sep": sep, "seed": seed,
        "first_components": first_n, "expected_first": expect_first, "usable": first_n == expect_first,
        "both_seeded": both_seeded,
        "absorbed_step": absorbed,
        "absorbed": absorbed is not None,
        "time_to_absorption": (absorbed - steps[0]) if absorbed is not None else None,
        "both_lineages_alive": bool(sep > 0 and both_seeded and subtree_alive(SEED_UIDS[0]) and subtree_alive(SEED_UIDS[1])),
        "control_alive": control_alive,
        "control_subtree": (len(descendants(kids, SEED_UIDS[0])) if sep == 0 and SEED_UIDS[0] in pos else None),
        "live": total >= OCCUPIED_FLOOR * GRID * GRID and largest >= LARGEST_FLOOR,
        "components_at_end": len(last_comps),
        "occupied": round(total / (GRID * GRID), 4),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X135 maze mixing length")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    rows = [world_row(p) for p in sorted(L1.glob("x135_sep*_s*.json")) if not p.name.endswith(".compact.json")]
    by_sep = {}
    for sep in sorted({r["sep"] for r in rows}):
        rs = sorted([r for r in rows if r["sep"] == sep], key=lambda r: r["seed"])
        usable = [r for r in rs if r["usable"]]
        absorbed = [r for r in usable if r["absorbed"]]
        entry = {
            "runs": len(rs), "usable": len(usable),
            "absorbed": len(absorbed),
            "both_alive": len([r for r in usable if r["both_lineages_alive"]]),
            "median_time": round(st.median([r["time_to_absorption"] for r in absorbed]), 1) if absorbed else None,
            "median_components_at_end": round(st.median([r["components_at_end"] for r in rs]), 1),
            "seeds": {str(r["seed"]): {"absorbed": r["absorbed"], "step": r["absorbed_step"],
                                       "both_alive": r["both_lineages_alive"], "usable": r["usable"],
                                       "live": r["live"]} for r in rs},
        }
        if sep == 0:
            entry["control_alive"] = len([r for r in rs if r["control_alive"]])
            entry["control_subtree_median"] = (round(st.median([r["control_subtree"] for r in rs if r["control_subtree"] is not None]), 1)
                                               if any(r["control_subtree"] is not None for r in rs) else None)
        by_sep[str(sep)] = entry

    mixing_seps = [s for s in sorted(by_sep) if int(s) > 0]
    seps = [int(s) for s in mixing_seps]
    mixing = [s for s in seps if by_sep[str(s)]["absorbed"] >= 3]
    apart = [s for s in seps if by_sep[str(s)]["absorbed"] <= 2]
    control_ok = by_sep.get("0", {}).get("control_alive", 0) >= 4

    bad = []
    if len(rows) < 30:
        bad.append(f"{len(rows)} runs")
    not_started = [r["world"] for r in rows if not r["usable"]]
    if len(not_started) > 3:
        bad.append(f"{len(not_started)} runs did not start as expected ({not_started[:2]})")
    dead = [r["world"] for r in rows if not r["live"]]
    if len(dead) > 2:
        bad.append(f"{len(dead)} runs not alive ({dead[:2]})")
    if not control_ok:
        bad.append(f"the single-disc control survives in only {by_sep.get('0', {}).get('control_alive', 0)} of 5 seeds")

    counts = ", ".join(f"{s}: {by_sep[str(s)]['absorbed']}/{by_sep[str(s)]['usable']} absorbed, "
                       f"{by_sep[str(s)]['both_alive']} both alive" for s in seps)
    if bad:
        verdict = "void: " + "; ".join(bad)
    elif len(mixing) == len(seps):
        verdict = (f"the body mixes everything: absorption in at least 3 of 5 seeds at every separation up to 36 cells ({counts}), "
                   f"with the single-disc control alive in {by_sep['0']['control_alive']} of 5 seeds, so a lone seeded structure does "
                   f"survive here and the merging is not the world simply dying")
    elif mixing and apart:
        lo, hi = max(mixing), min(apart)
        verdict = (f"a mixing length between {lo} and {hi} cells at F = 0.040, against 12-18 in the lattice ({counts}), with the "
                   f"single-disc control alive in {by_sep['0']['control_alive']} of 5 seeds")
        non_mono = [s for s in apart if s < lo]
        if non_mono:
            verdict += f"; non-monotone at {non_mono}"
    else:
        verdict = f"no separation shows absorption in 3 of 5 seeds ({counts})"

    res = {
        "kind": "l1_field_x135_maze_mixing",
        "experiment": "X135",
        "command": "python scripts/x135_analyse.py --write",
        "prereg": "reports/2026-11-03-x135-maze-mixing-plan.md",
        "definitions": {
            "absorption": f"one seeded uid ends without daughters while the other is present within r_dead + r_other + {REACH} cells of it",
            "control": "SEP = 0 seeds one disc (both offsets coincide); the arm reports whether a lone seeded structure survives",
            "mixing_length": "between the largest separation absorbed in >= 3 of 5 seeds and the smallest absorbed in <= 2",
        },
        "flow": 0.040,
        "by_separation": by_sep,
        "mixing": mixing,
        "apart": apart,
        "runs": len(rows),
        "verdict": verdict,
    }
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[x135] written: {OUT.name}")
    for s in sorted(by_sep, key=int):
        c = by_sep[s]
        extra = f"  control alive {c.get('control_alive')}/5 subtree {c.get('control_subtree_median')}" if s == "0" else ""
        print(f"  sep {s:>2}: absorbed {c['absorbed']}/{c['usable']}  both alive {c['both_alive']}  "
              f"median time {c['median_time']}  components {c['median_components_at_end']}{extra}")
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
