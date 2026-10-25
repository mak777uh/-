"""Простой постер для владельца: что мы узнали, без терминов.

Верстка полосами с фиксированными границами, чтобы блоки не наезжали друг на друга.
Данные — из артефактов: карта found_n1_seed1.json, зоны ресурса §10ak, числа §10aj.
"""
from __future__ import annotations

import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch

INK = "#1f2933"
MUTED = "#5c6773"
GREEN = "#2e7d5b"
AMBER = "#b8860b"
RED = "#a63d40"
LIGHT = "#f6f4ee"


def load_map(path: str) -> np.ndarray:
    d = json.load(open(path, encoding="utf-8"))
    raw = (d.get("summary") or {})["final_alive_map"]
    rows = [r for r in raw.split("/") if r]
    return np.array([[1 if ch == "1" else 0 for ch in row] for row in rows], dtype=float)


alive = load_map("morphogenesis/experiments/E09_pond/found_n1_seed1.json")

fig = plt.figure(figsize=(14.0, 22.0), dpi=100)
fig.patch.set_facecolor(LIGHT)

# ================================================================ шапка
fig.text(0.05, 0.975, "Пруд в цифре: что мы узнали", fontsize=30, weight="bold",
         color=INK, va="top")
fig.text(0.05, 0.951,
         "простыми словами, без терминов · 24–25 октября · все числа из настоящих прогонов",
         fontsize=13.5, color=MUTED, va="top")

# ================================================================ 1
fig.text(0.05, 0.925, "1. Одна клетка на пустом месте — вырастает колония",
         fontsize=19, weight="bold", color=GREEN, va="top")
fig.text(0.05, 0.899,
         "Мы сажали одну-единственную клетку и ждали 300 шагов.\n"
         "В 50 случаях из 50 вырастала колония в 520–665 клеток.",
         fontsize=13.5, color=INK, va="top", linespacing=1.55)

ax1 = fig.add_axes([0.05, 0.700, 0.255, 0.170])
ax1.imshow(alive, cmap="Greens", vmin=-0.15, vmax=1.0, interpolation="nearest")
ax1.set_xticks([])
ax1.set_yticks([])
fig.text(0.05, 0.688, "настоящий прогон, 32×32: тёмное — живые клетки",
         fontsize=10.5, color=MUTED, va="top")
for s in ax1.spines.values():
    s.set_color("#c8cfd4")
    s.set_linewidth(1.4)

fig.text(0.34, 0.845,
         "Это не рисунок и не схема — это карта живых\n"
         "клеток из настоящего прогона. Колония занимает\n"
         "почти всё поле, но не сплошным пятном,\n"
         "а «кружевом» — с дырками внутри.",
         fontsize=13.0, color=INK, va="top", linespacing=1.6)
fig.text(0.34, 0.765,
         "Вывод: маленький размер — не помеха.\nРосток всходит, если место свободно.",
         fontsize=13.0, color=GREEN, va="top", linespacing=1.55, style="italic")

# ================================================================ 2
fig.text(0.05, 0.660, "2. А рядом с соседом — не всходит",
         fontsize=19, weight="bold", color=RED, va="top")
fig.text(0.05, 0.634,
         "Мы подсаживали чужие клетки (от одной до двадцати) к уже живущей колонии.\n"
         "Итог один: они погибали — во всех 50 прогонах, при любом размещении.",
         fontsize=13.5, color=INK, va="top", linespacing=1.55)

ax2 = fig.add_axes([0.05, 0.475, 0.40, 0.135])
ax2.set_xlim(0, 1)
ax2.set_ylim(0, 3)
ax2.axis("off")
plates = [
    ("под живой колонией", 0.0003, RED, "еду съели подчистую"),
    ("в свободном месте", 0.4012, GREEN, "еды полно"),
    ("куда сажали чужую клетку", 0.9811, AMBER, "еды ещё больше — и всё равно гибнет"),
]
for i, (label, val, colour, note) in enumerate(plates):
    y = 2.45 - i
    ax2.text(0.0, y + 0.34, f"{label}:  {val:.4f}", fontsize=12.0, color=INK, va="bottom")
    ax2.add_patch(plt.Rectangle((0.0, y + 0.04), max(val, 0.006) * 0.92, 0.22,
                                facecolor=colour, edgecolor="none", alpha=0.9))
    ax2.text(0.0, y - 0.08, note, fontsize=10.0, color=MUTED, va="bottom")

fig.text(0.50, 0.590,
         "Мы думали: «в занятом месте просто\n"
         "нечего есть». Проверили напрямую —\n"
         "и это оказалось неверно.",
         fontsize=13.0, color=INK, va="top", linespacing=1.6)
fig.text(0.50, 0.525,
         "Вывод: дело не в еде.\nДаже на полной тарелке\nчужая клетка не приживается.",
         fontsize=13.0, color=RED, va="top", linespacing=1.55, style="italic")

# ================================================================ 3
fig.text(0.05, 0.450, "3. Кто вообще оставляет потомство",
         fontsize=19, weight="bold", color=AMBER, va="top")
fig.text(0.05, 0.424,
         "Пруд размножается не отдельными клетками, а целой колонией: она выпускает споры.\n"
         "Новая одиночная клетка потомства не оставляет — её признак никому не передаётся.",
         fontsize=13.5, color=INK, va="top", linespacing=1.55)

ax3 = fig.add_axes([0.055, 0.295, 0.86, 0.105])
ax3.set_xlim(0, 10)
ax3.set_ylim(0, 2)
ax3.axis("off")

ax3.add_patch(Circle((1.5, 1.0), 0.45, facecolor=GREEN, edgecolor="none", alpha=0.85))
for dx, dy in [(-1.10, 0.60), (-1.18, 0.02), (-1.00, -0.56)]:
    ax3.add_patch(Circle((1.5 + dx, 1.0 + dy), 0.09, facecolor=GREEN, edgecolor="none"))
    ax3.add_patch(FancyArrowPatch((1.05, 1.0), (0.66, 1.0 + dy * 0.9),
                                  arrowstyle="-|>", mutation_scale=13, color=GREEN, lw=1.5))
ax3.text(1.5, 0.02, "колония", fontsize=11.5, color=GREEN, ha="center", weight="bold")
ax3.text(2.35, 1.0, "выпускает споры — потомство есть", fontsize=12.0, color=INK, va="center")

ax3.add_patch(Circle((7.2, 1.0), 0.12, facecolor=AMBER, edgecolor="none"))
ax3.add_patch(Circle((7.2, 1.0), 0.32, facecolor="none", edgecolor=RED, lw=1.8, ls="--"))
ax3.text(7.2, 0.02, "новая одиночная клетка", fontsize=11.5, color=AMBER, ha="center", weight="bold")
ax3.text(7.95, 1.0, "потомства не оставляет —\nпризнак не передаётся", fontsize=12.0,
         color=INK, va="center", linespacing=1.45)

fig.text(0.05, 0.278,
         "Проверка на числах: из 44 «новых» линий споры дала ОДНА. Если бы работал простой случай\n"
         "(нейтральный дрейф), таких линий было бы 18–23. Значит отбору не из чего выбирать.",
         fontsize=13.0, color=INK, va="top", linespacing=1.55)

# ================================================================ 4
fig.text(0.05, 0.228, "4. Что это значит — тремя фразами",
         fontsize=19, weight="bold", color=INK, va="top")
lines = [
    ("Место важнее размера.", "— росток гибнет не потому, что он мал, а потому что место занято."),
    ("Еда — не главное объяснение.", "— даже там, где еды вдоволь, чужая линия не приживается."),
    ("Отбор пока не измерить.", "— плодится колония, а не клетка: у признака нет пути к потомству."),
]
y = 0.202
for head, body in lines:
    fig.text(0.05, y, "•", fontsize=13, color=GREEN, va="top")
    fig.text(0.066, y, head, fontsize=13.0, weight="bold", color=INK, va="top")
    fig.text(0.066, y - 0.0145, body, fontsize=12.0, color=MUTED, va="top")
    y -= 0.031

# ================================================================ 5
fig.text(0.05, 0.098, "5. Что делаем дальше", fontsize=19, weight="bold", color=INK, va="top")
fig.text(0.05, 0.072,
         "Проверим последнего подозреваемого — «основание рядом с соседом» — на нескольких повторах.",
         fontsize=12.5, color=INK, va="top")
fig.text(0.05, 0.054,
         "И ответим на простой вопрос: кто в этом пруду считается отдельной особью. Без этого отбор не измерить.",
         fontsize=12.5, color=INK, va="top")
fig.text(0.05, 0.022,
         "Все числа — из артефактов прогонов (found_n1_seed1, разделы 10ak и 10aj).",
         fontsize=10.0, color=MUTED, va="top")

out = "reports/figures/day-2026-10-25-simple.png"
fig.savefig(out, facecolor=fig.get_facecolor(), dpi=100)
print("saved:", out)
