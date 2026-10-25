#!/usr/bin/env python
"""make_day2_picture.py — картинка «что мы изучаем и как оно себя ведёт», простым языком.

Зачем: владелец просит глазами посмотреть, что за объекты и как они ведут себя за сутки.
Все числа берутся из артефактов, а не пишутся от руки: если артефакта нет, панель честно
пишет «нет данных», а не рисует красивое.

Панели:
  1. Мир: как растёт колония из одной клетки (реальная кривая из лога).
  2. Кто размножается: колония целиком или отдельная клетка (схема + реальные числа).
  3. Возможность отбора: I_obs против нуль-модели (реальные значения по сидам).
  4. Нашествие: сколько клеток просили подсадить и сколько реально легло.
  5. Цена признака: частная корреляция по сидам (направление, не вердикт).

Запуск (из корня):  python scripts/make_day2_picture.py
Выход:              reports/figures/day-2026-10-25-objects.png
"""
from __future__ import annotations

import json
import statistics as st
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle

ROOT = Path(__file__).resolve().parents[1]
POND = ROOT / "morphogenesis" / "experiments" / "E09_pond"
OUT = ROOT / "reports" / "figures" / "day-2026-10-25-objects.png"

C_BG = "#0f1620"
C_TEXT = "#e8eef5"
C_DIM = "#8fa3b8"
C_A = "#e4b363"      # пул A (еда резидента)
C_B = "#5aa9e6"      # пул B (еда инвайдера)
C_ALIVE = "#7bd389"
C_BAD = "#e05c5c"
C_ACC = "#b07be0"


def load(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def style(ax, title: str, subtitle: str = "") -> None:
    """Заголовок и подзаголовок рисуются вручную над осями: set_title + текст в transAxes
    накладывались друг на друга (проверено на рендере)."""
    ax.set_facecolor("#141c26")
    ax.text(0, 1.16, title, transform=ax.transAxes, color=C_TEXT, fontsize=15,
            fontweight="bold", va="bottom")
    if subtitle:
        ax.text(0, 1.055, subtitle, transform=ax.transAxes, color=C_DIM, fontsize=10,
                va="bottom")
    for spine in ax.spines.values():
        spine.set_color("#24313f")
    ax.tick_params(colors=C_DIM, labelsize=9)


def panel_growth(ax) -> None:
    """Реальная кривая роста колонии из одной клетки."""
    style(ax, "1. Мир: колония растёт из одной клетки",
          "пруд 32×32, еда возобновляется на месте")
    data = load(POND / "founding_matrix.json")
    alive = None
    if data:
        for row in data.get("rows", []):
            if row.get("n") == 1 and row.get("seed") == 1:
                alive = row.get("alive_final")
                art = load(ROOT / row["artifact"]) if row.get("artifact") else None
                if art:
                    log = art.get("log") or []
                    steps = [e.get("step") for e in log if isinstance(e.get("step"), int)]
                    cells = [e.get("alive_cells") for e in log]
                    cells = [c if isinstance(c, int) else None for c in cells]
                    pairs = [(s, c) for s, c in zip(steps, cells) if c is not None]
                    if pairs:
                        xs = [p[0] for p in pairs]
                        ys = [p[1] for p in pairs]
                        ax.plot(xs, ys, color=C_ALIVE, lw=2.2)
                        ax.fill_between(xs, ys, color=C_ALIVE, alpha=0.15)
                        ax.set_xlabel("шаг", color=C_DIM)
                        ax.set_ylabel("живых клеток", color=C_DIM)
                        ax.text(0.97, 0.08, f"в конце: {ys[-1]} клеток",
                                transform=ax.transAxes, ha="right", color=C_ALIVE, fontsize=11)
                        return
    ax.text(0.5, 0.5, "нет данных", ha="center", va="center", color=C_DIM, transform=ax.transAxes)


def panel_who_reproduces(ax) -> None:
    """Схема: колония целиком против отдельной клетки + реальные числа."""
    style(ax, "2. Кто оставляет потомство",
          "слева — потомство даёт вся колония, справа — отдельная клетка")
    ax.set_xlim(0, 10)
    ax.set_ylim(-1.8, 10)
    ax.axis("off")

    # слева: колониальное почкование
    ax.add_patch(Circle((2.5, 6.4), 1.5, color=C_ALIVE, alpha=0.85))
    for dx, dy in ((-0.5, 0.5), (0.4, -0.4), (0.1, 0.9)):
        ax.add_patch(Circle((2.5 + dx, 6.4 + dy), 0.32, color="#4f7f5c"))
    ax.annotate("", xy=(2.5, 3.6), xytext=(2.5, 4.8),
                arrowprops=dict(arrowstyle="-|>", color=C_DIM, lw=1.6))
    ax.add_patch(Circle((2.5, 2.9), 0.42, color=C_ALIVE))
    ax.add_patch(Circle((3.5, 2.9), 0.42, color=C_ALIVE))
    ax.text(2.5, 1.4, "W1: почкуется колония", ha="center", color=C_TEXT, fontsize=11)
    ax.text(2.5, 0.6, "метка линии не передаётся", ha="center", color=C_BAD, fontsize=9)

    # справа: клеточное почкование
    ax.add_patch(Circle((7.5, 6.4), 1.5, color=C_ALIVE, alpha=0.85))
    ax.add_patch(Circle((7.1, 6.8), 0.34, color=C_ACC))
    ax.add_patch(Circle((8.0, 6.0), 0.34, color=C_ALIVE, alpha=0.9))
    ax.annotate("", xy=(7.1, 3.6), xytext=(7.1, 4.8),
                arrowprops=dict(arrowstyle="-|>", color=C_ACC, lw=1.8))
    ax.add_patch(Circle((7.1, 2.9), 0.42, color=C_ACC))
    ax.add_patch(Circle((8.1, 2.9), 0.42, color=C_ACC))
    ax.text(7.5, 1.4, "W2-bud: почкуется клетка", ha="center", color=C_TEXT, fontsize=11)
    ax.text(7.5, 0.6, "метка линии наследуется", ha="center", color=C_ACC, fontsize=9)

    # реальные числа
    data = load(POND / "w2bud3_matrix.json")
    if data:
        arms = {a["arm"]: a for a in data.get("by_arm", [])}
        w1 = arms.get("colony", {}).get("tags_ge2_median")
        w2 = arms.get("cell", {}).get("tags_ge2_median")
        if w1 is not None and w2 is not None:
            ax.text(5.0, -1.1, f"линий с ≥2 клетками:  W1 = {w1:.1f}   →   W2-bud = {w2:.1f}",
                    ha="center", color=C_TEXT, fontsize=11, fontweight="bold")


def panel_selection(ax) -> None:
    """I_obs против нуль-модели по сидам."""
    style(ax, "3. Может ли отбор вообще работать",
          "разброс приспособленности линий: реальный против случайного")
    data = load(POND / "w2bud3_matrix.json")
    if not data:
        ax.text(0.5, 0.5, "нет данных", ha="center", va="center", color=C_DIM, transform=ax.transAxes)
        return
    obs, null = [], []
    for row in data.get("rows", []):
        if row.get("arm") != "cell":
            continue
        o = row.get("I_obs")
        n95 = row.get("I_null_95")
        if isinstance(o, (int, float)):
            obs.append(o)
            null.append(n95 if isinstance(n95, (int, float)) else 0.0)
    if not obs:
        ax.text(0.5, 0.5, "нет данных", ha="center", va="center", color=C_DIM, transform=ax.transAxes)
        return
    idx = list(range(1, len(obs) + 1))
    ax.bar([i - 0.2 for i in idx], obs, width=0.4, color=C_ACC, label="реально (I_obs)")
    ax.bar([i + 0.2 for i in idx], null, width=0.4, color=C_DIM, label="как при случайном счёте")
    arms = {a["arm"]: a for a in data.get("by_arm", [])}
    ratio = arms.get("cell", {}).get("I_ratio_median")
    ax.legend(facecolor="#141c26", edgecolor="#24313f", labelcolor=C_TEXT, fontsize=9, loc="upper left")
    ax.set_xlabel("прогон (сид)", color=C_DIM)
    ax.set_ylabel("возможность отбора", color=C_DIM)
    if ratio:
        ax.text(0.97, 0.92, f"выше случайного в {ratio:.1f}×", transform=ax.transAxes,
                ha="right", color=C_ACC, fontsize=12, fontweight="bold")


def panel_invasion(ax) -> None:
    """Сколько клеток просили подсадить и сколько легло."""
    style(ax, "4. Нашествие: чужая линия рядом с колонией",
          "подсадка 20 клеток — сколько реально поместилось")
    files = sorted((POND / "invdeath").glob("*.json")) if (POND / "invdeath").exists() else []
    req, actual, labels = [], [], []
    for f in files:
        s = load(f)
        if not s:
            continue
        summ = s.get("summary") or {}
        a = summ.get("invader_cells_actual")
        if isinstance(a, int):
            req.append(20)
            actual.append(a)
            labels.append(f.stem.replace("invdeath_", "").replace("_seed", "·"))
    if not actual:
        ax.text(0.5, 0.5, "серия идёт — данных пока нет", ha="center", va="center",
                color=C_DIM, transform=ax.transAxes)
        return
    idx = list(range(len(actual)))
    colors = [C_BAD if a < 15 else C_B for a in actual]
    ax.bar(idx, actual, color=colors)
    ax.axhline(20, color=C_DIM, ls="--", lw=1)
    ax.set_xticks(idx)
    ax.set_xticklabels(labels, rotation=60, ha="right", fontsize=7)
    ax.set_ylabel("клеток легло", color=C_DIM)
    bad = sum(1 for a in actual if a < 15)
    ax.text(0.98, 0.62, f"не встало целиком: {bad} из {len(actual)}", transform=ax.transAxes,
            ha="right", color=C_BAD, fontsize=11, fontweight="bold")


def panel_price(ax) -> None:
    """Частная корреляция признак ↔ клетко-шаги по сидам."""
    style(ax, "5. Цена признака: признак против роста",
          "отрицательно = «сильнее признак → меньше растёт»; это направление, не вердикт")
    data = load(POND / "w2bud4s_matrix.json")
    if not data:
        ax.text(0.5, 0.5, "нет данных", ha="center", va="center", color=C_DIM, transform=ax.transAxes)
        return
    vals = []
    for row in data.get("rows", []):
        v = row.get("rho_partial_energy")
        if isinstance(v, (int, float)):
            vals.append(v)
    if not vals:
        ax.text(0.5, 0.5, "нет данных", ha="center", va="center", color=C_DIM, transform=ax.transAxes)
        return
    colors = [C_ALIVE if v < 0 else C_BAD for v in vals]
    ax.bar(range(len(vals)), vals, color=colors)
    ax.axhline(0, color=C_DIM, lw=1)
    med = st.median(vals)
    ax.axhline(med, color=C_ACC, ls="--", lw=1.4)
    ax.set_xticks(range(len(vals)))
    ax.set_xticklabels([str(i + 1) for i in range(len(vals))], fontsize=8)
    ax.set_xlabel("сид, где корреляция посчитана", color=C_DIM)
    ax.set_ylabel("ρ при равной энергии", color=C_DIM)
    neg = sum(1 for v in vals if v < 0)
    ax.text(0.03, -0.30, f"отрицательных: {neg} из {len(vals)}, медиана {med:.2f}",
            transform=ax.transAxes, color=C_TEXT, fontsize=10)


def main() -> int:
    fig = plt.figure(figsize=(15.5, 12.4), facecolor=C_BG)
    gs = fig.add_gridspec(3, 2, hspace=0.62, wspace=0.20,
                          left=0.06, right=0.97, top=0.83, bottom=0.06)

    head = fig.add_axes([0.06, 0.915, 0.88, 0.075])
    head.axis("off")
    head.text(0, 0.72, "Что мы изучаем: цифровой пруд, линии и их судьба",
              color=C_TEXT, fontsize=20, fontweight="bold", va="top")
    head.text(0, 0.16, "25 октября 2026 · все числа взяты из артефактов прогонов, не из пересказа",
              color=C_DIM, fontsize=11, va="top")

    panel_growth(fig.add_subplot(gs[0, 0]))
    panel_who_reproduces(fig.add_subplot(gs[0, 1]))
    panel_invasion(fig.add_subplot(gs[1, 0]))
    panel_price(fig.add_subplot(gs[1, 1]))
    panel_selection(fig.add_subplot(gs[2, :]))

    note = ("Как читать: «линия» — потомки одной клетки с наследуемой меткой. "
            "Возможность отбора (панель 3) — насколько линии различаются по числу потомков; "
            "если это не выше случайного счёта, отбирать нечего.")
    fig.text(0.06, 0.015, note, color=C_DIM, fontsize=9.5)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=150, facecolor=C_BG)
    print(f"записано: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
