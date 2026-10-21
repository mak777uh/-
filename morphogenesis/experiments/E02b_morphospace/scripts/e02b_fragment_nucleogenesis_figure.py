"""Фигура: кривая нуклеогенеза по размеру живого очага.

Читает `fragment_nucleogenesis_exploratory.json` (результат прогона
`e02b_fragment_nucleogenesis.py`) и рисует:
- слева: сколько из 12 повторов выросло в домашний класс с ростом живой
  области, в зависимости от размера очага k (лог-шкала), по модели и режиму;
  пунктир — предзарегистрированный порог 11 из 12;
- справа: медианный бинарный IoU финала с прототипом, по той же оси.

Скрипт читает артефакт, ничего не пересчитывает «по-своему»: все числа
взяты из готовых полей артефакта, вердикты пересчитаны независимым
верификатором `e02b_verify_exploratory.py`.

Запуск: `python e02b_fragment_nucleogenesis_figure.py`
"""
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve()
EXP = HERE.parents[1]
REPO = HERE.parents[4]
ART = EXP / "fragment_nucleogenesis_exploratory.json"
FIG = REPO / "reports" / "figures" / "e02b_fragment_nucleogenesis.png"

if not ART.exists():
    raise SystemExit(f"нет артефакта {ART}")

art = json.loads(ART.read_text(encoding="utf-8"))
models = art["models"]
modes = art.get("modes", ["scattered", "compact"])
sign_min = 11
repeats = art.get("repeats", 12)

labels = {
    "WP4_R-9_s2000_seed42": "R-9 seed42 (struct_2)",
    "WP4_R-9_s2000_seed101": "R-9 seed101 (struct_1)",
    "untrained_current_arch": "необученная архитектура",
}
styles = {
    "scattered": ("o", "-"),
    "compact": ("s", "--"),
}
colors = {
    "WP4_R-9_s2000_seed42": "#b2182b",
    "WP4_R-9_s2000_seed101": "#2166ac",
    "untrained_current_arch": "#666666",
}
mode_labels = {
    "scattered": "разбросанный",
    "compact": "компактный",
}

fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.8))

for entry in models:
    fam = entry["family"]
    for mode in modes:
        cells = [c for c in entry["cells"] if c["mode"] == mode]
        if not cells:
            continue
        cells = sorted(cells, key=lambda c: c["k"])
        ks = [c["k"] for c in cells]
        marker, ls = styles.get(mode, ("o", "-"))
        color = colors.get(fam, "#333333")
        label = f"{labels.get(fam, fam)} — {mode_labels.get(mode, mode)}"
        axes[0].plot(
            ks,
            [c["nucleogenesis_count"] for c in cells],
            marker=marker,
            linestyle=ls,
            color=color,
            label=label,
        )
        axes[1].plot(
            ks,
            [
                c["median_iou"] if c["median_iou"] is not None else 0.0
                for c in cells
            ],
            marker=marker,
            linestyle=ls,
            color=color,
            label=label,
        )

axes[0].axhline(sign_min, color="#444444", linestyle=":", linewidth=1.2)
axes[0].annotate(
    f"порог {sign_min} из {repeats}",
    (min(c["k"] for c in models[0]["cells"] if c["mode"] == modes[0]), sign_min),
    textcoords="offset points",
    xytext=(4, -12),
    fontsize=9,
    color="#444444",
)
axes[0].set_xscale("log")
axes[0].set_xticks([1, 8, 32, 128, 512])
axes[0].set_xticklabels(["1", "8", "32", "128", "512"])
axes[0].set_ylim(-0.5, repeats + 0.5)
axes[0].set_xlabel("размер живого очага k (клеток)")
axes[0].set_ylabel("пробуждений из 12")
axes[0].set_title("Нуклеогенез: поле выросло в домашний класс")
axes[0].legend(fontsize=8, loc="upper left")
axes[0].grid(alpha=0.25, linewidth=0.6)

axes[1].axhline(0.5, color="#444444", linestyle=":", linewidth=1.2)
axes[1].set_xscale("log")
axes[1].set_xticks([1, 8, 32, 128, 512])
axes[1].set_xticklabels(["1", "8", "32", "128", "512"])
axes[1].set_ylim(-0.02, 1.02)
axes[1].set_xlabel("размер живого очага k (клеток)")
axes[1].set_ylabel("медианный бинарный IoU с прототипом")
axes[1].set_title("Тот же рисунок восстановлен?")
axes[1].grid(alpha=0.25, linewidth=0.6)

fig.suptitle(
    "E02b: растёт ли целая форма из крошечного живого очага?",
    fontsize=12,
)
fig.tight_layout()
FIG.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(FIG, dpi=150)
print(f"[frag-fig] saved {FIG}", flush=True)
