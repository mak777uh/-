"""E02b E05: геометрия формы — чем struct_2 отличается от struct_1 по рисунку.

Вопрос к сильному выражению «у выученной модели есть своя форма»: различие
между `struct_2` (выученная форма R-9 seed42) и `struct_1` (архитектурный
конфаунд, одинаковый у необученной сети) — это различие в ГЕОМЕТРИИ рисунка
(где лежит масса, как она связана, каков профиль по радиусу) или только в
текстуре и яркости? Если только в текстуре, слово «форма» слишком сильное.
Если различие геометрическое, у выученной формы есть собственная геометрия.

Источник данных — каноническая перепись `census.json` (832 развёртки,
13 семейств × 64 старта) и полный дескриптор финального состояния каждой
развёртки. Новых вычислений на GPU нет: только чтение уже записанной переписи.

Правила (зафиксированы ДО запуска):

1. Популяция — все 832 прогона. Группировка — финальный класс (`class_name`).

2. Оси делятся на три уровня зависимости от кластеризации. Классы были
   разведены по 18-мерному вектору `CLUSTER_FEATURES`, поэтому различие по
   признаку из этого вектора частично тавтологично.
   - Уровень A, независимые: признак вычислен по величине, которой в
     `CLUSTER_FEATURES` не было и которая не является его статистикой.
     autocorr_lag2, autocorr_lag8, centroid_x, centroid_y, soft_std,
     bright_alive_fraction, alive_b0.
   - Уровень B, частично зависимые: та же вычислительная процедура, что и у
     признака из `CLUSTER_FEATURES`, но сам признак в вектор не входил.
     radial_outer_occupancy, radial_profile (вектор 8 бинов).
   - Уровень C, круговые: признаки из `CLUSTER_FEATURES`. Приводятся для
     справки и в вердикт НЕ входят.

3. Главный вердикт считается ТОЛЬКО по уровню A. Вторичный — по A+B.
   Уровень C показан, но не учитывается.

4. Для скалярной оси «полное разделение» = max(A) < min(B) или min(A) > max(B),
   без допусков. Дополнительно: доля верных по ближайшей медиане (accuracy) и
   разрыв медиан в единицах объединённого IQR.

5. Для векторной оси `radial_profile` критерий «полного разделения» другой:
   для каждого прогона считается L1-расстояние (полная вариация) до среднего
   профиля группы A и до среднего профиля группы B; полное разделение = все
   прогоны A ближе к профилю A, и все прогоны B ближе к профилю B.

6. Вердикт по паре групп:
   - «геометрически различны» — ≥3 оси с полным разделением;
   - «частично различны» — 1–2 оси;
   - «не различны» — 0 осей.

7. Контрасты (зафиксированы ДО запуска):
   C1: struct_2 (все прогоны) vs struct_1 (все прогоны)
   C2: struct_2 vs uniform_dark
   C3: struct_1 необученной архитектуры vs struct_1 выученных семейств
   C4: struct_2 vs struct_1 необученной архитектуры

8. Значимость не оценивается: полное разделение на 832 прогонах — уже
   консервативный критерий. Приводится доля инверсий (аналог U-статистики)
   как описание силы разделения.
"""
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve()
EXP = HERE.parents[1]
CENSUS = EXP / "census.json"
OUT = EXP / "geometry_of_form_exploratory.json"

# Признаки 18-мерного вектора кластеризации (копия из e02b_morphospace.py).
# Дублируется здесь намеренно: уровень зависимости оси определяется именно
# этим списком, и он не должен молча разъехаться с кодом кластеризации.
CLUSTER_FEATURES = (
    "alive_fraction",
    "binary_fraction",
    "bright_fraction",
    "soft_mean",
    "entropy",
    "log1p_b0",
    "log1p_b1",
    "chi",
    "bbox_fill",
    "largest_component_fraction",
    "radial_var",
    "radial_peak_bin",
    "radial_center_occupancy",
    "symmetry_rot_centered",
    "symmetry_reflect_centered",
    "autocorr_lag1",
    "autocorr_lag4",
    "edge_fraction",
)

AXES_A = [
    "autocorr_lag2",
    "autocorr_lag8",
    "centroid_x",
    "centroid_y",
    "soft_std",
    "bright_alive_fraction",
    "alive_b0",
]
AXES_B = ["radial_outer_occupancy"]
AXES_VECTOR = ["radial_profile"]
AXES_C = list(CLUSTER_FEATURES)

# Добавлено ПОСЛЕ основного результата. Это проверка устойчивости вердикта к
# спорному выбору состава уровня A, а не замена основного правила. В строгий
# набор попадают только оси, которые (а) не входят в CLUSTER_FEATURES,
# (б) не вычисляются той же процедурой, что признак из вектора
# (`alive_b0` — та же процедура подсчёта компонент, что у `log1p_b0`;
# `autocorr_lag2` — та же процедура, что у `autocorr_lag1`/`lag4`;
# `bright_alive_fraction` — выводится из `bright_fraction` и `alive_fraction`),
# и (в) не приводят к осевому смещению, то есть к «форме в углу поля».
AXES_A_STRICT = [
    "autocorr_lag8",
    "soft_std",
    "centroid_x",
    "centroid_y",
    "radial_outer_occupancy",
]
AXES_A_EXCLUDED_FROM_STRICT = {
    "alive_b0": "та же процедура подсчёта компонент, что у log1p_b0",
    "autocorr_lag2": "та же процедура автокорреляции, что у autocorr_lag1/lag4",
    "bright_alive_fraction": "выводится из bright_fraction и alive_fraction",
}

UNTRAINED_FAMILY = "untrained_current_arch"
DISTINCT_MIN_AXES = 3

census = json.loads(CENSUS.read_text(encoding="utf-8"))
runs = census["runs"]


def rows_of(predicate):
    return [r for r in runs if predicate(r)]


GROUPS = {
    "struct_2": rows_of(lambda r: r["class_name"] == "struct_2"),
    "struct_1": rows_of(lambda r: r["class_name"] == "struct_1"),
    "uniform_dark": rows_of(lambda r: r["class_name"] == "uniform_dark"),
    "struct_1_untrained": rows_of(
        lambda r: r["class_name"] == "struct_1"
        and r["family"] == UNTRAINED_FAMILY
    ),
    "struct_1_learned": rows_of(
        lambda r: r["class_name"] == "struct_1" and not r.get("is_control")
    ),
}

CONTRASTS = [
    ("C1_struct2_vs_struct1", "struct_2", "struct_1"),
    ("C2_struct2_vs_uniform_dark", "struct_2", "uniform_dark"),
    ("C3_struct1_untrained_vs_learned", "struct_1_untrained", "struct_1_learned"),
    ("C4_struct2_vs_struct1_untrained", "struct_2", "struct_1_untrained"),
]


def values(group_rows, axis):
    out = []
    for r in group_rows:
        v = r["final"].get(axis)
        if v is None:
            continue
        out.append(float(v))
    return np.asarray(out, dtype=np.float64)


def profiles(group_rows):
    out = []
    for r in group_rows:
        prof = r["final"].get("radial_profile")
        if not prof:
            continue
        out.append(np.asarray(prof, dtype=np.float64))
    return np.asarray(out, dtype=np.float64)


def scalar_axis_stats(a_vals, b_vals):
    """Статистики по одной скалярной оси для пары групп."""
    res = {
        "n_a": int(a_vals.size),
        "n_b": int(b_vals.size),
        "median_a": float(np.median(a_vals)) if a_vals.size else None,
        "median_b": float(np.median(b_vals)) if b_vals.size else None,
        "q25_a": float(np.percentile(a_vals, 25)) if a_vals.size else None,
        "q75_a": float(np.percentile(a_vals, 75)) if a_vals.size else None,
        "q25_b": float(np.percentile(b_vals, 25)) if b_vals.size else None,
        "q75_b": float(np.percentile(b_vals, 75)) if b_vals.size else None,
        "min_a": float(a_vals.min()) if a_vals.size else None,
        "max_a": float(a_vals.max()) if a_vals.size else None,
        "min_b": float(b_vals.min()) if b_vals.size else None,
        "max_b": float(b_vals.max()) if b_vals.size else None,
    }
    if not a_vals.size or not b_vals.size:
        res.update(
            complete_separation=False,
            direction=None,
            accuracy=None,
            inversions=None,
            median_gap_over_pooled_iqr=None,
        )
        return res
    separated = bool(a_vals.max() < b_vals.min() or b_vals.max() < a_vals.min())
    if separated:
        direction = "a_higher" if np.median(a_vals) > np.median(b_vals) else "b_higher"
    else:
        direction = None
    # Ближайшая медиана: доля прогонов, отнесённых к своей группе.
    ma, mb = float(np.median(a_vals)), float(np.median(b_vals))
    correct = int(np.sum(np.abs(a_vals - ma) < np.abs(a_vals - mb)))
    correct += int(np.sum(np.abs(b_vals - mb) < np.abs(b_vals - ma)))
    total = a_vals.size + b_vals.size
    # Доля инверсий: какая доля пар (a < b) — доля неправильного порядка.
    all_a = np.repeat(a_vals, b_vals.size)
    all_b = np.tile(b_vals, a_vals.size)
    inv = float(np.mean(all_a < all_b))
    iqr_a = float(np.percentile(a_vals, 75) - np.percentile(a_vals, 25))
    iqr_b = float(np.percentile(b_vals, 75) - np.percentile(b_vals, 25))
    pooled = max((iqr_a + iqr_b) / 2.0, 1e-12)
    gap = abs(ma - mb) / pooled
    res.update(
        complete_separation=separated,
        direction=direction,
        accuracy=float(correct / total) if total else None,
        inversions=inv,
        median_gap_over_pooled_iqr=float(gap),
    )
    return res


def vector_axis_stats(a_prof, b_prof):
    """radial_profile: полное разделение через ближайший средний профиль."""
    res = {
        "n_a": int(a_prof.shape[0]),
        "n_b": int(b_prof.shape[0]),
    }
    if a_prof.shape[0] == 0 or b_prof.shape[0] == 0:
        res.update(complete_separation=False, accuracy=None)
        return res
    mean_a = a_prof.mean(axis=0)
    mean_b = b_prof.mean(axis=0)
    da = 0.5 * np.abs(a_prof - mean_a[None, :]).sum(axis=1)
    db = 0.5 * np.abs(a_prof - mean_b[None, :]).sum(axis=1)
    da_b = 0.5 * np.abs(b_prof - mean_b[None, :]).sum(axis=1)
    db_b = 0.5 * np.abs(b_prof - mean_a[None, :]).sum(axis=1)
    correct = int(np.sum(da < db)) + int(np.sum(da_b < db_b))
    total = a_prof.shape[0] + b_prof.shape[0]
    res.update(
        complete_separation=bool(correct == total),
        accuracy=float(correct / total),
        mean_profile_a=[float(v) for v in mean_a],
        mean_profile_b=[float(v) for v in mean_b],
        mean_profile_l1=float(0.5 * np.abs(mean_a - mean_b).sum()),
    )
    return res


def verdict(n_separated):
    if n_separated >= DISTINCT_MIN_AXES:
        return "geometrically_distinct"
    if n_separated >= 1:
        return "partially_distinct"
    return "not_distinct"


contrasts_out = {}
for name, ga_name, gb_name in CONTRASTS:
    ga, gb = GROUPS[ga_name], GROUPS[gb_name]
    per_axis = {}
    for axis in AXES_A:
        per_axis[axis] = dict(scalar_axis_stats(values(ga, axis), values(gb, axis)),
                               tier="A")
    for axis in AXES_B:
        per_axis[axis] = dict(scalar_axis_stats(values(ga, axis), values(gb, axis)),
                               tier="B")
    for axis in AXES_VECTOR:
        per_axis[axis] = dict(vector_axis_stats(profiles(ga), profiles(gb)), tier="B")
    for axis in AXES_C:
        per_axis[axis] = dict(scalar_axis_stats(values(ga, axis), values(gb, axis)),
                               tier="C")
    sep_a = [a for a, s in per_axis.items() if s["tier"] == "A" and s["complete_separation"]]
    sep_b = [a for a, s in per_axis.items() if s["tier"] == "B" and s["complete_separation"]]
    sep_c = [a for a, s in per_axis.items() if s["tier"] == "C" and s["complete_separation"]]
    sep_strict = [
        a
        for a in AXES_A_STRICT
        if per_axis[a].get("complete_separation")
    ]
    contrasts_out[name] = {
        "group_a": ga_name,
        "group_b": gb_name,
        "n_a": len(ga),
        "n_b": len(gb),
        "n_separated_A": len(sep_a),
        "separated_A": sep_a,
        "n_separated_B": len(sep_b),
        "separated_B": sep_b,
        "n_separated_C": len(sep_c),
        "separated_C": sep_c,
        "n_separated_A_strict": len(sep_strict),
        "separated_A_strict": sep_strict,
        "verdict_A": verdict(len(sep_a)),
        "verdict_AB": verdict(len(sep_a) + len(sep_b)),
        "verdict_A_strict": verdict(len(sep_strict)),
        "per_axis": per_axis,
    }

# Описательные профили по группам: форма в терминах «пятно / кольцо / ядро».
group_profiles = {}
for gname, grows in GROUPS.items():
    prof = profiles(grows)
    if prof.shape[0] == 0:
        continue
    group_profiles[gname] = {
        "n": int(prof.shape[0]),
        "mean_radial_profile": [float(v) for v in prof.mean(axis=0)],
        "median_outer_occupancy": float(np.median(values(grows, "radial_outer_occupancy"))),
        "median_center_occupancy": float(
            np.median(values(grows, "radial_center_occupancy"))
        ),
        "median_peak_bin": float(np.median(values(grows, "radial_peak_bin"))),
        "median_alive_b0": float(np.median(values(grows, "alive_b0"))),
        "median_largest_component_fraction": float(
            np.median(values(grows, "largest_component_fraction"))
        ),
    }

result = {
    "schema_version": 1,
    "experiment": "E02b_morphospace",
    "kind": "exploratory_geometry_of_form",
    "note": (
        "геометрическая сигнатура классов по канонической переписи; "
        "только чтение census.json, без новых вычислений на GPU"
    ),
    "source": "census.json",
    "n_runs": len(runs),
    "rules": {
        "tier_A": (
            "признаки, которых не было в 18-мерном векторе кластеризации; "
            "главный вердикт считается только по ним"
        ),
        "tier_B": "та же процедура, но сам признак в вектор не входил",
        "tier_C": "признаки из CLUSTER_FEATURES; в вердикт не входят",
        "complete_separation": (
            "max(A) < min(B) или min(A) > max(B) без допусков; "
            "для radial_profile — 100% верности по ближайшему среднему профилю"
        ),
        "verdict": (
            f">= {DISTINCT_MIN_AXES} осей с полным разделением — "
            "«геометрически различны»; 1–2 — «частично различны»; 0 — «не различны»"
        ),
        "axes_A": AXES_A,
        "axes_B": AXES_B,
        "axes_vector": AXES_VECTOR,
        "axes_A_strict": AXES_A_STRICT,
        "axes_A_excluded_from_strict": AXES_A_EXCLUDED_FROM_STRICT,
        "contrasts": [c[0] for c in CONTRASTS],
    },
    "groups": {
        name: {
            "n": len(rows),
            "families": sorted({r["family"] for r in rows}),
            "n_families": len({r["family"] for r in rows}),
        }
        for name, rows in GROUPS.items()
    },
    "contrasts": contrasts_out,
    "group_profiles": group_profiles,
    "summary": {
        name: {
            "n_separated_A": c["n_separated_A"],
            "separated_A": c["separated_A"],
            "n_separated_B": c["n_separated_B"],
            "n_separated_C": c["n_separated_C"],
            "n_separated_A_strict": c["n_separated_A_strict"],
            "separated_A_strict": c["separated_A_strict"],
            "verdict_A": c["verdict_A"],
            "verdict_AB": c["verdict_AB"],
            "verdict_A_strict": c["verdict_A_strict"],
        }
        for name, c in contrasts_out.items()
    },
}

OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"[geometry] записан {OUT}", flush=True)
for name, c in contrasts_out.items():
    print(
        f"[geometry] {name:42s} A={c['n_separated_A']} B={c['n_separated_B']} "
        f"C={c['n_separated_C']} -> {c['verdict_A']}",
        flush=True,
    )
    for axis in c["separated_A"] + c["separated_B"]:
        s = c["per_axis"][axis]
        print(
            f"[geometry]     {axis:26s} tier={s['tier']} "
            f"dir={s.get('direction')} acc={s.get('accuracy')}",
            flush=True,
        )
