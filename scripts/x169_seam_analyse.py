"""x169_seam_analyse.py — X169: is there a seam in the field after a fusion?

For each field dump, the profile v(s) is sampled along the segment joining the two original parent centres (20 points), and
the bimodality index is min(profile between the outermost local maxima) / max(outermost local maxima). Near 1 = one smooth
bump; well below 1 = two centres with a saddle.

The parent centres are taken from the run's first logged step (the two seeded discs), and the segment is measured in the
periodic metric, so the sampling does not care where the pair was placed.

Writes morphogenesis/experiments/E09_pond/l1_field_x169_seam.json.
"""
from __future__ import annotations

import json
import math
import statistics
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
FIELDS = ROOT / "_hourly" / "x169_fields"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x169_seam.json"
SAMPLES = 20
CONTROL_MIN = 0.9


def comps(row):
    if isinstance(row, dict):
        return row.get("components_log") or []
    return []


def profile_at(v: np.ndarray, p0, p1, grid: int, n: int = SAMPLES):
    g = v.shape[0]
    out = []
    for i in range(n):
        t = i / (n - 1)
        x = p0[0] + t * (p1[0] - p0[0])
        y = p0[1] + t * (p1[1] - p0[1])
        xi, yi = int(round(x)) % g, int(round(y)) % g
        out.append(float(v[yi, xi]))
    return out


def bimodality(prof: list[float]) -> float | None:
    """Central dip: the field at the middle third of the parents' segment, relative to the profile's peak.

    The first version looked for the outermost local maxima and divided the saddle between them by the larger one. On a
    unimodal hump those maxima land on the shoulders of the same hump, the control reads 0.05 and the measure has no headroom.
    The central dip asks the item's actual question and behaves as a control should.
    """
    n = len(prof)
    if n < 8:
        return None
    peak = max(prof)
    if peak <= 1e-6:
        return None
    lo, hi = int(n * 1 / 3), int(math.ceil(n * 2 / 3))
    return round(min(prof[lo:hi]) / peak, 4)


def run_profiles(arm: str, seed: int, art: dict) -> list[dict]:
    series = art.get("series") or []
    if not series:
        return []
    first = comps(series[0])
    if arm == "pair" and len(first) >= 2:
        first = sorted(first, key=lambda c: c["cx"])
        p0 = (first[0]["cx"], first[0]["cy"])
        p1 = (first[-1]["cx"], first[-1]["cy"])
    else:
        c = first[0]
        r = math.sqrt(max(c["area"], 1.0) / math.pi)
        # an arbitrary diameter of the single body, the same length as the pair's segment
        p0 = (c["cx"] - SEP_HALF, c["cy"])
        p1 = (c["cx"] + SEP_HALF, c["cy"])
    steps = {int(r.get("step")): len(comps(r)) for r in series if r.get("step") is not None}
    rows = []
    for f in sorted(FIELDS.joinpath(f"{arm}_s{seed}").glob("*.npy")):
        step = int(f.stem.split("_t")[-1])
        v = np.load(f)
        if v.ndim == 3:
            v = v[0]
        prof = profile_at(v, p0, p1, v.shape[0])
        rows.append({"step": step, "components": steps.get(step), "bimodality": bimodality(prof),
                     "peak": round(max(prof), 4)})
    return rows


SEP_HALF = 7.0


def main() -> int:
    arms: dict[str, dict[int, list[dict]]] = {"pair": {}, "single": {}}
    for arm in ("pair", "single"):
        for f in sorted(L1.glob(f"x169_{arm}_s99*.json")):
            if f.name.endswith(".compact.json"):
                continue
            seed = int(f.stem.split("_s")[-1])
            art = json.loads(f.read_text(encoding="utf-8"))
            rows = run_profiles(arm, seed, art)
            if rows:
                arms[arm][seed] = rows

    def collect(arm: str, pred) -> list[float]:
        return [r["bimodality"] for rows in arms[arm].values() for r in rows
                if r["bimodality"] is not None and pred(r)]

    control = collect("single", lambda r: True)
    control_min = min(control) if control else None
    post = collect("pair", lambda r: r["components"] == 1)
    pre = collect("pair", lambda r: (r["components"] or 0) >= 2)
    control_ok = control_min is not None and control_min >= CONTROL_MIN
    all_post = [r["bimodality"] for rows in arms["pair"].values() for r in rows if r["bimodality"] is not None]
    spread = round(statistics.pstdev(all_post), 4) if len(all_post) > 1 else None
    readout_ok = spread is not None and spread >= 0.03

    med_control = statistics.median(control) if control else None
    med_post = statistics.median(post) if post else None
    med_pre = statistics.median(pre) if pre else None
    if not control_ok:
        verdict = (f"NOT REPORTABLE: the single-body control's bimodality index reaches {control_min}, below the 0.9 floor, so "
                   f"the measure has no headroom and cannot distinguish a seam from its own noise.")
    elif not readout_ok or med_post is None:
        verdict = "NOT REPORTABLE: the index does not vary across dumps, or the pair never reached a one-component step."
    elif med_post >= med_control - 0.1:
        verdict = (f"THE SEAM IS GONE: after the fusion the profile along the parents' axis is as flat-topped as a single "
                   f"body's (bimodality {med_post:.2f} against the control's {med_control:.2f}), so the merged body is one bump "
                   f"and the merge erases the pair's structure.")
    else:
        verdict = (f"THE SEAM SURVIVES: after the fusion the profile still carries a saddle between the parents' positions "
                   f"(bimodality {med_post:.2f} against a single body's {med_control:.2f}), so the merged body retains two "
                   f"centres and the fusion preserves the pair's structure at the level of the field.")

    trajectories = {f"{arm}_s{s}": [{"step": r["step"], "components": r["components"], "bimodality": r["bimodality"]}
                                    for r in rows] for arm, seeds in arms.items() for s, rows in seeds.items()}
    agg = {"kind": "x169_seam", "samples_per_profile": SAMPLES,
           "control_floor": CONTROL_MIN, "control_min": control_min,
           "measure_note": ("central dip, not the pre-registered saddle-between-outermost-maxima: the pre-registered index is "
                            "degenerate on a unimodal profile (the control read 0.047, no headroom) because the outermost "
                            "local maxima land on the shoulders of the same hump. The replacement was made after the fields "
                            "were dumped and before any pair number was read; the control check is unchanged."),
           "median_control": med_control, "median_pair_two_body": med_pre, "median_pair_one_body": med_post,
           "pair_one_body_values": post, "controls": {"positive_control_fires": control_ok, "readout_varies": readout_ok},
           "index_sd": spread, "verdict": verdict, "trajectories": trajectories}
    OUT.write_text(json.dumps(agg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"[x169] control min {control_min} median {med_control}")
    print(f"[x169] pair median: two bodies {med_pre}, one body {med_post} (n {len(post)})")
    print(f"[x169] index sd {spread}")
    print(f"[x169] verdict: {verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
