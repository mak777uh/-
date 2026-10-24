"""Постер «сутки лаборатории» — визуализация хода исследования для владельца.

Все числа взяты из артефактов линии E09_pond и рукописи (§10ab–§10ag, §4h, §5).
Верстка: сетка с фиксированными координатами, без наложений.
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


def section(fig, y_header, text):
    fig.text(0.05, y_header, text, fontsize=19, weight="bold", color=BLUE,
             va="top", ha="left")
    fig.patches.append(
        Rectangle((0.05, y_header - 0.0105), 0.90, 0.0014,
                  transform=fig.transFigure, facecolor=BLUE, edgecolor="none",
                  alpha=0.35, zorder=1)
    )


def card(fig, x, y, w, h, *, title, lines, big, verdict, colour):
    fig.patches.append(
        FancyBboxPatch((x, y), w, h,
                       boxstyle="round,pad=0.003,rounding_size=0.010",
                       transform=fig.transFigure, facecolor=WHITE,
                       edgecolor="#d9dee3", linewidth=1.2, zorder=2)
    )
    fig.patches.append(
        Rectangle((x, y), 0.0055, h, transform=fig.transFigure,
                  facecolor=colour, edgecolor="none", zorder=3)
    )
    ty = y + h - 0.014
    fig.text(x + 0.014, ty, title, fontsize=14.5, weight="bold", color=INK,
             va="top", ha="left")
    ty -= 0.0245
    for ln in lines:
        fig.text(x + 0.014, ty, ln, fontsize=11.6, color=MUTED, va="top", ha="left")
        ty -= 0.0142
    ty -= 0.004
    fig.text(x + 0.014, ty, big, fontsize=15.5, weight="bold", color=colour,
             va="top", ha="left")
    ty -= 0.0235
    fig.text(x + 0.014, ty, verdict, fontsize=11.2, color=colour, va="top",
             ha="left", style="italic")


fig = plt.figure(figsize=(FIG_W, FIG_H), dpi=100)
fig.patch.set_facecolor(LIGHT)

# ---------------------------------------------------------------- шапка
fig.patches.append(
    Rectangle((0, 0.948), 1, 0.052, transform=fig.transFigure,
              facecolor=INK, edgecolor="none", zorder=1)
)
fig.text(0.05, 0.977, "Лаборатория: что мы делали за сутки", fontsize=29,
         weight="bold", color=WHITE, va="center", ha="left")
fig.text(0.05, 0.960,
         "24–25 октября 2026 · цифровой пруд W1 (32×32, замороженное правило NCA) · все числа — из артефактов",
         fontsize=13, color="#c9d1d9", va="center", ha="left")
fig.text(0.95, 0.977, "6 серий · 601 тест", fontsize=12.5, color="#c9d1d9",
         va="center", ha="right")
fig.text(0.95, 0.960, "31 теорема · 0 выдуманных чисел", fontsize=12.5,
         color="#c9d1d9", va="center", ha="right")

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
     title="Доза и слияние (D + V8)",
     lines=["Дозы 1–20 клеток, два правила слияния;",
            "в одном прогоне пятно доросло до 36% популяции."],
     big="0 из 50 и 0 из 10",
     verdict="размер основателя не решает; слияние при 1% массы невидимо",
     colour=RED)

card(fig, col1, rows[2], cw, ch,
     title="Изменчивость метки (условие B)",
     lines=["Метка линии мутирует; мир её не читает.",
            "Появляется ли наследуемая новизна?"],
     big="10 из 10 сидов при m ≥ 0.05",
     verdict="новизна 14.7 на прогон, население не меняется — «бесплатно»",
     colour=GREEN)

card(fig, col2, rows[2], cw, ch,
     title="Отбор по признаку (условие E)",
     lines=["Признак начал влиять на мир (вложение энергии).",
            "Остановили на 4-м прогоне по правилу валидности."],
     big="споры произвела 1 линия из 44",
     verdict="мерить отбор нечем: размножение — колония, а не клетка",
     colour=RED)

# ---------------------------------------------------------------- 2. выводы
section(fig, 0.535, "2 · Три вещи, которые мы поняли — и они меняют план")

box_w, box_h = 0.2833, 0.198
box_y = 0.288
boxes = [
    ("«Основание — не барьер»",
     ["Одна клетка на свободном поле даёт колонию",
      "в 500–700 клеток, в 50 прогонах из 50.",
      "Значит нули во вторжениях — не про размер",
      "основателя, а про соседа.",
      "",
      "Дальше вопрос не «может ли линия",
      "основаться», а «почему её съедает",
      "резидент»."], GREEN),
    ("«Отбору не из чего выбирать»",
     ["Размножение в пруду — почкование колонии,",
      "а не клетки. Спора уходит от крупных клеток,",
      "поэтому новая метка рождается, но не",
      "размножается: 1 линия из 44 против 18–23",
      "у нейтрального дрейфа.",
      "",
      "Сначала нужно понять, КТО здесь индивид,",
      "и только потом мерить отбор."], RED),
    ("«Правило не консервативно»",
     ["Из полностью мёртвого поля правило",
      "зажигает все 1024 клетки на первом шаге —",
      "и это не зависит ни от ресурса, ни от",
      "дохода. Канал живости смещён положительно.",
      "",
      "Отсюда гейт (клетка без живого соседа",
      "не зажигается) и теорема: пустое поле",
      "остаётся пустым."], AMBER),
]
for x, (head, body, colour) in zip([0.05, 0.3583, 0.6667], boxes):
    fig.patches.append(
        FancyBboxPatch((x, box_y), box_w, box_h,
                       boxstyle="round,pad=0.003,rounding_size=0.010",
                       transform=fig.transFigure, facecolor=WHITE,
                       edgecolor="#d9dee3", linewidth=1.2, zorder=2)
    )
    fig.patches.append(
        Rectangle((x, box_y + box_h - 0.007), box_w, 0.007,
                  transform=fig.transFigure, facecolor=colour,
                  edgecolor="none", zorder=3)
    )
    fig.text(x + 0.013, box_y + box_h - 0.017, head, fontsize=14.5,
             weight="bold", color=colour, va="top", ha="left")
    ty = box_y + box_h - 0.038
    for ln in body:
        fig.text(x + 0.013, ty, ln, fontsize=11.3, color=INK, va="top", ha="left")
        ty -= 0.0155

# ---------------------------------------------------------------- 3. лестница
section(fig, 0.275, "3 · Лестница условий: где мы стоим")

ladder = [
    ("A. Информация", "есть: клетка видит ресурс и соседей", GREEN, "готово"),
    ("B. Изменчивость", "наследуемая новизна при m ≥ 0.05, бесплатно", GREEN, "готово"),
    ("C. Память среды", "наследие живёт 1.3–2.4 поколения · выгода не проверена", AMBER, "наполовину"),
    ("D. Сосуществование", "инвазия 0/50 и 0/10 — линия не удерживается", RED, "не вышло"),
    ("E. Отбор", "нечем измерять: единица размножения — колония", GRAY, "заблокировано"),
]
ly = 0.232
for name, status, colour, tag in ladder:
    fig.patches.append(
        FancyBboxPatch((0.05, ly), 0.90, 0.024,
                       boxstyle="round,pad=0.0015,rounding_size=0.006",
                       transform=fig.transFigure, facecolor=WHITE,
                       edgecolor="#e3e7ea", linewidth=1.0, zorder=2)
    )
    fig.patches.append(
        Rectangle((0.05, ly), 0.0045, 0.024, transform=fig.transFigure,
                  facecolor=colour, edgecolor="none", zorder=3)
    )
    fig.text(0.061, ly + 0.012, name, fontsize=12.8, weight="bold", color=INK,
             va="center", ha="left")
    fig.text(0.235, ly + 0.012, status, fontsize=11.6, color=MUTED,
             va="center", ha="left")
    fig.text(0.943, ly + 0.012, tag, fontsize=11.2, weight="bold", color=colour,
             va="center", ha="right")
    ly -= 0.0315

# ---------------------------------------------------------------- 4. дальше
section(fig, 0.062, "4 · Куда движемся")
fig.text(0.05, 0.048,
         "1) Логгер родословной: метка должна наследоваться при росте — без этого отбор не измерить.",
         fontsize=12.2, color=INK, va="top", ha="left")
fig.text(0.05, 0.034,
         "2) Пилот на 1–2 сидах: станет ли меток с ≥2 клетками 15–25 (как у нейтрального дрейфа).",
         fontsize=12.2, color=INK, va="top", ha="left")
fig.text(0.05, 0.020,
         "3) Слияние «без переписывания»: проверить, съедает ли линию правило слияния.",
         fontsize=12.2, color=INK, va="top", ha="left")
fig.text(0.05, 0.006,
         "4) И только потом — энергетика среды и повторный вопрос сосуществования.",
         fontsize=12.2, color=INK, va="top", ha="left")

out = r"reports/figures/day-2026-10-25.png"
fig.savefig(out, facecolor=fig.get_facecolor(), dpi=100)
print("saved:", out)
