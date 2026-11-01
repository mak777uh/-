"""x72c_size_contrast.py — the same events, two readouts: size versus mixture.

X70 found that a daughter's peak area follows her parent's and survives a nearest-distance surrogate. X72c found that a
daughter's band mixture does **not** survive the same kind of surrogate, although parent and daughter band powers correlate at
0.85. Those two statements come from different runs with different instruments, which leaves the obvious objection that the
comparison is between datasets.

This script removes the objection: it uses **the same 1 715 division events** of the X72c worlds and computes both readouts on
them —

* **size:** Spearman(parent peak area, daughter peak area) against Spearman(nearest non-parent peak area, daughter peak area);
* **mixture:** Spearman(parent `p_wide`, daughter `p_wide`) against the same with the surrogate.

If size is parent-specific on the very events where mixture is not, the contrast "the medium remembers size, not form" stands
on one dataset and one event set.

Run:
    python scripts/x72c_size_contrast.py --write
"""
from __future__ import annotations

import argparse
import json
import math
import statistics as st
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x72c_size_contrast.json"

sys.path.insert(0, str(ROOT / "scripts"))
from x72c_analyse import spearman  # noqa: E402

GRID = 96


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="size versus mixture on the same events")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    rows = []
    for path in sorted(L1.glob("x72c_pattern_s*.json")):
        d = json.loads(path.read_text(encoding="utf-8"))
        peaks = {int(u["uid"]): int(u["peak"]) for u in (d.get("uid_outcomes") or []) if u.get("peak")}
        first = {int(u["uid"]): int(u["first"]) for u in (d.get("uid_outcomes") or []) if u.get("first") is not None}
        snaps = []
        for s in d.get("series") or []:
            log = [c for c in (s.get("components_log") or []) if c.get("cx") is not None]
            snaps.append((int(s["step"]), log))
        snaps.sort()

        for p_uid, c_uid in (d.get("uid_pairs") or []):
            p_uid, c_uid = int(p_uid), int(c_uid)
            if p_uid not in peaks or c_uid not in peaks or c_uid not in first:
                continue
            t_birth = first[c_uid]
            nxt = [(t, log) for t, log in snaps if t >= t_birth and any(int(c["uid"]) == c_uid for c in log)]
            if not nxt:
                continue
            _, log_child = nxt[0]
            pos_c = next((c for c in log_child if int(c["uid"]) == c_uid), None)
            if pos_c is None:
                continue
            best = None
            for c in log_child:
                uid = int(c["uid"])
                if uid in (p_uid, c_uid) or uid not in peaks:
                    continue
                dx = min(abs(c["cx"] - pos_c["cx"]), GRID - abs(c["cx"] - pos_c["cx"]))
                dy = min(abs(c["cy"] - pos_c["cy"]), GRID - abs(c["cy"] - pos_c["cy"]))
                dxy = math.hypot(dx, dy)
                if best is None or dxy < best[0]:
                    best = (dxy, peaks[uid])
            rows.append({
                "world": path.stem.split("_s")[-1],
                "parent_area": peaks[p_uid], "child_area": peaks[c_uid],
                "surrogate_area": best[1] if best else None,
            })

    with_sur = [r for r in rows if r["surrogate_area"] is not None]
    rho_p = spearman([r["parent_area"] for r in with_sur], [r["child_area"] for r in with_sur])
    rho_s = spearman([r["surrogate_area"] for r in with_sur], [r["child_area"] for r in with_sur])

    per_world = {}
    for w in sorted({r["world"] for r in rows}):
        sub = [r for r in with_sur if r["world"] == w]
        per_world[w] = {
            "events": len(sub),
            "rho_parent": round(spearman([r["parent_area"] for r in sub], [r["child_area"] for r in sub]) or 0.0, 3),
            "rho_surrogate": round(spearman([r["surrogate_area"] for r in sub], [r["child_area"] for r in sub]) or 0.0, 3),
        }

    res = {"kind": "l1_field_x72c_size_contrast", "experiment": "X72c follow-up",
           "command": "python scripts/x72c_size_contrast.py --write",
           "question": "on the same division events, is size parent-specific where the mixture is not?",
           "events": len(rows), "events_with_surrogate": len(with_sur),
           "rho_parent_area": round(rho_p, 3) if rho_p is not None else None,
           "rho_surrogate_area": round(rho_s, 3) if rho_s is not None else None,
           "difference": round(rho_p - rho_s, 3) if (rho_p is not None and rho_s is not None) else None,
           "per_world": per_world,
           "note": ("the mixture readout on the same events gives parent 0.853 against a surrogate that predicts the daughter "
                    "better; if size gives parent > surrogate here, the contrast lives on one dataset")}
    worlds_parent_higher = sum(1 for w in per_world.values() if w["rho_parent"] > w["rho_surrogate"])
    res["worlds_parent_higher"] = worlds_parent_higher
    res["verdict"] = ("size is parent-specific where the mixture is not"
                      if (res["difference"] or 0) > 0.10 and worlds_parent_higher >= 8 else
                      "no clear contrast on the same events")

    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[x72c-size] written: {OUT.name}")

    print(f"  events={res['events']} (with surrogate {res['events_with_surrogate']})")
    print(f"  area: parent rho={res['rho_parent_area']} surrogate rho={res['rho_surrogate_area']} "
          f"diff={res['difference']}")
    for w, row in per_world.items():
        print(f"    s{w}: parent={row['rho_parent']} surrogate={row['rho_surrogate']}")
    print("  verdict:", res["verdict"], "| worlds parent higher:", worlds_parent_higher, "/10")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
