"""x77_patch_control.py — is the size memory parental, or just the local patch? 

X70's control compared a daughter with the **nearest non-parent** structure and the parent won (0.457 vs 0.069). That is a
one-neighbour control; the sharper version of the same objection is that the *patch* — everything within about one wavelength of
the daughter's birth — sets her size, and the parent is merely a member of that patch. This script tests that.

Per division event, at the daughter's birth snapshot:

* `patch_mean` = mean peak area of all structures within radius `R` of the daughter's centroid that are **not ancestors** of
  her (parent, grandparent, …) and not herself;
* `parent_peak` = the parent's peak area, as in X70/X73.

Three statistics, pooled and per world:

1. Spearman(parent, daughter) and Spearman(patch_mean, daughter);
2. a **conditional** comparison: OLS of daughter on (parent, patch_mean) with the coefficient of `parent` and its bootstrap CI —
   if the parent's coefficient survives with the patch in the model, the memory is parental beyond the patch;
3. the same with `patch_mean` replaced by the **nearest non-parent** (the X70 control) for reference.

Criteria: `reports/2026-11-02-x77-patch-plan.md` (registered before this script).

Run:
    python scripts/x77_patch_control.py --write
"""
from __future__ import annotations

import argparse
import json
import math
import random
import statistics as st
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x77_patch.json"

sys.path.insert(0, str(ROOT / "scripts"))
from x72c_analyse import spearman  # noqa: E402

GRID = 96
RADIUS = 12.0     # cells, about one wavelength at this inflow
BOOT = 2000


def world_events(path: Path) -> list[dict]:
    d = json.loads(path.read_text(encoding="utf-8"))
    peaks = {int(u["uid"]): int(u["peak"]) for u in (d.get("uid_outcomes") or []) if u.get("peak")}
    first = {int(u["uid"]): int(u["first"]) for u in (d.get("uid_outcomes") or []) if u.get("first") is not None}
    parent_of = {}
    for p, c in (d.get("uid_pairs") or []):
        parent_of.setdefault(int(c), int(p))
    snaps = []
    for s in d.get("series") or []:
        log = [c for c in (s.get("components_log") or []) if c.get("cx") is not None]
        snaps.append((int(s["step"]), log))
    snaps.sort()

    events = []
    for p_uid, c_uid in (d.get("uid_pairs") or []):
        p_uid, c_uid = int(p_uid), int(c_uid)
        if p_uid not in peaks or c_uid not in peaks or c_uid not in first:
            continue
        t_birth = first[c_uid]
        nxt = [(t, log) for t, log in snaps if t >= t_birth and any(int(c["uid"]) == c_uid for c in log)]
        if not nxt:
            continue
        _, log_child = nxt[0]
        pos = next((c for c in log_child if int(c["uid"]) == c_uid), None)
        if pos is None:
            continue
        chain, cur = set(), c_uid
        while cur is not None:
            chain.add(cur)
            cur = parent_of.get(cur)
        patch, nearest = [], None
        for c in log_child:
            uid = int(c["uid"])
            if uid in chain or uid not in peaks:
                continue
            dx = min(abs(c["cx"] - pos["cx"]), GRID - abs(c["cx"] - pos["cx"]))
            dy = min(abs(c["cy"] - pos["cy"]), GRID - abs(c["cy"] - pos["cy"]))
            dxy = math.hypot(dx, dy)
            if dxy <= RADIUS:
                patch.append(peaks[uid])
            if nearest is None or dxy < nearest[0]:
                nearest = (dxy, peaks[uid])
        if not patch:
            continue
        events.append({"parent": peaks[p_uid], "child": peaks[c_uid],
                       "patch_mean": st.mean(patch), "patch_n": len(patch),
                       "nearest": nearest[1] if nearest else None})
    return events


def ols_beta(y: list[float], x1: list[float], x2: list[float]) -> float | None:
    """Coefficient of x1 in y = a + b1 x1 + b2 x2, by normal equations."""
    n = len(y)
    if n < 10:
        return None
    my, m1, m2 = st.mean(y), st.mean(x1), st.mean(x2)
    yc = [v - my for v in y]
    a = [v - m1 for v in x1]
    b = [v - m2 for v in x2]
    saa = sum(v * v for v in a)
    sbb = sum(v * v for v in b)
    sab = sum(u * v for u, v in zip(a, b))
    say = sum(u * v for u, v in zip(a, yc))
    sby = sum(u * v for u, v in zip(b, yc))
    det = saa * sbb - sab * sab
    if abs(det) < 1e-12:
        return None
    return (say * sbb - sby * sab) / det


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X77 patch control for size memory")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    rng = random.Random(77)

    res = {"kind": "l1_field_x77_patch", "experiment": "X77",
           "command": "python scripts/x77_patch_control.py --write",
           "prereg": "reports/2026-11-02-x77-patch-plan.md",
           "radius_cells": RADIUS, "datasets": {}}

    for name, pattern in (("x72c", "x72c_pattern_s*.json"), ("x70r", "x70r_pattern_s*.json")):
        rows = []
        for path in sorted(L1.glob(pattern)):
            evs = world_events(path)
            rows.extend([dict(e, world=path.stem.split("_s")[-1]) for e in evs])
        par = [float(e["parent"]) for e in rows]
        ch = [float(e["child"]) for e in rows]
        pm = [float(e["patch_mean"]) for e in rows]
        near = [(float(e["nearest"]), float(e["child"])) for e in rows if e["nearest"] is not None]
        beta = ols_beta(ch, par, pm)
        boots = []
        for _ in range(BOOT):
            idx = [rng.randrange(len(rows)) for _ in rows]
            b = ols_beta([ch[i] for i in idx], [par[i] for i in idx], [pm[i] for i in idx])
            if b is not None:
                boots.append(b)
        boots.sort()
        res["datasets"][name] = {
            "events": len(rows),
            "rho_parent": round(spearman(par, ch) or 0.0, 3),
            "rho_patch_mean": round(spearman(pm, ch) or 0.0, 3),
            "rho_nearest": round(spearman([a for a, _ in near], [b for _, b in near]) or 0.0, 3) if near else None,
            "beta_parent_given_patch": round(beta, 6) if beta is not None else None,
            "beta_ci95": [round(boots[int(0.025 * len(boots))], 6), round(boots[int(0.975 * len(boots)) - 1], 6)]
            if len(boots) > 100 else None,
            "patch_size_median": round(st.median([e["patch_n"] for e in rows]), 1),
        }

    d = res["datasets"]["x72c"]
    r = res["datasets"]["x70r"]
    ci = d.get("beta_ci95") or [None, None]
    ci_r = r.get("beta_ci95") or [None, None]
    # Правило из пре-регистрации: контроль обязан иметь силу. Если средний размер соседей не предсказывает дочь,
    # то «контроль на патч» не различает объяснения — вердикт void, а не «родитель побеждает».
    controls = {
        "patch_has_power": (d["rho_patch_mean"] >= 0.20),
        "enough_events": (d["events"] >= 1000 and (d["patch_size_median"] or 0) >= 3),
        "reference_reproduces_x70": (0.00 <= (d["rho_nearest"] or 0.0) <= 0.20),
    }
    res["controls"] = controls
    if not controls["patch_has_power"] or not controls["reference_reproduces_x70"]:
        failed = [k for k, v in controls.items() if not v]
        res["verdict"] = (f"void as a discriminator: control(s) {failed} failed — the patch mean does not predict the daughter, "
                          f"so putting it in the model cannot absorb the parent")
    elif ci[0] is not None and ci[0] > 0 and ci_r[0] is not None and ci_r[0] > 0:
        res["verdict"] = "parent-specific beyond the patch: the parent's coefficient excludes zero in both datasets"
    elif ci[0] is not None and ci[0] > 0:
        res["verdict"] = "inconclusive: primary passes, replication does not"
    else:
        res["verdict"] = "not separable: with the patch mean in the model the parent's coefficient includes zero"
    res["note"] = ("patch_mean replaces the nearest-neighbour control with a local average; the coefficient of the parent is the "
                   "part of the daughter's size that the patch cannot explain")

    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[x77] written: {OUT.name}")

    for name, row in res["datasets"].items():
        print(f"  {name}: events={row['events']} patch_n={row['patch_size_median']} "
              f"rho parent={row['rho_parent']} patch={row['rho_patch_mean']} nearest={row['rho_nearest']} "
              f"beta_parent|patch={row['beta_parent_given_patch']} ci={row['beta_ci95']}")
    print("  verdict:", res["verdict"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
