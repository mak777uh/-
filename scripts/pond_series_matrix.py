"""pond_series_matrix.py — агрегаты серий пруда (habitable, adequacy) с корректными путями.

Зачем. Агрегаты `habitable_matrix.json` и `adequacy_matrix.json` были собраны вручную и лежали внутри каталогов
серий, тогда как гейт `check_series_followthrough` и `aggregate_check --strict` ждут агрегат в **родительском**
каталоге `E09_pond`, а пути в строках — **относительно агрегата**. В результате: (1) гейт «хвосты серий» ругался,
что агрегата нет; (2) после переноса в родитель `aggregate_check` нашёл 25 расхождений, потому что имена файлов не
содержали подкаталога. Здесь агрегаты собираются скриптом, пути пишутся **от корня репозитория** (так их проверяет `aggregate_check`), и оба гейта
проходят.

Запуск:
    python scripts/pond_series_matrix.py --write
    python scripts/pond_series_matrix.py
"""
from __future__ import annotations

import argparse
import glob
import json
import statistics as st
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POND = ROOT / "morphogenesis" / "experiments" / "E09_pond"


def habitable() -> dict:
    rows = []
    for f in sorted((POND / "habitable").glob("x43_hab_s*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))["runs"][0]
        a = d["alive_series"]
        rows.append({"artifact": f.relative_to(ROOT).as_posix(), "seed": d["seed"], "alive_last": a[-1],
                     "alive_max": max(a), "extinct_at": next((i for i, x in enumerate(a) if x == 0), None),
                     "resource_under_alive_last": round((d["E"][-1]["resource_under_alive"] or 0), 3)})
    lasts = [r["alive_last"] for r in rows]
    return {
        "kind": "habitable_matrix", "experiment": "X43",
        "command": "python scripts/pond_series_matrix.py --write",
        "metric": {"alive_last": "живых клеток на последнем шаге (1500)",
                   "extinct_at": "первый шаг с нулём живых"},
        "design": {"income": 0.02, "cost": 0.03, "steps": 1500, "seeds": len(rows)},
        "rows": rows,
        "summary": {"survived": sum(1 for x in lasts if x > 0), "n": len(lasts),
                    "median_alive_last": st.median(lasts) if lasts else None,
                    "min": min(lasts) if lasts else None, "max": max(lasts) if lasts else None},
        "not_claimed": ["один мир и одно правило", "граница между b=0.010 и b=0.020 не уточнена"],
    }


def adequacy() -> dict:
    rows = []
    for f in sorted((POND / "adequacy").glob("x44_*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))["runs"][0]
        a = d["alive_series"]
        rows.append({"artifact": f.relative_to(ROOT).as_posix(), "arm": d["arm"], "seed": d["seed"],
                     "alive_last": a[-1], "alive_max": max(a),
                     "energy_last": round(d["S"][-1]["energy"], 4) if d["S"] else None})
    return {
        "kind": "adequacy_matrix", "experiment": "X44",
        "command": "python scripts/pond_series_matrix.py --write",
        "metric": {"alive_last": "живых на последнем шаге (700)",
                   "energy_last": "средняя энергия живых"},
        "design": {"income": 0.02, "arms": ["cost", "cheap", "free"], "steps": 700,
                   "seeds_per_arm": len(rows) // 3 if rows else 0},
        "rows": rows,
        "summary": {"n": len(rows)},
        "note": ("мера I(Δэнергия; Δресурс) считается отдельно — scripts/adequacy_mi.py; здесь только состав серии"),
        "not_claimed": ["5 сидов на плечо", "агрегат не содержит меры, только ряды и исходы"],
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="агрегаты серий пруда")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    for name, data in (("habitable_matrix.json", habitable()), ("adequacy_matrix.json", adequacy())):
        if args.write:
            (POND / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                                     encoding="utf-8", newline="\n")
            print(f"[pond] записано: {name} | строк {len(data['rows'])}")
        else:
            print(f"  {name}: строк {len(data['rows'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
