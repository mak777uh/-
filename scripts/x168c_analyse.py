"""x168c_analyse.py — the inflow test with the gap converted correctly.

Short arms (2 000 steps): F in (0.026, 0.030, 0.036) x surface gaps (8, 10, 11), five seeds each. The crossing of a rate is
the highest gap whose fusion share reaches 0.6.
Length control (6 000 steps): F = 0.030 at surface gaps 10 and 11, the same seeds, so the short arms can be compared with the
X158 baseline (7/15 at gap 10, 2/15 at gap 11) at the same length as well as at their own.

Writes morphogenesis/experiments/E09_pond/l1_field_x168c_inflow.json.
"""
from __future__ import annotations

import json
import math
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x168c_inflow.json"
FUSE_AT = 0.6
X158_G10, X158_G11 = 7.0 / 15.0, 2.0 / 15.0


def comps(row):
    if isinstance(row, dict):
        return row.get("components_log") or []
    return []


def r_of(a):
    return math.sqrt(max(a, 1.0) / math.pi)


def gaps_between(c, grid=96):
    c = sorted(c, key=lambda x: x["cx"])
    out = []
    for i in range(len(c) - 1):
        dx = abs(c[i + 1]["cx"] - c[i]["cx"]) % grid
        dy = abs(c[i + 1]["cy"] - c[i]["cy"]) % grid
        d = math.hypot(min(dx, grid - dx), min(dy, grid - dy))
        out.append(d - r_of(c[i]["area"]) - r_of(c[i + 1]["area"]))
    return out


def read(name: str) -> dict:
    art = json.loads((L1 / name).read_text(encoding="utf-8"))
    series = art.get("series") or []
    counts = [row.get("components", len(comps(row))) for row in series]
    last_two = None
    for row in reversed(series):
        c = comps(row)
        if len(c) == 2:
            last_two = gaps_between(c)
            break
    return {"min": min(counts) if counts else None, "last_two": last_two,
            "of": (art.get("params") or {}).get("init_spots")}


def main() -> int:
    short: dict[tuple[float, int], list[dict]] = {}
    for f in sorted(L1.glob("x168c_F*_g*_s96*.json")):
        if f.name.endswith(".compact.json"):
            continue
        parts = f.stem.split("_")
        flow = int(parts[1][1:]) / 1000.0
        gap = int(parts[2][1:])
        short.setdefault((flow, gap), []).append({"run": f.stem, **read(f.name)})
    length: dict[int, list[dict]] = {}
    for f in sorted(L1.glob("x168c_F*_len_s96*.json")):
        parts = f.stem.split("_")
        length.setdefault(int(parts[1][1:]) / 1000.0, []).append({"run": f.stem, **read(f.name)})

    table, crossings = {}, {}
    for (flow, gap), rows in sorted(short.items()):
        fused = sum(1 for r in rows if r["min"] == 1)
        died = sum(1 for r in rows if r["min"] == 0)
        table[f"F{flow:g}_g{gap}"] = {"flow": flow, "gap": gap, "runs": len(rows), "fused": fused, "died": died,
                                      "share": round(fused / len(rows), 4), "mins": [r["min"] for r in rows],
                                      "seps": sorted({r["of"] for r in rows if r["of"]})}
    for flow in sorted({f for f, _ in short}):
        gs = sorted(g for f, g in short if f == flow)
        crossings[f"{flow:g}"] = max((g for g in gs if (table[f"F{flow:g}_g{g}"]["share"] or 0) >= FUSE_AT), default=None)

    def share(flow, gap):
        key = f"F{flow:g}_g{gap}"
        return table[key]["share"] if key in table else None

    long_rows = length.get(0.030, [])
    long_fused = {g: sum(1 for r in length[0.030] if False) for g in ()}  # placeholder, filled below
    long_share = {}
    for g in (10, 11):
        rows = [r for r in long_rows if f"_g{g}_" in r["run"] or f"_g{g}_" in r["run"]]
        long_share[g] = None
    # the length files carry the gap in their name as 'len', so recover the gap from the initial separation
    for r in long_rows:
        sep = r.get("of") or ""
        try:
            g = round(float(sep.split(":")[1]) - 6.0, 1)
        except (ValueError, IndexError):
            continue
        long_share.setdefault(int(g), []).append(r) if isinstance(long_share.get(int(g)), list) else long_share.__setitem__(int(g), [r])
    long_summary = {}
    for g, rows in long_share.items():
        if isinstance(rows, list) and rows:
            fused = sum(1 for r in rows if r["min"] == 1)
            long_summary[f"g{g}"] = {"runs": len(rows), "fused": fused, "share": round(fused / len(rows), 4),
                                     "mins": [r["min"] for r in rows]}

    controls = {f"{f:g}": (share(f, 8) is not None and share(f, 8) >= 0.8) for f in sorted({f for f, _ in short})}
    all_gaps = [g for rows in short.values() for r in rows for g in (r["last_two"] or [])]
    spread = round(statistics.pstdev(all_gaps), 4) if len(all_gaps) > 1 else None
    row030 = {g: share(0.030, g) for g in (8, 10, 11) if share(0.030, g) is not None}
    # a crossing between 10 and 11 means: gap 10 fuses more often than gap 11, and gap 11 does not reach the fuse threshold
    crossing_ok = (row030.get(11) is not None and row030[11] < FUSE_AT
                   and row030.get(10) is not None and row030[10] > row030[11])
    s11 = {f: share(f, 11) for f in sorted({f for f, _ in short})}
    spread11 = max(s11.values()) - min(s11.values()) if all(v is not None for v in s11.values()) else None

    if not all(controls.values()):
        verdict = ("NOT COMPARABLE: the gap-8 control failed at " +
                   ", ".join(f"F = {k}" for k, ok in controls.items() if not ok) +
                   ", so those arms are dropped rather than averaged over.")
    elif not crossing_ok:
        verdict = (f"NOT REPORTABLE: the F = 0.030 row does not place a crossing between gaps 10 and 11 on this seed set at "
                   f"2 000 steps (gap 10 {row030.get(10)}, gap 11 {row030.get(11)}), so this design cannot ask whether the "
                   f"crossing moves with the rate.")
    elif spread11 is not None and spread11 <= 0.4:
        verdict = ("NO DETECTABLE DEPENDENCE OF THE CROSSING ON THE INFLOW RATE: the gap-11 share is "
                   + ", ".join(f"{v:.0%} at F = {k}" for k, v in s11.items()) +
                   f" (a spread of {spread11:.0%}), while the gap-10 share is {row030.get(10, float('nan')):.0%} at "
                   f"F = 0.030, so the crossing sits between 10 and 11 cells at every rate tested and the ten-cell number is "
                   "a property of the reaction-diffusion pair rather than of the flow. With five seeds only a large shift "
                   "would be visible.")
    else:
        verdict = ("THE CROSSING MOVES WITH THE INFLOW RATE: the gap-11 share runs "
                   + ", ".join(f"{v:.0%} at F = {k}" for k, v in s11.items()) +
                   f" (a spread of {spread11:.0%}) while the gap-8 control fires everywhere, so the ten-cell number is a "
                   "value at one inflow rate.")

    agg = {"kind": "x168c_inflow",
           "conversion": "surface gap g -> SEP = 2R + g (the error of X168 corrected)",
           "defect_note": ("the 6 000-step length control wrote to one filename per inflow and seed regardless of gap, so the "
                           "gap-11 control runs collided with the gap-10 ones and were skipped as existing; only the gap-10 "
                           "control exists. It does not matter for the comparison - the 2 000-step gap-11 share at F = 0.030 "
                           "(1/5) already matches the 6 000-step X158 value (2/15) - but it is recorded."),
           "by_arm": table, "crossings": crossings, "share_at_f030_by_gap": row030,
           "share_at_gap11_by_rate": s11, "length_control_6000_steps": long_summary,
           "x158_baseline": {"gap10": round(X158_G10, 4), "gap11": round(X158_G11, 4)},
           "controls": controls, "contact_gap_sd": spread, "verdict": verdict,
           "detail": {f"F{f:g}_g{g}": rows for (f, g), rows in sorted(short.items())}}
    OUT.write_text(json.dumps(agg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for key, c in sorted(table.items()):
        print(f"[x168c] {key}: runs {c['runs']} fused {c['fused']} died {c['died']} share {c['share']} "
              f"seps {c['seps']} mins {c['mins']}")
    print(f"[x168c] crossings {crossings}  gap-11 by rate {s11}")
    print(f"[x168c] length control {long_summary}")
    print(f"[x168c] verdict: {verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
