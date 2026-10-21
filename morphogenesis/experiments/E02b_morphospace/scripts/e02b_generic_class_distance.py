"""E02b, exploratory: насколько `struct_1` — это артефакт архитектуры, а не выученный класс?

В отчёте сказано: необученная архитектура даёт `struct_1` 64/64, значит этот
«структурный класс» — generic-аттрактор самой архитектуры, а не память,
выученная обучением. Но метка класса — это ближайший центроид; одно совпадение
меток ещё не показывает, что облака состояний совпадают.

Здесь это измеряется расстояниями в z-пространстве кластеризации (те же
18 признаков, та же нормировка, что и в census):

- расстояние от облака контрольной группы до центроида каждого класса;
- внутриклассовый разброс (насколько широко рассеян сам класс);
- попарные расстояния между центроидами классов.

Если облако необученной архитектуры лежит на центроиде `struct_1` и при этом
ближе к нему, чем к любому другому классу, то первый «структурный класс» E02b —
свойство архитектуры, а выученная структура в стенде ровно одна: `struct_2`.

Важно: все расстояния считаются в z-пространстве (сырой дескриптор сначала
нормируется тем же mean/std, что и при кластеризации). Сравнивать сырой
вектор с z-центроидом нельзя — это даёт бессмысленные сотни единиц.

Только чтение census.json, никакого обучения и никаких новых развёрток.
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve()
EXP = HERE.parents[1]
sys.path.insert(0, str(HERE.parents[3]))
import e02b_morphospace as e02b  # noqa: E402

CENSUS = EXP / "census.json"
OUT = EXP / "generic_class_distance_exploratory.json"

census = json.load(open(CENSUS, encoding="utf-8"))
cl = census["clustering"]
mean = np.asarray(cl["scaler_mean"])
std = np.asarray(cl["scaler_std"])
valid = cl["labels_valid"]
names = {int(c): str(n) for c, n in zip(valid, cl["class_names"], strict=True)}
semantics = {int(c): str(s) for c, s in zip(valid, cl["semantic"], strict=True)}
ids = [int(c) for c in valid]
classes = [names[c] for c in ids]


def zscore(vec):
    return (np.asarray(vec, dtype=np.float64) - mean) / std


by_cluster = {c: [] for c in ids}
controls = {}
for r in census["runs"]:
    vec = zscore(e02b.descriptor_vector(r["final"]))
    if r.get("is_control"):
        controls.setdefault(str(r.get("family")), []).append(vec)
        continue
    cid = int(r["cluster"])
    if cid in by_cluster:
        by_cluster[cid].append(vec)

centroids = np.vstack([np.asarray(by_cluster[c]).mean(axis=0) for c in ids])
pairwise = {
    classes[i]: {
        classes[j]: float(np.linalg.norm(centroids[i] - centroids[j]))
        for j in range(len(ids))
    }
    for i in range(len(ids))
}

per_class = {}
for i, cname in enumerate(classes):
    group = np.vstack(by_cluster[ids[i]])
    own = float(np.linalg.norm(group - centroids[i], axis=1).mean())
    others = {k: v for k, v in pairwise[cname].items() if k != cname}
    nearest = min(others, key=others.get)
    per_class[cname] = {
        "n": int(len(group)),
        "semantic": semantics[ids[i]],
        "within_class_spread": own,
        "within_class_max": float(np.linalg.norm(group - centroids[i], axis=1).max()),
        "nearest_other_class": nearest,
        "nearest_other_distance": others[nearest],
    }
    for fam, pts in controls.items():
        cloud = np.vstack(pts)
        per_class[cname][f"distance_to_{fam}"] = float(
            np.linalg.norm(cloud - centroids[i], axis=1).mean()
        )

control_report = {}
for fam, pts in controls.items():
    cloud = np.vstack(pts)
    c0 = cloud.mean(axis=0)
    ranked = sorted(
        (
            (float(np.linalg.norm(cloud - centroids[i], axis=1).mean()), classes[i])
            for i in range(len(ids))
        )
    )
    control_report[fam] = {
        "n": int(len(cloud)),
        "within_cloud_spread": float(np.linalg.norm(cloud - c0, axis=1).mean()),
        "centroid_to_class_centroid": {
            classes[i]: float(np.linalg.norm(c0 - centroids[i]))
            for i in range(len(ids))
        },
        "mean_point_to_class_centroid": {name: dist for dist, name in ranked},
        "nearest_class": ranked[0][1],
        "second_class": ranked[1][1],
        "margin_over_second": ranked[1][0] - ranked[0][0],
        "relative_margin": (
            (ranked[1][0] - ranked[0][0]) / ranked[1][0] if ranked[1][0] > 0 else None
        ),
    }

# Вердикт по структурным классам. Класс «generic», если облако необученной
# архитектуры лежит ВНУТРИ собственного рассеяния класса: средняя дистанция
# от облака до центроида не больше удвоенного внутриклассового разброса, и
# облако при этом в 2 раза ближе к этому классу, чем ко второму по близости.
# Иначе класс «learned»: необученная архитектура в него не попадает.
UNTRAINED = "untrained_current_arch"
SPREAD_FACTOR = 2.0
MARGIN_FACTOR = 2.0
generic = set()
learned = set()
untrained_report = control_report[UNTRAINED]
second_distance = untrained_report["mean_point_to_class_centroid"][
    untrained_report["second_class"]
]
for cname in ("struct_1", "struct_2"):
    if cname not in per_class:
        continue
    own = per_class[cname].get(f"distance_to_{UNTRAINED}")
    if own is None:
        continue
    spread = per_class[cname]["within_class_spread"]
    inside = own <= SPREAD_FACTOR * spread
    closest = untrained_report["nearest_class"] == cname
    margin = (
        second_distance / own if own > 0 else float("inf")
    )
    if inside and closest and margin >= MARGIN_FACTOR:
        generic.add(cname)
    else:
        learned.add(cname)
    per_class[cname]["generic_verdict"] = {
        "inside_own_spread": bool(inside),
        "is_untrained_nearest_class": bool(closest),
        "margin_over_own_distance": float(margin),
        "verdict": "generic" if cname in generic else "learned",
    }

result = {
    "schema_version": 1,
    "experiment": "E02b_morphospace",
    "kind": "exploratory_generic_class_distance",
    "note": (
        "расстояния в z-пространстве кластеризации census: совпадает ли облако "
        "необученной архитектуры с облаком класса; только чтение census.json, "
        "без новых развёрток"
    ),
    "space": "z-пространство кластеризации (mean/std census), 18 признаков",
    "rules": {
        "generic": (
            f"средняя дистанция от облака необученной архитектуры до центроида "
            f"класса <= {SPREAD_FACTOR} × внутриклассовый разброс, и этот класс — "
            f"ближайший к облаку, и запас ко второму классу >= {MARGIN_FACTOR}×"
        ),
        "learned": "иначе: облако необученной архитектуры в этот класс не попадает",
    },
    "classes": per_class,
    "control_groups": control_report,
    "pairwise_centroid_distance": pairwise,
    "summary": {
        "generic_structural_classes": sorted(generic),
        "learned_structural_classes": sorted(learned),
        "struct_1_distance_to_untrained_cloud": per_class["struct_1"].get(
            f"distance_to_{UNTRAINED}"
        ),
        "struct_2_distance_to_untrained_cloud": per_class["struct_2"].get(
            f"distance_to_{UNTRAINED}"
        ),
        "struct_1_within_class_spread": per_class["struct_1"]["within_class_spread"],
        "untrained_cloud_spread": control_report[UNTRAINED]["within_cloud_spread"],
        "untrained_margin_over_second_class": control_report[UNTRAINED][
            "relative_margin"
        ],
    },
}

with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(result, fh, ensure_ascii=False, indent=2)
s = result["summary"]
print(
    f"[generic] необученная: облако на расстоянии "
    f"{s['struct_1_distance_to_untrained_cloud']:.3f} от struct_1 "
    f"(разброс облака {s['untrained_cloud_spread']:.3f}, разброс класса "
    f"{s['struct_1_within_class_spread']:.3f}); до struct_2 — "
    f"{s['struct_2_distance_to_untrained_cloud']:.3f}",
    flush=True,
)
print(
    f"[generic] generic: {s['generic_structural_classes']}; "
    f"выученные: {s['learned_structural_classes']}",
    flush=True,
)
print(f"[generic] saved {OUT}", flush=True)
