"""Build x160_memory_matrix.json from the x160_memory series (63 artifacts, 3 arms x 20 seeds).

Closes two red gates at once:
  - check_series_followthrough: "x160_memory — агрегата нет (63 артефактов)"
  - check_aggregate_coverage: "СЕРИЯ БЕЗ АГРЕГАТА x160_memory/x160_{const,real,surrogate}_t300_s"

Arms (from file names `x160_<arm>_t300_s<seed>.json`): const | real | surrogate.
Reads only `summary` fields that exist in the artifacts; nothing is invented.
"""
from __future__ import annotations
import json, os, re, statistics

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SERIES = os.path.join(_ROOT, "morphogenesis", "experiments", "E09_pond", "x160_memory")
_OUT = os.path.join(_ROOT, "morphogenesis", "experiments", "E09_pond", "x160_memory_matrix.json")

FIELDS = ["pop_time", "final_resource_mean", "final_resource_alive_mean",
          "clonal_fraction", "mobility_moves", "plastic_moves", "organism_moves",
          "learn_updates", "learn_useless", "invade_at"]
PAT = re.compile(r"^x160_(?P<arm>const|real|surrogate)_t300_s(?P<seed>\d+)\.json$")


def main() -> int:
    rows = []
    per_arm: dict[str, list[dict]] = {}
    for name in sorted(os.listdir(_SERIES)):
        m = PAT.match(name)
        if not m:
            continue
        with open(os.path.join(_SERIES, name), encoding="utf-8") as fh:
            art = json.load(fh)
        s = art.get("summary", {})
        rec = {"arm": m.group("arm"), "seed": int(m.group("seed")),
               "steps": s.get("steps"),
               # coverage gate (check_aggregate_coverage.py) links artifacts to aggregates
               # through row["artifact"]; without it the series looks "without aggregate".
               "artifact": f"x160_memory/{name}"}
        for f in FIELDS:
            rec[f] = s.get(f)
        rows.append(rec)
        per_arm.setdefault(rec["arm"], []).append(rec)

    agg = []
    for arm in ("const", "real", "surrogate"):
        rs = per_arm.get(arm, [])
        if not rs:
            continue
        entry = {"arm": arm, "n": len(rs)}
        for f in FIELDS:
            vals = [r[f] for r in rs if isinstance(r.get(f), (int, float))]
            if vals:
                entry[f] = {"median": statistics.median(vals),
                            "mean": round(sum(vals) / len(vals), 4),
                            "min": min(vals), "max": max(vals)}
            else:
                entry[f] = None
        agg.append(entry)

    out = {
        "experiment": "E09_pond_x160_memory",
        "metric": "pop_time + resource/mobility counters",
        "note": ("Собрано из 63 артефактов серии x160_memory (3 плеча x 20 сидов + 3 stream-файла). "
                 "Числа взяты из summary артефактов, ничего не досчитано. "
                 "Серия снята на двух коммитах кода (cbbd0f7a x49, 660fe5e9 x11) — "
                 "парное сравнение плеч внутри одного плеча однородно по сидам, но "
                 "межплечевые различия требуют сверки коммитов (см. homogeneity)."),
        "kind": "x160_memory_matrix",
        "source_dir": "morphogenesis/experiments/E09_pond/x160_memory",
        "n_artifacts": len(rows),
        "rows": rows,          # per-run rows: coverage gate reads row["artifact"] here
        "arms": agg,           # per-arm medians/means (NOT in "rows": the gate expects artifacts there)
        "not_claimed": ["межплечевое сравнение без сверки коммитов cbbd0f7a/660fe5e9"],
        "not_claimed_source": "check_series_homogeneity.py (E09_pond/x160_memory: 2 коммита)",
        "per_seed": rows,
    }
    with open(_OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(f"[x160_memory_matrix] written {_OUT}: {len(rows)} artifacts, arms: "
          f"{[a['arm'] + '=' + str(a['n']) for a in agg]}")
    for a in agg:
        pt = a.get("pop_time")
        print(f"  {a['arm']:10s} n={a['n']:2d} pop_time median={pt['median'] if pt else None}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
