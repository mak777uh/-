"""x70_analyse.py — size heredity: does a daughter's peak area follow its parent's?

Pooled over seeds within an arm: correlation and regression slope of daughter peak area on parent peak area, using
`uid_pairs` (parent uid, daughter uid) and `uid_outcomes` (peak area per uid).

Bands, pre-declared in `reports/2026-11-01-x70-size-heredity-plan.md`:

    corr >= 0.5 and slope >= 0.6   -> the medium carries size heredity
    corr < 0.3 or slope < 0.5      -> sizes regress to the medium's own scale
    otherwise                      -> intermediate, reported as such

Run:
    python scripts/x70_analyse.py --write
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import statistics as st
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x70_size.json"

ARMS = ("pattern", "homog")


PREFIX = "x70"


def pairs_for_arm(arm: str) -> tuple[list[tuple[float, float]], int, int]:
    xs, ys = [], []
    events = 0
    paired = 0
    for f in sorted(glob.glob(str(L1 / f"{PREFIX}_{arm}_s*.json"))):
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        peaks = {int(u["uid"]): int(u["peak"]) for u in (d.get("uid_outcomes") or []) if u.get("peak")}
        uid_pairs = d.get("uid_pairs") or []
        events += len(uid_pairs)
        for parent_uid, child_uid in uid_pairs:
            xp = peaks.get(int(parent_uid))
            yc = peaks.get(int(child_uid))
            if xp and yc:
                xs.append(float(xp))
                ys.append(float(yc))
                paired += 1
    return list(zip(xs, ys)), events, paired


def stats(pairs: list[tuple[float, float]]) -> dict | None:
    if len(pairs) < 5:
        return None
    xs = [p for p, _ in pairs]
    ys = [q for _, q in pairs]
    mx, my = st.mean(xs), st.mean(ys)
    sx = st.pstdev(xs)
    sy = st.pstdev(ys)
    if not sx or not sy:
        return None
    cov = sum((x - mx) * (y - my) for x, y in pairs) / len(pairs)
    return {"n": len(pairs), "corr": round(cov / (sx * sy), 3), "slope": round(cov / (sx * sx), 3),
            "parent_median": round(st.median(xs), 1), "daughter_median": round(st.median(ys), 1)}


def shuffle_null(arm: str, n_perm: int = 200, seed: int = 7) -> dict | None:
    """Нулевая модель: пары родитель-дочь перемешиваются внутри прогона.

    Если наблюдённая корреляция не превышает нулевую, она объясняется тем, что все структуры
    в этом мире похожи по размеру, а не тем, что дочь похожа на своего родителя.
    """
    import random

    per_run = []
    for f in sorted(glob.glob(str(L1 / f"{PREFIX}_{arm}_s*.json"))):
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        peaks = {int(u["uid"]): int(u["peak"]) for u in (d.get("uid_outcomes") or []) if u.get("peak")}
        rows = [(peaks[int(a)], peaks[int(b)]) for a, b in (d.get("uid_pairs") or [])
                if int(a) in peaks and int(b) in peaks]
        if rows:
            per_run.append(rows)
    if not per_run:
        return None
    rng = random.Random(seed)
    obs = stats([p for run in per_run for p in run])
    if not obs:
        return None
    nulls = []
    for _ in range(n_perm):
        sample = []
        for run in per_run:
            parents = [x for x, _ in run]
            daughters = [y for _, y in run]
            rng.shuffle(parents)
            sample.extend(zip(parents, daughters))
        s = stats(sample)
        if s:
            nulls.append(s["corr"])
    if not nulls:
        return None
    nulls.sort()
    return {"observed_corr": obs["corr"], "null_median": round(st.median(nulls), 3),
            "null_p95": round(nulls[int(0.95 * len(nulls)) - 1], 3),
            "exceeds_null": obs["corr"] > nulls[int(0.95 * len(nulls)) - 1],
            "n_perm": len(nulls)}


def per_world(arm: str, n_perm: int = 2000, seed: int = 9) -> list[dict]:
    """Per-world numbers and a per-world pairing null.

    A world is the unit: pooling across worlds mixes between-world size differences into the correlation, so the pooled
    number is reported but never quoted alone.
    """
    import random

    rng = random.Random(seed)
    rows = []
    for f in sorted(glob.glob(str(L1 / f"{PREFIX}_{arm}_s*.json"))):
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        peaks = {int(u["uid"]): int(u["peak"]) for u in (d.get("uid_outcomes") or []) if u.get("peak")}
        pairs = [(peaks[int(a)], peaks[int(b)]) for a, b in (d.get("uid_pairs") or [])
                 if int(a) in peaks and int(b) in peaks]
        s = stats(pairs)
        null = None
        if pairs:
            parents = [x for x, _ in pairs]
            daughters = [y for _, y in pairs]
            draws = []
            for _ in range(n_perm):
                rng.shuffle(parents)
                z = stats(list(zip(parents, daughters)))
                if z:
                    draws.append(z["corr"])
            if draws:
                draws.sort()
                null = {"p95": round(draws[int(0.95 * len(draws)) - 1], 3),
                        "median": round(st.median(draws), 3), "n_perm": len(draws)}
        rows.append({"file": Path(f).name, "stats": s, "shuffle_null": null})
    return rows


def main(argv=None) -> int:
    global PREFIX, OUT
    ap = argparse.ArgumentParser(description="X70 size heredity")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--prefix", default="x70", help="artifact prefix: x70 (one world copied), x70r (five worlds)")
    ap.add_argument("--out", default=None, help="aggregate path; default follows the prefix")
    args = ap.parse_args(argv)
    PREFIX = args.prefix
    if args.out:
        OUT = Path(args.out)
    elif PREFIX != "x70":
        OUT = OUT.with_name(f"l1_field_{PREFIX}_size.json")

    out = {"kind": f"l1_field_{PREFIX}_size", "experiment": "X70",
           "command": f"python scripts/x70_analyse.py --write --prefix {PREFIX}",
           "prefix": PREFIX,
           "prereg": "reports/2026-11-01-x70-size-heredity-plan.md",
           "arms": {}, "not_claimed": [
               "five seeds per arm, pooled events, no p-values",
               "peak area is a thresholded quantity and moves with the threshold",
               "the daughter's own peak may occur after it has already split again, which biases the slope downward",
           ]}
    for arm in ARMS:
        pairs, events, paired = pairs_for_arm(arm)
        s = stats(pairs)
        out["arms"][arm] = {"events": events, "paired_events": paired, "stats": s,
                            "shuffle_null": shuffle_null(arm), "per_world": per_world(arm)}
        if s:
            if s["corr"] >= 0.5 and s["slope"] >= 0.6:
                out["arms"][arm]["verdict"] = "medium carries size heredity"
            elif s["corr"] < 0.3 or s["slope"] < 0.5:
                out["arms"][arm]["verdict"] = "sizes regress to the medium's scale"
            else:
                out["arms"][arm]["verdict"] = "intermediate"

    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[x70] written: {OUT.name}")
    for arm, a in out["arms"].items():
        s = a["stats"]
        print("  %-8s events=%4d paired=%4d  %s" % (
            arm, a["events"], a["paired_events"],
            ("corr=%.3f slope=%.3f  n=%d  %s" % (s["corr"], s["slope"], s["n"], a["verdict"])) if s else "not estimable"))
        nu = a.get("shuffle_null")
        if nu:
            print("           null: median %.3f, p95 %.3f -> exceeds: %s" % (nu["null_median"], nu["null_p95"], nu["exceeds_null"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
