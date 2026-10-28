"""additivity_interaction.py — взаимодействие двух механизмов на парных сидах.

Зачем. Агрегат одной серии (например `w2bud_additivity`) содержит только два плеча и **не может** судить
о взаимодействии: для `I = ln E11 − ln E10 − ln E01 + ln E00` нужны четыре ячейки, две из которых лежат
в другой серии (`w2bud_async`), но сняты на **тех же сидах**. Поэтому взаимодействие считается отдельным
инструментом и лежит отдельным файлом, а не подменяет критерий чужой серии (замечание доски B-090).

Все четыре ячейки задаются шаблонами glob; величина `1/Σp²` считается по `summary.type_counts`.

Использование:
    python scripts/additivity_interaction.py \
      --cell00 "morphogenesis/.../w2bud_async_cellp10_seed*.json" \
      --cell10 "morphogenesis/.../w2bud_async_cellp05_seed*.json" \
      --cell01 "morphogenesis/.../w2bud_add_cellp10kw_seed*.json" \
      --cell11 "morphogenesis/.../w2bud_add_cellp05kw_seed*.json" \
      --out morphogenesis/experiments/E09_pond/w2bud_additivity_interaction.json
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import random
import statistics as st
from pathlib import Path


def effective_lineages(path: Path) -> tuple[float | None, int | None]:
    s = json.loads(path.read_text(encoding="utf-8")).get("summary") or {}
    cells = {str(k).lstrip("T"): int(v) for k, v in (s.get("type_counts") or {}).items()}
    tot = sum(cells.values()) or 0
    p = [v / tot for v in cells.values() if v > 0] if tot else []
    return ((1.0 / sum(x * x for x in p)) if p else None), (tot or None)


def load(pattern: str) -> dict[int, tuple[float, int | None]]:
    out = {}
    for f in sorted(glob.glob(pattern)):
        seed = int(Path(f).stem.split("seed")[-1])
        eff, census = effective_lineages(Path(f))
        if eff is not None:
            out[seed] = (eff, census)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--cell00", required=True, help="ни одного механизма")
    ap.add_argument("--cell10", required=True, help="только асинхронность")
    ap.add_argument("--cell01", required=True, help="только смертность по доле")
    ap.add_argument("--cell11", required=True, help="оба механизма")
    ap.add_argument("--boot", type=int, default=4000)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    cells = {"E00": load(args.cell00), "E10": load(args.cell10),
             "E01": load(args.cell01), "E11": load(args.cell11)}
    seeds = sorted(set.intersection(*(set(v) for v in cells.values())))
    if not seeds:
        print("[interaction] нет общих сидов во всех четырёх ячейках")
        return 1

    I = [math.log(cells["E11"][s][0]) - math.log(cells["E10"][s][0])
         - math.log(cells["E01"][s][0]) + math.log(cells["E00"][s][0]) for s in seeds]
    rnd = random.Random(args.seed)
    boots = sorted(st.median([I[rnd.randrange(len(I))] for _ in I]) for _ in range(args.boot))
    lo, hi = boots[int(0.025 * args.boot)], boots[int(0.975 * args.boot) - 1]
    med = {"E00": st.median([cells["E00"][s][0] for s in seeds]),
           "E10": st.median([cells["E10"][s][0] for s in seeds]),
           "E01": st.median([cells["E01"][s][0] for s in seeds]),
           "E11": st.median([cells["E11"][s][0] for s in seeds])}
    predicted = med["E10"] * med["E01"] / med["E00"] if med["E00"] else None

    out = {
        "kind": "additivity-interaction",
        "metric": {
            "effective_lineages": "1/Σp² по живым клеткам (обратный индекс Симпсона)",
            "interaction": "I = ln E11 − ln E10 − ln E01 + ln E00 (лог-шкала; 0 = аддитивность, "
                           "<0 = насыщение, >0 = синергия)",
            "ci": "bootstrap медианы по парным сидам, фиксированный seed",
        },
        "cells": {k: {"runs": len(v), "median_effective_lineages": round(st.median([x[0] for x in v.values()]), 3),
                      "pattern": p} for (k, v), p in zip(cells.items(),
                                                          (args.cell00, args.cell10, args.cell01, args.cell11))},
        "paired_seeds": len(seeds),
        "seeds": seeds,
        "interaction": {"median": round(st.median(I), 4), "ci_low": round(lo, 4), "ci_high": round(hi, 4),
                        "positive": sum(1 for x in I if x > 0), "n": len(I),
                        "half_width": round((hi - lo) / 2, 4)},
        "additive_prediction": round(predicted, 3) if predicted else None,
        "observed_E11": round(med["E11"], 3),
        "verdict": {
            "criterion_kind": "interaction",
            "criterion": "95 % ДИ взаимодействия целиком > 0 ⇒ синергия; целиком < 0 ⇒ насыщение; "
                         "содержит 0 ⇒ аддитивность; полуширина > 0.7 ⇒ величина неизмерима",
            "synergy": bool(lo > 0),
            "saturation": bool(hi < 0),
            "additive": bool(lo <= 0 <= hi),
            "measurable": bool((hi - lo) / 2 <= 0.7),
        },
    }
    text = json.dumps(out, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8", newline="\n")
    print(f"[interaction] парных сидов {out['paired_seeds']} | медианы: "
          + ", ".join(f"{k} {v:.2f}" for k, v in med.items()))
    print(f"  аддитивное предсказание E11 = {out['additive_prediction']}, наблюдено {out['observed_E11']}")
    print(f"  I: медиана {out['interaction']['median']:+.3f} | 95 % ДИ "
          f"[{out['interaction']['ci_low']:+.3f}, {out['interaction']['ci_high']:+.3f}] | "
          f"положительных {out['interaction']['positive']}/{out['interaction']['n']}")
    v = out["verdict"]
    label = "СИНЕРГИЯ" if v["synergy"] else ("насыщение" if v["saturation"] else "аддитивность")
    print(f"  вердикт: {label}" + ("" if v["measurable"] else " (но величина не измерима: полуширина > 0.7)"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
