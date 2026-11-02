"""Helpers for reading the committed `.compact.json` projections of the dense series.

The full dense logs (2-4 MB per run) were deleted from local disk on 03.11 to relieve a full host disk; they were never committed. What survives in
git is the projection written by `scripts/compact_field_series.py`: params, uid_pairs, and per logged step [uid, area, cx, cy]. That is enough to
rebuild every field this line's log-only analyses use — peaks, first appearances, lifetimes and genealogies — so the reader lives here rather than
in each script.
"""
from __future__ import annotations

import json
from pathlib import Path


def world_from_compact(path: Path) -> dict:
    d = json.loads(path.read_text(encoding="utf-8"))
    peak: dict[int, dict] = {}
    first: dict[int, dict] = {}
    per_step: dict[int, list[dict]] = {}
    life: dict[int, int] = {}
    for step, comps in d.get("series") or []:
        step = int(step)
        rows = []
        for uid, area, cx, cy in comps:
            uid = int(uid)
            row = {"uid": uid, "area": float(area or 0.0), "cx": cx, "cy": cy}
            rows.append(row)
            if uid not in first:
                first[uid] = {"step": step, "cx": cx, "cy": cy}
            last = life.get(uid, (step, step))
            life[uid] = (last[0], step)
            if uid not in peak or (area or 0) > (peak[uid].get("area") or 0):
                peak[uid] = {"area": float(area or 0.0), "cx": cx, "cy": cy, "step": step}
        per_step[step] = rows
    # lifetime in logged steps: last appearance minus first
    lifetime = {uid: (v[1] - v[0] + 1) for uid, v in life.items()}
    parent = {int(b): int(a) for a, b in (d.get("uid_pairs") or [])}
    return {"peak": peak, "first": first, "per_step": per_step, "parent": parent, "life": lifetime,
            "params": d.get("params") or {}}
