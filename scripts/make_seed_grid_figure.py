"""Собрать Figure 4 рукописи: сетка «инициализация × порядок данных» (§4.13).

Зачем: §4.13 сейчас — таблица в тексте. Сетка 2×4 с восемью клетками (четыре
измеренных + два якоря в тех же строках) читается как карта бассейна: при init=42
`struct_2` держится с тремя порядками данных, при init=101 не появляется ни разу.

Данные — только [`seed_grid.json`](../morphogenesis/experiments/E02c_replication/seed_grid.json):
счётчики классов и провенанс клетки (measured или anchor). Ни обучения, ни GPU,
ни новых измерений.

Запуск (из корня репозитория):

    python scripts/make_seed_grid_figure.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
EXP = REPO / "morphogenesis" / "experiments" / "E02c_replication"
GRID = EXP / "seed_grid.json"
OUT = REPO / "reports" / "figures" / "e02c_seed_grid.png"

INITS = [42, 101]
DATAS = [42, 101, 202, 303]

# Цвета классов: те же акценты, что в тексте (structured — тёплый, смерть — серый).
COLORS = {
    "struct_2": "#c0504d",
    "struct_1": "#4f81bd",
    "uniform_dark": "#7f7f7f",
    "uniform_bright": "#b3b3b3",
    "death": "#404040",
    "outlier": "#d9d9d9",
}
LABELS = {
    "struct_2": "struct_2",
    "struct_1": "struct_1",
    "uniform_dark": "uniform\ndark",
    "uniform_bright": "uniform\nbright",
    "death": "death",
}


def load_grid() -> dict:
    if not GRID.is_file():
        raise SystemExit(
            f"нет {GRID}: сначала соберите сетку `python scripts/e02c_seed_grid.py`"
        )
    return json.loads(GRID.read_text(encoding="utf-8"))


def cell_key(init: int, data: int) -> str:
    return f"init{init}_data{data}"


def draw(grid: dict, out: Path) -> None:
    cells = grid["cells"]
    fig, ax = plt.subplots(figsize=(8.6, 3.6))
    for row, init in enumerate(INITS):
        for col, data in enumerate(DATAS):
            key = cell_key(init, data)
            ax.add_patch(
                Rectangle((col, len(INITS) - 1 - row), 1, 1, facecolor="white", edgecolor="black", lw=0.6)
            )
            cell = cells.get(key)
            if cell is None:
                ax.text(col + 0.5, len(INITS) - 1 - row + 0.5, "—", ha="center", va="center",
                        fontsize=11, color="#999999")
                continue
            cls = cell["dominant_class"]
            n = cell.get("n") or 64
            count = cell.get("struct_2") if cls == "struct_2" else None
            if count is None:
                counts = cell.get("class_counts") or {}
                count = counts.get(cls, n)
            ax.add_patch(
                Rectangle(
                    (col, len(INITS) - 1 - row),
                    1,
                    1,
                    facecolor=COLORS.get(cls, "#d9d9d9"),
                    alpha=0.85,
                    edgecolor="black",
                    lw=2.4 if cell["kind"] == "measured" else 0.9,
                    linestyle="-" if cell["kind"] == "measured" else "--",
                )
            )
            ax.text(
                col + 0.5,
                len(INITS) - 1 - row + 0.56,
                LABELS.get(cls, cls),
                ha="center",
                va="center",
                fontsize=10,
                color="white" if cls not in ("uniform_bright", "outlier") else "black",
                fontweight="bold",
            )
            ax.text(
                col + 0.5,
                len(INITS) - 1 - row + 0.3,
                f"{count}/{n}",
                ha="center",
                va="center",
                fontsize=8.5,
                color="white" if cls not in ("uniform_bright", "outlier") else "black",
            )
            if cell["kind"] == "anchor":
                ax.text(
                    col + 0.9,
                    len(INITS) - 1 - row + 0.9,
                    "anchor",
                    ha="right",
                    va="top",
                    fontsize=6.5,
                    color="white",
                    style="italic",
                )

    ax.set_xlim(0, len(DATAS))
    ax.set_ylim(0, len(INITS))
    ax.set_xticks([c + 0.5 for c in range(len(DATAS))])
    ax.set_xticklabels([f"data {d}" for d in DATAS], fontsize=9)
    ax.set_yticks([len(INITS) - 1 - r + 0.5 for r in range(len(INITS))])
    ax.set_yticklabels([f"init {i}" for i in INITS], fontsize=9)
    ax.set_xlabel("data order (seed of the data factor)", fontsize=9)
    ax.set_ylabel("weight initialisation", fontsize=9)
    ax.set_title(
        "R-9: dominant census class per cell (64 starts, frozen E02b centroids)",
        fontsize=10,
    )
    ax.set_aspect("equal")
    fig.subplots_adjust(left=0.12, right=0.98, top=0.88, bottom=0.30)
    fig.text(
        0.02,
        0.04,
        "Measured cell: bold solid border; anchor from a published report: dashed border.\n"
        "init=42 keeps struct_2 with three data orders; init=101 never produces it.",
        fontsize=7.5,
        va="bottom",
        ha="left",
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=160)
    plt.close(fig)


def main() -> int:
    grid = load_grid()
    draw(grid, OUT)
    print(f"записано: {OUT} ({OUT.stat().st_size} байт)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
