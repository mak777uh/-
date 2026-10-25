"""Постер «сутки лаборатории» для владельца (версия 2, после ночных серий).

Все числа — из артефактов линии E09_pond и разделов 10ab–10al мира/рукописи.
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

INK = "#1f2933"
MUTED = "#5c6773"
GREEN = "#2e7d5b"
AMBER = "#b8860b"
RED = "#a63d40"
GRAY = "#7b8794"
LIGHT = "#eef1f4"
WHITE = "#ffffff"
BLUE = "#2f5d8a"

FIG_W, FIG_H = 19.0, 28.0


def section(fig, y, text):
    fig.text(0.05, y, text, fontsize=19, weight="bold", color=BLUE, va="top", ha="left")
    fig.patches.append(
        Rectangle((0.05, y - 0.0105), 0.90, 0.0014, transform=fig.transFigure,
                  facecolor=BLUE, edgecolor="none", alpha=0.35, zorder=1)
    )


def card(fig, x, y, w, h, *, title, lines, big, verdict, colour):
    fig.patches.append(
        FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.003,rounding_size=0.010",
                       transform=fig.transFigure, facecolor=WHITE,
                       edgecolor="#d9dee3", linewidth=1.2, zorder=2)
    )
    fig.patches.append(
        Rectangle((x, y), 0.0055, h, transform=fig.transFigure,
                  facecolor=colour, edgecolor="none", zorder=3)
    )
    ty = y + h - 0.014
    fig.text(x + 0.014, ty, title, fontsize=14.0, weight="bold", color=INK, va="top", ha="left")
    ty -= 0.024
    for ln in lines:
        fig.text(x + 0.014, ty, ln, fontsize=11.4, color=MUTED, va="top", ha="left")
        ty -= 0.014
    ty -= 0.004
    fig.text(x + 0.014, ty, big, fontsize=15.0, weight="bold", color=colour, va="top", ha="left")
    ty -= 0.023
    fig.text(x + 0.014, ty, verdict, fontsize=11.0, color=colour, va="top", ha="left", style="italic")


fig = plt.figure(figsize=(FIG_W, FIG_H), dpi=100)
fig.patch.set_facecolor(LIGHT)

# ---------------------------------------------------------------- шапка
fig.patches.append(Rectangle((0, 0.948), 1, 0.052, transform=fig.transFigure,
                             facecolor=INK, edgecolor="none", zorder=1))
fig.text(0.05, 0.977, "Лаборатория: сутки 24–25 октября", fontsize=29, weight="bold",
         color=WHITE, va="center", ha="left")
fig.text(0.05, 0.960,
         "цифровой пруд W1 (32×32, замороженное правило NCA) · все числа — из артефактов, ни одного «примерно»",
         fontsize=13, color="#c9d1d9", va="center", ha="left")
fig.text(0.95, 0.977, "≈150 прогонов · 605 тестов", fontsize=12.5, color="#c9d1d9",
         va="center", ha="right")
fig.text(0.95, 0.960, "31 теорема · 8 агрегатов", fontsize=12.5, color="#c9d1d9",
         va="center", ha="right")

# ---------------------------------------------------------------- 1. серии
section(fig, 0.935, "1 · Шесть серий: что проверяли и что вышло")

cw, ch = 0.435, 0.113
col1, col2 = 0.05, 0.515
rows = [0.812, 0.687, 0.562]

card(fig, col1, rows[0], cw, ch,
     title="Порог основания: может ли колония начаться с нуля?",
     lines=["Пустое поле + гейт зажигания, N клеток, 50 прогонов.",
            "Сколько клеток нужно, чтобы основать колонию?"],
     big="50 из 50 — хватает ОДНОЙ клетки",
     verdict="порога нет: 1 клетка → 520–665 клеток",
     colour=GREEN)

card(fig, col2, rows[0], cw, ch,
     title="Гейт зажигания: чего он стоит",
     lines=["Тот же прогон с гейтом и без — сравнение один-в-один.",
            "Оказалось, правило умеет зажигать клетки само."],
     big="670 клеток с гейтом против 449 без",
     verdict="мир другой: без гейта 4.9% рождений не прирастают к телу",
     colour=AMBER)

card(fig, col1, rows[1], cw, ch,
     title="Вторжение редкой линии (V8)",
     lines=["50 прогонов: сажаем чужую линию в колонию —",
            "в плотную, в свободное место, крупной дозой."],
     big="0 из 10 выживших — во всех пяти вариантах",
     verdict="посадить можно, закрепиться нельзя; доза 20 тоже гибнет",
     colour=RED)

card(fig, col2, rows[1], cw, ch,
     title="Слияние «без переписывания»",
     lines=["Клетки сохраняют тип при слиянии — меньшинство",
            "не переписывается. Якорь сошёлся бит-в-бит."],
     big="2 из 10 против 0 из 10",
     verdict="«направление есть, мощность мала»: держатся на 0.2–0.3 %",
     colour=AMBER)

card(fig, col1, rows[2], cw, ch,
     title="Изменчивость метки (условие B)",
     lines=["Метка линии мутирует; мир её не читает.",
            "Появляется ли наследуемая новизна?"],
     big="10 из 10 сидов при m ≥ 0.05",
     verdict="новизна 14.7 на прогон, население не меняется — «бесплатно»",
     colour=GREEN)

card(fig, col2, rows[2], cw, ch,
     title="Родословная и отбор (условие E)",
     lines=["Логгер исправлен: клетка наследует метку предка.",
            "Пилот: меток с ≥2 клетками — 2 из 47."],
     big="2 метки против 18–23 у дрейфа",
     verdict="бухгалтерия не причина: мутанты рождаются, но не основываются",
     colour=RED)

# ---------------------------------------------------------------- 2. исключения
section(fig, 0.535, "2 · Что мы за сутки исключили — и что осталось")

ew, eh = 0.172, 0.150
ey = 0.352
items = [
    ("Размер основания", ["доза 20 клеток —", "0/10; пятно доросло", "до 36 % и погибло"], RED),
    ("Правило слияния", ["без переписывания —", "2/10, доля", "всего 0.2–0.3 %"], RED),
    ("Бухгалтерия меток", ["логгер починен —", "2 метки с ≥2 клетками", "против 18–23 у дрейфа"], RED),
    ("Ресурс в точке", ["в точку подсадки —", "ресурс 0.9811,", "линия всё равно гибнет"], RED),
]
exs = [0.05, 0.245, 0.440, 0.635]
for x, (head, body, colour) in zip(exs, items):
    fig.patches.append(
        FancyBboxPatch((x, ey), ew, eh, boxstyle="round,pad=0.003,rounding_size=0.010",
                       transform=fig.transFigure, facecolor="#fbf3f3",
                       edgecolor="#e3c9c9", linewidth=1.2, zorder=2)
    )
    fig.text(x + 0.010, ey + eh - 0.010, "✗", fontsize=19, color=colour, va="top",
             ha="left", weight="bold")
    fig.text(x + 0.036, ey + eh - 0.017, head, fontsize=12.0, weight="bold",
             color=INK, va="top", ha="left")
    ty = ey + eh - 0.052
    for ln in body:
        fig.text(x + 0.010, ty, ln, fontsize=9.8, color=MUTED, va="top", ha="left")
        ty -= 0.0135

sx, sw = 0.828, 0.122
fig.patches.append(
    FancyBboxPatch((sx, ey), sw, eh, boxstyle="round,pad=0.003,rounding_size=0.010",
                   transform=fig.transFigure, facecolor="#fff8e6",
                   edgecolor=AMBER, linewidth=2.0, zorder=2)
)
fig.text(sx + 0.010, ey + eh - 0.010, "?", fontsize=19, color=AMBER, va="top",
         ha="left", weight="bold")
fig.text(sx + 0.010, ey + eh - 0.042, "Основание\nпропагула\nрядом с\nколонией",
         fontsize=11.2, weight="bold", color=AMBER, va="top", ha="left", linespacing=1.25)
fig.text(sx + 0.010, ey + 0.010, "1 клетка даёт\nколонию 50/50 —\nтолько на пустом поле",
         fontsize=9.0, color=INK, va="bottom", ha="left", linespacing=1.3)

fig.text(0.05, ey - 0.016,
         "Четыре объяснения проверены и отброшены числом. Осталось одно, и оно согласуется со всеми: "
         "редкая линия не может основаться там, где место занято.",
         fontsize=11.6, color=INK, va="top", ha="left", style="italic")

# ---------------------------------------------------------------- 3. лестница
section(fig, 0.312, "3 · Лестница условий: где мы стоим")

ladder = [
    ("A. Информация", "есть: клетка видит ресурс и соседей", GREEN, "готово"),
    ("B. Изменчивость", "наследуемая новизна при m ≥ 0.05, бесплатно", GREEN, "готово"),
    ("C. Память среды", "наследие живёт 1.3–2.4 поколения · выгода не проверена", AMBER, "наполовину"),
    ("D. Сосуществование", "0/10 при любом размещении, 2/10 без переписывания", RED, "не вышло"),
    ("E. Отбор", "нечем измерять: единица размножения — колония", GRAY, "заблокировано"),
]
ly = 0.269
for name, status, colour, tag in ladder:
    fig.patches.append(
        FancyBboxPatch((0.05, ly), 0.90, 0.024, boxstyle="round,pad=0.0015,rounding_size=0.006",
                       transform=fig.transFigure, facecolor=WHITE, edgecolor="#e3e7ea",
                       linewidth=1.0, zorder=2)
    )
    fig.patches.append(
        Rectangle((0.05, ly), 0.0045, 0.024, transform=fig.transFigure,
                  facecolor=colour, edgecolor="none", zorder=3)
    )
    fig.text(0.061, ly + 0.012, name, fontsize=12.6, weight="bold", color=INK, va="center", ha="left")
    fig.text(0.235, ly + 0.012, status, fontsize=11.4, color=MUTED, va="center", ha="left")
    fig.text(0.943, ly + 0.012, tag, fontsize=11.0, weight="bold", color=colour, va="center", ha="right")
    ly -= 0.0315

# ---------------------------------------------------------------- 4. дальше
section(fig, 0.098, "4 · Куда движемся")
steps = [
    "1) Проверить оставшегося подозреваемого: ресурсные зоны на 2–3 сидах (сейчас один сид — это направление, а не доказательство).",
    "2) Вернуть чувствительность проверке наследования среды: порог двигать ценой шага (own* = 0.30), а не доходом — доход управляет и выеденностью.",
    "3) Ответить на вопрос «кто здесь индивид»: пока единица размножения — колония, отбор по клеточной метке измерить нечем.",
    "4) И только после этого — новая формулировка условия E и новая пре-регистрация, а не ещё одна серия «на удачу».",
]
ty = 0.080
for s in steps:
    fig.text(0.05, ty, s, fontsize=11.6, color=INK, va="top", ha="left")
    ty -= 0.0185

out = "reports/figures/day-2026-10-25.png"
fig.savefig(out, facecolor=fig.get_facecolor(), dpi=100)
print("saved:", out)
