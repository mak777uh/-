"""E02b, exploratory: рисунок матрицы переходов с повторами.

Читает `transition_matrix_rep_exploratory.json` (повтор матрицы 12×12 с
3 состояниями на источник и 3 сидами шума цели) и рисует два панели:

- слева — тепловая карта 12 целей × 12 источников: цвет = доминирующий
  эффективный класс пары (смерть или один из живых классов), число в клетке —
  `pair_consistency`, то есть доля из 9 выборок, попавших в этот класс;
- справа — для каждой цели минимальная `pair_consistency` среди живых
  источников: насколько устойчиво модель удерживает одну форму.

Рисунок — иллюстрация, а не доказательство: числа остаются в артефакте.
"""
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import ListedColormap, BoundaryNorm  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

HERE = Path(__file__).resolve()
EXP = HERE.parents[1]
sys.path.insert(0, str(HERE.parents[3]))
import e02b_morphospace as e02b  # noqa: E402

np = e02b.np

ART = EXP / "transition_matrix_rep_exploratory.json"
OUT = Path(__file__).resolve().parents[4] / "reports" / "figures" / "e02b_transition_matrix.png"

CLASS_ORDER = ["death", "struct_1", "struct_2", "uniform_dark", "uniform_bright"]
CLASS_COLORS = ["#d9d9d9", "#4c72b0", "#dd8452", "#8172b3", "#ccb974"]
CLASS_LABELS = {
    "death": "смерть",
    "struct_1": "struct_1",
    "struct_2": "struct_2",
    "uniform_dark": "uniform_dark",
    "uniform_bright": "uniform_bright",
}

if not ART.exists():
    print(f"[figure] нет артефакта {ART.name}, рисунок пропущен")
    raise SystemExit(0)

data = json.load(open(ART, encoding="utf-8"))
targets = data["targets"]
source_order = [
    s["family"] for s in data["source_states"][::len(data["source_seeds"])]
]
target_order = list(targets.keys())

grid = np.full((len(target_order), len(source_order)), np.nan)
cons = np.zeros_like(grid)
for i, tf in enumerate(target_order):
    for j, sf in enumerate(source_order):
        pair = targets[tf]["pairs"].get(sf)
        if not pair:
            continue
        grid[i, j] = CLASS_ORDER.index(pair["dominant_class"])
        cons[i, j] = pair["pair_consistency"]

labels = [f.replace("WP4_", "").replace("_s2000_seed", "/").replace("_s400_seed", "/s400/")
          for f in target_order]

fig, (ax, ax2) = plt.subplots(
    1, 2, figsize=(13.5, 7.2), gridspec_kw={"width_ratios": [1.35, 1]}
)

cmap = ListedColormap(CLASS_COLORS)
norm = BoundaryNorm(np.arange(-0.5, len(CLASS_ORDER)), cmap.N)
ax.imshow(grid, cmap=cmap, norm=norm, aspect="auto")

for i in range(len(target_order)):
    for j in range(len(source_order)):
        cls = CLASS_ORDER[int(grid[i, j])]
        value = cons[i, j]
        ax.text(
            j, i, f"{value:.2f}",
            ha="center", va="center", fontsize=6.6,
            color="white" if cls in {"struct_1", "struct_2", "uniform_dark"} else "#222222",
        )

ax.set_xticks(range(len(source_order)))
ax.set_xticklabels(labels, rotation=90, fontsize=7)
ax.set_yticks(range(len(target_order)))
ax.set_yticklabels(labels, fontsize=7)
ax.set_xlabel("источник (модель, из которой взято готовое состояние)", fontsize=9)
ax.set_ylabel("цель (модель, в которую состояние подано)", fontsize=9)
ax.set_title(
    "Матрица переходов с повторами: доминирующий исход и его устойчивость\n"
    "(в клетке — доля выборок пары из 9, попавших в доминирующий класс)",
    fontsize=10,
)
ax.legend(
    handles=[
        Patch(facecolor=CLASS_COLORS[k], label=CLASS_LABELS[c])
        for k, c in enumerate(CLASS_ORDER)
    ],
    loc="upper left", bbox_to_anchor=(1.02, 1.0), fontsize=8, frameon=False,
)

mins = []
for tf in target_order:
    live = targets[tf]["live_pairs"]
    mins.append(min((p["pair_consistency"] for p in live.values()), default=1.0))
colors = ["#c44e52" if m < 0.8 else "#4c72b0" for m in mins]
ax2.barh(range(len(target_order)), mins, color=colors)
ax2.axvline(0.8, color="#444444", linestyle="--", linewidth=1)
ax2.set_yticks(range(len(target_order)))
ax2.set_yticklabels(labels, fontsize=7)
ax2.set_xlim(0, 1.02)
ax2.invert_yaxis()
ax2.set_xlabel("минимальная устойчивость пары среди живых источников", fontsize=9)
ax2.set_title(
    "Где карта устойчива, а где «лотерея»\n"
    "красным — пары с устойчивостью ниже 0.8",
    fontsize=10,
)
fig.tight_layout()
OUT.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT, dpi=150, bbox_inches="tight")
print(f"[figure] saved {OUT}")
