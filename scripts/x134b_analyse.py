"""x134b_analyse.py — X134: the mixing length, read from the genealogy of the two seeded lineages.

Two discs are seeded as uid 1 and uid 2 (with `--split-new-uid` each daughter gets a fresh uid, so a lineage is a subtree). The question is whether the habitat keeps
the two lineages apart or lets one take the other's cells. The primary readout is therefore genealogical, not the component count: does one seeded subtree disappear
into the other, when, and are both still present at the last step?

Plan: reports/2026-11-03-x134-mixing-plan.md.

    python scripts/x134b_analyse.py --write
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
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x134b_mixing.json"
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

    seeded = [u for u in SEED_UIDS if u in pos]
    both_seeded = len(seeded) == 2

    absorbed = None
    if both_seeded:
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

    first_comps = w["per_step"].get(steps[0]) or []
    first_n = len([c for c in first_comps if float(c.get("area") or 0) >= 5.0])
    last_comps = w["per_step"].get(last_step) or []
    total = sum(float(c["area"]) for c in last_comps)
    largest = max((float(c["area"]) for c in last_comps), default=0.0)
    return {
        "world": name, "sep": sep, "seed": seed,
        "both_seeded": both_seeded,
        "first_components": first_n,
        "usable": first_n == 2,
        "seeded_present": len(seeded),
        "absorbed_step": absorbed,
        "absorbed": absorbed is not None,
        "time_to_absorption": (absorbed - steps[0]) if absorbed is not None else None,
        "both_lineages_alive": bool(both_seeded and subtree_alive(SEED_UIDS[0]) and subtree_alive(SEED_UIDS[1])),
        "subtree_sizes": {str(u): len(descendants(kids, u)) for u in SEED_UIDS},
        "live": total >= OCCUPIED_FLOOR * GRID * GRID and largest >= LARGEST_FLOOR,
        "components_at_end": len(last_comps),
        "occupied": round(total / (GRID * GRID), 4),
        "steps": len(steps),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X134 mixing length")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    rows = [world_row(p) for p in sorted(L1.glob("x134b_sep*_s*.json")) if not p.name.endswith(".compact.json")]
    by_sep = {}
    degenerate = sorted({r["sep"] for r in rows if not r.get("usable")})
    for sep in sorted({r["sep"] for r in rows if r.get("usable")}):
        rs = sorted([r for r in rows if r["sep"] == sep and r.get("usable")], key=lambda r: r["seed"])
        absorbed = [r for r in rs if r["absorbed"]]
        both = [r for r in rs if r["both_lineages_alive"]]
        by_sep[str(sep)] = {
            "runs": len(rs),
            "absorbed": len(absorbed),
            "both_alive": len(both),
            "median_time": round(st.median([r["time_to_absorption"] for r in absorbed]), 1) if absorbed else None,
            "median_components_at_end": round(st.median([r["components_at_end"] for r in rs]), 1),
            "seeds": {str(r["seed"]): {"absorbed": r["absorbed"], "step": r["absorbed_step"],
                                       "both_alive": r["both_lineages_alive"],
                                       "subtrees": r["subtree_sizes"], "live": r["live"]} for r in rs},
        }

    seps = sorted(int(s) for s in by_sep)
    res_degenerate = degenerate
    mixing = [s for s in seps if by_sep[str(s)]["absorbed"] >= 3]
    apart = [s for s in seps if by_sep[str(s)]["absorbed"] <= 2]

    bad = []
    if len(rows) < 15:   # X134b is the declared bracketing replication: three separations, five seeds
        bad.append(f"{len(rows)} runs")
    not_two = [r["world"] for r in rows if not r["both_seeded"]]
    if len(not_two) > max(1, int(0.1 * len(rows))):
        bad.append(f"{len(not_two)} runs did not start as two seeded lineages ({not_two[:2]})")
    dead = [r["world"] for r in rows if not r["live"]]
    if len(dead) > 2:
        bad.append(f"{len(dead)} runs not alive ({dead[:2]})")
    if not mixing or not apart:
        bad.append("the sweep spans one outcome only (control 4): absorbed "
                   + str({s: by_sep[str(s)]["absorbed"] for s in seps}))

    if bad:
        verdict = "void: " + "; ".join(bad)
    else:
        lo, hi = max(mixing), min(apart)
        counts = ", ".join(f"{s}: {by_sep[str(s)]['absorbed']}/5 absorbed, "
                           f"{by_sep[str(s)]['both_alive']}/5 both alive" for s in seps)
        verdict = (f"a mixing length between {lo} and {hi} cells: one seeded lineage takes the other in at least 3 of 5 seeds up to "
                   f"{lo} cells and in at most 2 of 5 from {hi} on ({counts})")
        non_mono = [s for s in apart if s < lo]
        if non_mono:
            verdict += f"; non-monotone at {non_mono}"

    res = {
        "kind": "l1_field_x134_mixing",
        "experiment": "X134",
        "command": "python scripts/x134b_analyse.py --write",
        "prereg": "reports/2026-11-03-x134-mixing-plan.md",
        "definitions": {
            "seed_uids": "the two discs are uid 1 and uid 2; with --split-new-uid a lineage is the subtree",
            "absorption": f"one seeded uid ends without daughters while the other is present within r_dead + r_other + {REACH} cells of it",
            "both_alive": "both seeded subtrees have a member at the last logged step",
            "mixing_length": "between the largest separation absorbed in >= 3 of 5 seeds and the smallest absorbed in <= 2",
        },
        "by_separation": by_sep,
        "degenerate_separations": degenerate,
        "mixing": mixing,
        "apart": apart,
        "runs": len(rows),
        "verdict": verdict,
    }
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[x134] written: {OUT.name}")
    for s in seps:
        c = by_sep[str(s)]
        print(f"  sep {s:2d}: absorbed {c['absorbed']}/{c['runs']}  both alive {c['both_alive']}/{c['runs']}  "
              f"median time {c['median_time']}  components at end {c['median_components_at_end']}")
    print("  verdict:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
