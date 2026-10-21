"""E02b: транзиторные классы на карте — встречается ли форма «по пути».

Вопрос к сильному утверждению «struct_2 — выученная морфология»: а не
проходят ли другие модели через эту форму транзиторно, по дороге к своей
смерти или к однородному полю? Если да, то struct_2 — обычная фаза, а её
редкость объясняется тем, что она быстро «уходит». Если нет, форма
принадлежит ровно одной модели.

Источник данных — каноническая перепись `census.json` (832 развёртки,
13 семейств × 64 старта, 40 снимков траектории на развёртку). Новых
вычислений на GPU нет: только чтение уже записанной переписи.

Правила (зафиксированы до запуска):

1. Класс «встречен в семействе», если он встречается хотя бы в одном из
   снимков траектории хотя бы одного прогона этого семейства.
2. Семейство называется «только транзиторным» для класса, если класс в нём
   встречается, но ни один прогон этого семейства не заканчивается этим
   классом (финальный класс прогона — последний снимок траектории).
3. Класс «эксклюзивен», если он встречается ровно в одном семействе и ни в
   одном семействе не является только транзиторным.
4. Класс «универсален», если он встречается в трёх и более семействах.
5. Это описание структуры карты, а не проверка гипотезы: значимость
   здесь не оценивается.
"""
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve()
EXP = HERE.parents[1]
CENSUS = EXP / "census.json"
OUT = EXP / "transient_class_analysis_exploratory.json"

CLASSES = ["struct_1", "struct_2", "uniform_dark", "uniform_bright", "death"]
EXCLUSIVE_MAX_FAMILIES = 1
UNIVERSAL_MIN_FAMILIES = 3

census = json.loads(CENSUS.read_text(encoding="utf-8"))
runs = census["runs"]

families = []
for r in runs:
    if r["family"] not in families:
        families.append(r["family"])
families.sort()

per_family = {}
for fam in families:
    group = [r for r in runs if r["family"] == fam]
    final_counts = Counter(r["class_name"] for r in group)
    visited = Counter()
    transient = Counter()
    steps = Counter()
    for r in group:
        traj = r.get("trajectory_class") or []
        for cls in set(traj):
            visited[cls] += 1
        for cls in set(traj):
            if r["class_name"] != cls:
                transient[cls] += 1
        for cls in traj:
            steps[cls] += 1
    per_family[fam] = {
        "n_runs": len(group),
        "is_control": bool(group[0].get("is_control")),
        "final_classes": dict(final_counts),
        "visited_classes": dict(visited),
        "transient_only_classes": dict(transient),
        "snapshot_occurrences": dict(steps),
    }

per_class = {}
for cls in CLASSES:
    with_cls = [f for f in families if cls in per_family[f]["visited_classes"]]
    transient_only = [
        f
        for f in families
        if cls in per_family[f]["visited_classes"]
        and per_family[f]["final_classes"].get(cls, 0) == 0
    ]
    finals = {
        f: per_family[f]["final_classes"].get(cls, 0) for f in with_cls
    }
    per_class[cls] = {
        "families_with_class": len(with_cls),
        "family_list": with_cls,
        "transient_only_families": transient_only,
        "n_transient_only_families": len(transient_only),
        "final_counts_by_family": finals,
        "total_final_runs": sum(finals.values()),
        "total_runs_visited": sum(
            per_family[f]["visited_classes"].get(cls, 0) for f in with_cls
        ),
        "exclusive": bool(
            len(with_cls) == EXCLUSIVE_MAX_FAMILIES and not transient_only
        ),
        "universal": bool(len(with_cls) >= UNIVERSAL_MIN_FAMILIES),
    }

result = {
    "schema_version": 1,
    "experiment": "E02b_morphospace",
    "kind": "exploratory_transient_class_analysis",
    "note": (
        "структура карты: какие классы встречаются транзиторно; "
        "только чтение census.json, без новых вычислений на GPU"
    ),
    "source": "census.json",
    "n_runs": len(runs),
    "n_families": len(families),
    "rules": {
        "visited": "класс встречается хотя бы в одном снимке траектории",
        "transient_only_family": (
            "класс встречается в семействе, но ни один прогон не заканчивается им"
        ),
        "exclusive": (
            f"класс встречается ровно в {EXCLUSIVE_MAX_FAMILIES} семействе "
            "и нигде не только транзиторный"
        ),
        "universal": f"класс встречается в >= {UNIVERSAL_MIN_FAMILIES} семействах",
    },
    "per_class": per_class,
    "per_family": per_family,
    "summary": {
        "exclusive_classes": [c for c in CLASSES if per_class[c]["exclusive"]],
        "universal_classes": [c for c in CLASSES if per_class[c]["universal"]],
        "struct_2_families": per_class["struct_2"]["family_list"],
        "struct_2_transient_only_families": per_class["struct_2"][
            "transient_only_families"
        ],
        "struct_1_families": per_class["struct_1"]["family_list"],
        "struct_1_transient_only_families": per_class["struct_1"][
            "transient_only_families"
        ],
    },
}

OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"[transient] записан {OUT}", flush=True)
for cls in CLASSES:
    pc = per_class[cls]
    print(
        f"[transient] {cls:16s} семейств={pc['families_with_class']:2d} "
        f"только транзиторно={pc['n_transient_only_families']:2d} "
        f"exclusive={pc['exclusive']}",
        flush=True,
    )
