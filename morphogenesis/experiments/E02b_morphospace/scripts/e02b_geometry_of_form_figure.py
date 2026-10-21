"""Фигура: геометрия формы — «тело» против «россыпи».

Читает `geometry_of_form_exploratory.json` (результат
`e02b_geometry_of_form.py`) и рисует три панели:

- слева: средний профиль заполнения по радиусу (8 бинов) для четырёх групп —
  видно, что `struct_2` это заполненный диск с плотным краем, а `struct_1` —
  россыпь без радиальной структуры;
- в центре: распределение числа связных живых островов (`alive_b0`) по группам —
  главный признак, который разделяет классы и который НЕ входил в вектор
  кластеризации;
- справа: разброс независимых осей по группам (нормированный), с отметкой
  порога вердикта.

Скрипт читает артефакт, ничего не пересчитывает «по-своему»: все числа взяты
из готовых полей артефакта, вердикты пересчитаны независимым верификатором
`e02b_verify_exploratory.py`.

Запуск: `python e02b_geometry_of_form_figure.py`
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve()
EXP = HERE.parents[1]
REPO = HERE.parents[4]
ART = EXP / "geometry_of_form_exploratory.json"
FIG = REPO / "reports" / "figures" / "e02b_geometry_of_form.png"

if not ART.exists():
    raise SystemExit(f"нет артефакта {ART}")

art = json.loads(ART.read_text(encoding="utf-8"))
profiles = art["group_profiles"]
contrasts = art["contrasts"]

PANELS = [
    ("struct_2", "struct_2 (R-9 seed42)", "#b2182b", "o"),
    ("struct_1_untrained", "struct_1 (необуч.)", "#2166ac", "s"),
    ("struct_1_learned", "struct_1 (обученные)", "#67a9cf", "^"),
    ("uniform_dark", "uniform_dark", "#888888", "x"),
]
AXES_A = art["rules"]["axes_A"]
AXES_B = art["rules"]["axes_B"]

fig, axes = plt.subplots(1, 3, figsize=(15.5, 4.9))

# --- 1. профиль по радиусу -------------------------------------------------
ax = axes[0]
for key, label, color, marker in PANELS:
    prof = profiles.get(key)
    if not prof:
        continue
    xs = np.arange(1, len(prof["mean_radial_profile"]) + 1)
    ax.plot(
        xs,
        prof["mean_radial_profile"],
        marker=marker,
        color=color,
        label=f"{label} (n={prof['n']})",
    )
ax.set_xticks(np.arange(1, 9))
ax.set_xlabel("радиальный бин (1 — центр, 8 — край поля)")
ax.set_ylabel("доля заполнения бина")
ax.set_title("Профиль по радиусу: тело с плотным краем против россыпи")
ax.legend(fontsize=8, loc="lower right")
ax.grid(alpha=0.25, linewidth=0.6)

# --- 2. число связных живых островов --------------------------------------
ax = axes[1]
census_path = EXP / "census.json"
if census_path.exists():
    census = json.loads(census_path.read_text(encoding="utf-8"))
    groups = {
        "struct_2": [r for r in census["runs"] if r["class_name"] == "struct_2"],
        "struct_1": [r for r in census["runs"] if r["class_name"] == "struct_1"],
    }
    data = [
        (
            "struct_2 (R-9 seed42)",
            [float(r["final"].get("alive_b0", 0)) for r in groups["struct_2"]],
            "#b2182b",
        ),
        (
            "struct_1 (все семейства)",
            [float(r["final"].get("alive_b0", 0)) for r in groups["struct_1"]],
            "#2166ac",
        ),
    ]
    for label, vals, color in data:
        vals = [v for v in vals if v > 0]
        if not vals:
            continue
        jitter = np.linspace(-0.16, 0.16, len(vals))
        ax.scatter(
            np.full(len(vals), 0 if color == "#b2182b" else 1) + jitter,
            vals,
            s=13,
            alpha=0.45,
            color=color,
            edgecolors="none",
        )
    ax.set_yscale("log")
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["struct_2", "struct_1"], fontsize=9)
    ax.set_ylabel("число связных живых островов (log)")
    ax.set_title("Связность: одно тело против россыпи")
    ax.grid(alpha=0.25, linewidth=0.6)

# --- 3. независимые оси, нормированные ------------------------------------
ax = axes[2]
c1 = contrasts["C4_struct2_vs_struct1_untrained"]
axis_list = AXES_A + AXES_B
labels = [
    "autocorr_lag2",
    "autocorr_lag8",
    "centroid_x",
    "centroid_y",
    "soft_std",
    "bright_alive_fraction",
    "alive_b0",
    "radial_outer_occupancy",
]
labels = [lab for lab in labels if lab in axis_list]
width = 0.36
for i, lab in enumerate(labels):
    stat = c1["per_axis"][lab]
    med_a = stat.get("median_a")
    med_b = stat.get("median_b")
    if med_a is None or med_b is None:
        continue
    ax.bar(
        i - width / 2,
        med_a,
        width,
        color="#b2182b",
        label="struct_2" if i == 0 else None,
    )
    ax.bar(i + width / 2, med_b, width, color="#2166ac", label="struct_1 (необуч.)" if i == 0 else None)
    if stat.get("complete_separation"):
        ax.text(
            i,
            max(med_a, med_b) * 1.06,
            "•",
            ha="center",
            va="bottom",
            fontsize=13,
            color="#333333",
        )
ax.set_yscale("symlog", linthresh=0.05)
ax.set_xticks(range(len(labels)))
ax.set_xticklabels(labels, rotation=38, ha="right", fontsize=7.5)
ax.set_ylabel("медиана (symlog)")
ax.set_title("Независимые оси: • — полное разделение")
ax.legend(fontsize=8)
ax.grid(alpha=0.25, linewidth=0.6, axis="y")

fig.suptitle(
    "E02b: какая это форма — тело или россыпь?\n"
    "Вердикт считается только по осям, не входившим в кластеризацию",
    fontsize=11.5,
)
fig.tight_layout()
FIG.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(FIG, dpi=150)
print(f"[geometry-fig] saved {FIG}", flush=True)
