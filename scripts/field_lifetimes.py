"""field_lifetimes.py — времена жизни структур: числа статьи 028 §4.9 из артефактов.

Почему отдельный скрипт. Библиотекарь (аудит 31.10) заметил и был прав: числа «долгоживущих 1.3 против 1.2»,
«медиана жизни 57 против 4046», «пик площади 97 против 4575», «75 % / 24 %» стояли в статье без артефакта в
репозитории и без команды. Код учёта `uid` в `field_track.py` был, а результаты лежали вне git — то есть
**главный вывод линии не воспроизводился**. Здесь эти числа считаются из артефактов и пишутся в агрегат.

Дизайн (фиксирован): прогоны `x23_{static,homog}_s{171..180}` — по 10 сидов на плечо, 6000 шагов, срез каждые
500. Прогоны с сидами 181–200 — отдельный добор (`X25`), в этот агрегат **не входят** и перечислены как
исключённые: иначе медианы смещаются (54 вместо 57 и 132 вместо 97 при 24 файлах).

Запуск:
    python scripts/field_lifetimes.py --write     # пересобрать агрегат
    python scripts/field_lifetimes.py             # только напечатать числа
"""
from __future__ import annotations

import argparse
import glob
import json
import statistics as st
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "morphogenesis" / "experiments" / "L1_field"
OUT = SRC / "lifetimes_matrix.json"

SEEDS = list(range(171, 181))          # дизайн статьи
DURABLE = 1500                          # порог «долгоживущей» структуры, шагов


def collect(arm: str) -> dict:
    life: list[int] = []
    durable_per_run: list[int] = []
    total_per_run: list[int] = []
    peaks: list[int] = []
    files: list[str] = []
    for seed in SEEDS:
        f = SRC / f"x23_{arm}_s{seed}.json"
        if not f.exists():
            continue
        d = json.loads(f.read_text(encoding="utf-8"))
        lt = d.get("lifetimes") or {}
        ls = lt.get("life_steps") or []
        if not ls:
            continue
        files.append(f.name)
        life.extend(ls)
        durable_per_run.append(sum(1 for x in ls if x >= DURABLE))
        total_per_run.append(len(ls))
        peaks.extend(lt.get("peak_sizes") or [])
    if not life:
        return {"n_files": 0}
    return {
        "n_files": len(files),
        "files": files,
        "uids_total": len(life),
        "median_life_steps": int(st.median(life)),
        "durable_per_run": round(st.mean(durable_per_run), 2),
        "ephemeral_per_run": round(st.mean([t - d for t, d in zip(total_per_run, durable_per_run)]), 2),
        "structures_per_run": round(st.mean(total_per_run), 2),
        "median_peak_size": int(st.median(peaks)) if peaks else None,
        "share_durable": round(sum(1 for x in life if x >= DURABLE) / len(life), 3),
        "share_short": round(sum(1 for x in life if x <= 500) / len(life), 3),
    }


def build() -> dict:
    arms = {arm: collect(arm) for arm in ("static", "homog")}
    extra = sorted(p.name for p in SRC.glob("x23_*_s1[89]*.json"))
    return {
        "kind": "lifetimes_matrix",
        "experiment": "X23",
        "command": "python scripts/field_lifetimes.py --write",
        "metric": {
            "median_life_steps": "медиана времени жизни структуры (uid), шагов",
            "durable_per_run": f"структур на прогон, живущих >= {DURABLE} шагов",
            "ephemeral_per_run": "структур на прогон, живущих меньше порога",
            "median_peak_size": "медиана пиковой площади структуры, клеток",
            "share_durable": "доля структур с жизнью >= порога (по всем структурам всех прогонов)",
            "share_short": "доля структур с жизнью <= 500 шагов",
        },
        "design": {"seeds": SEEDS, "durable_threshold": DURABLE, "sample_every": 500,
                   "note": "по 10 сидов на плечо; доборы с сидами 181–200 в агрегат не входят"},
        "by_arm": arms,
        "excluded_files": extra,
        "contrast": {
            "durable_static": arms["static"].get("durable_per_run"),
            "durable_homog": arms["homog"].get("durable_per_run"),
            "median_life_static": arms["static"].get("median_life_steps"),
            "median_life_homog": arms["homog"].get("median_life_steps"),
        },
        "not_claimed": [
            "«долгоживущая» = пережившая 1500 шагов из 6000; порог выбран как четверть прогона",
            "uid наследуется по перекрытию >= 0.5, поэтому слияния считаются продолжением одной структуры",
            "время жизни короче 500 шагов не разрешается (срез каждые 500)",
        ],
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="времена жизни структур")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    data = build()
    if args.write:
        OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[lifetimes] записано: {OUT.name}")
    for arm, v in data["by_arm"].items():
        print(f"  {arm}: файлов {v.get('n_files')}, медиана жизни {v.get('median_life_steps')}, "
              f"долгоживущих {v.get('durable_per_run')}, коротких {v.get('ephemeral_per_run')}, "
              f"пик {v.get('median_peak_size')}, доля >= {DURABLE}: {v.get('share_durable')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
