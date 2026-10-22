"""Собрать два рисунка по закрытиям carriers/кластеров из сырых артефактов.

Зачем: рукопись сейчас имеет только PCA-рисунок; результаты по носителям формы и
по асимметрии опираются на текст. Оба рисунка строятся из уже закоммиченных
артефактов, без GPU и без новых измерений:

1. `e02b_carrier_map.png` — карта носителей: доля повторов, в которых форма/тело
   восстановились, по условиям разных экспериментов (H-CH-1, H-CH-2/3/4, H-CH-6,
   H-CH-7, H-CH-8), для `struct_2` и для необученной архитектуры.
2. `e02b_asymmetry_pairs.png` — все пары с выровненной массой из трёх
   экспериментов (H-AB-2, H-AB-5, H-AB-6): разность IoU лево/право как функция
   доли удалённого; видно, что знак устойчив, а величина — нет.

Запуск (из корня репозитория):

    python scripts/make_carrier_figures.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
EXP = REPO / "morphogenesis" / "experiments" / "E02b_morphospace"
FIG = REPO / "reports" / "figures"

S2 = "WP4_R-9_s2000_seed42"
UNTRAINED = "untrained_current_arch"
REPEATS = 12


def load(name: str) -> dict:
    return json.loads((EXP / name).read_text(encoding="utf-8"))


def fraction(n: int) -> float:
    return n / REPEATS


def carrier_rows() -> list[tuple[str, str, int]]:
    """(группа, подпись, доля восстановления 0..12) для struct_2."""
    rows: list[tuple[str, str, int]] = []

    cm = load("channel_memory_exploratory.json")
    model = next(m for m in cm["models"] if m["family"] == S2)
    labels = {
        "none": "intact",
        "visible_zeroed": "visible=0",
        "hidden_zeroed": "hidden=0",
        "hidden_shuffled": "hidden shuffled",
    }
    for cond in model["conditions"]:
        rows.append(("H-CH-1 where the form lives", f"{labels[cond['condition']]} · pattern", cond["same_pattern_n"]))

    cl = load("closures_exploratory.json")
    model = next(m for m in cl["models"] if m["family"] == S2)
    worst = min(
        (summary["same_pattern"] for cond, summary in model["ch2"].items() if cond != "none"),
        default=0,
    )
    rows.append(("H-CH-2 channels", f"worst hidden subset · pattern", worst))
    rows.append(("H-CH-3 orientation", "visible=0 · same orientation", model["ch3"]["identity_orientation"]))
    rows.append(("H-CH-4 minimum", "visible=0 & hidden=0 · pattern", model["ch4"]["same_pattern"]))

    ao = load("alive_open_exploratory.json")
    model = next(m for m in ao["models"] if m["family"] == S2)
    rows.append(("H-CH-6 gate", "alive open everywhere · body", model["conditions"]["alive_open"]["body_returned"]))

    c2 = load("carriers2_exploratory.json")
    model = next(m for m in c2["models"] if m.get("ch7"))
    rows.append(
        (
            "H-CH-7 visible",
            "visible=0 + gate open · body",
            model["ch7"]["visible_zeroed_alive_open"]["body_returned"],
        )
    )

    c3 = load("clusters3_exploratory.json")
    model = next(m for m in c3["models"] if m.get("ch8"))
    rows.append(("H-CH-8 group", "only channels 2-7 · body", model["ch8"]["group_a_only"]["body_returned"]))
    rows.append(("H-CH-8 group", "only channels 8-14 · body", model["ch8"]["group_b_only"]["body_returned"]))
    return rows


def untrained_rows() -> list[tuple[str, int]]:
    out: list[tuple[str, int]] = []
    cm = load("channel_memory_exploratory.json")
    model = next(m for m in cm["models"] if m["family"] == UNTRAINED)
    cond = next(c for c in model["conditions"] if c["condition"] == "visible_zeroed")
    out.append(("H-CH-1 visible=0 · pattern", cond["same_pattern_n"]))
    cl = load("closures_exploratory.json")
    model = next(m for m in cl["models"] if m["family"] == UNTRAINED)
    out.append(("H-CH-4 visible=0 & hidden=0 · pattern", model["ch4"]["same_pattern"]))
    c3 = load("clusters3_exploratory.json")
    model = next(m for m in c3["models"] if m["family"] == UNTRAINED)
    out.append(("H-CH-8 only 2-7 · body", model["ch8"]["group_a_only"]["body_returned"]))
    out.append(("H-CH-8 only 8-14 · body", model["ch8"]["group_b_only"]["body_returned"]))
    return out


def draw_carrier_map(rows, control_rows, out: Path) -> None:
    colors = {
        "H-CH-1 where the form lives": "#4C72B0",
        "H-CH-2 channels": "#55A868",
        "H-CH-3 orientation": "#8172B2",
        "H-CH-4 minimum": "#C44E52",
        "H-CH-6 gate": "#DD8452",
        "H-CH-7 visible": "#937860",
        "H-CH-8 group": "#64B5CD",
    }
    fig, axes = plt.subplots(1, 2, figsize=(13.2, 5.6), gridspec_kw={"width_ratios": [2.1, 1.0]})

    labels = [f"{name}\n{cond}" for name, cond, _n in rows]
    values = [fraction(n) for _g, _c, n in rows]
    bar_colors = [colors[name] for name, _c, _n in rows]
    ypos = range(len(rows))
    axes[0].barh(list(ypos), values, color=bar_colors, edgecolor="black", linewidth=0.4)
    axes[0].set_yticks(list(ypos))
    axes[0].set_yticklabels(labels, fontsize=8)
    axes[0].invert_yaxis()
    axes[0].set_xlim(0, 1.05)
    axes[0].axvline(11 / REPEATS, color="black", linestyle=":", linewidth=1)
    axes[0].set_xlabel("fraction of 12 repeats where the form / body returned")
    axes[0].set_title("struct_2 (R-9 seed42): what survives each ablation", fontsize=10)
    for y, value, (_g, _c, n) in zip(ypos, values, rows):
        axes[0].text(value + 0.02, y, f"{n}/12", va="center", fontsize=8)
    axes[0].grid(axis="x", alpha=0.25)

    t_labels = [f"{cond}" for cond, _n in control_rows]
    t_values = [fraction(n) for _c, n in control_rows]
    axes[1].barh(range(len(control_rows)), t_values, color="#9E9E9E", edgecolor="black", linewidth=0.4)
    axes[1].set_yticks(range(len(control_rows)))
    axes[1].set_yticklabels(t_labels, fontsize=8)
    axes[1].invert_yaxis()
    axes[1].set_xlim(0, 1.05)
    axes[1].set_xlabel("fraction of 12")
    axes[1].set_title("untrained architecture (control)", fontsize=10)
    for y, n in zip(range(len(control_rows)), [n for _c, n in control_rows]):
        axes[1].text(fraction(n) + 0.02, y, f"{n}/12", va="center", fontsize=8)
    axes[1].grid(axis="x", alpha=0.25)

    fig.suptitle(
        "E02b carriers: the form survives texture loss, body loss and channel loss — "
        "but not in the untrained control",
        fontsize=11,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=160)
    plt.close(fig)
    print(f"[fig] {out.name}: {out.stat().st_size} bytes")


def asymmetry_pairs() -> list[tuple[float, float, str]]:
    pairs: list[tuple[float, float, str]] = []
    cl = load("closures_exploratory.json")
    model = next(m for m in cl["models"] if m.get("ab2"))
    for p in model["ab2"]["pairs"]:
        if p["valid"]:
            pairs.append((p["removed_fraction_left"], p["diff"], "H-AB-2 (q 0.15-0.49)"))
    c2 = load("carriers2_exploratory.json")
    model = next(m for m in c2["models"] if m.get("ab5"))
    for p in model["ab5"]["pairs"]:
        if p["valid"]:
            pairs.append((p["removed_fraction_left"], p["diff"], "H-AB-5 (q 0.50-0.70)"))
    c3 = load("clusters3_exploratory.json")
    model = next(m for m in c3["models"] if m.get("ab6"))
    for p in model["ab6"]["pairs"]:
        if p["valid"]:
            pairs.append((p["removed_fraction_left"], p["diff"], "H-AB-6 (q 0.55-0.65 dense)"))
    return pairs


def draw_asymmetry(pairs, out: Path) -> None:
    colors = {
        "H-AB-2 (q 0.15-0.49)": "#4C72B0",
        "H-AB-5 (q 0.50-0.70)": "#DD8452",
        "H-AB-6 (q 0.55-0.65 dense)": "#55A868",
    }
    fig, ax = plt.subplots(figsize=(9.2, 5.2))
    for label in colors:
        xs = [q for q, _d, lab in pairs if lab == label]
        ys = [d for _q, d, lab in pairs if lab == label]
        ax.scatter(xs, ys, s=42, color=colors[label], edgecolor="black", linewidth=0.4, label=label, zorder=3)
    ax.axhline(0.0, color="black", linewidth=1)
    ax.set_xlabel("removed fraction of live cells (mass-matched left/right cut)")
    ax.set_ylabel("IoU(left cut) - IoU(right cut)")
    negatives = sum(1 for _q, d, _l in pairs if d < 0)
    ax.set_title(
        f"E02b asymmetry: {negatives}/{len(pairs)} mass-matched pairs are negative, "
        "but the magnitude is not a function of the removed fraction",
        fontsize=10,
    )
    ax.legend(fontsize=8, loc="lower right")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=160)
    plt.close(fig)
    print(f"[fig] {out.name}: {out.stat().st_size} bytes; pairs={len(pairs)}; negative={negatives}")


def main() -> int:
    rows = carrier_rows()
    control = untrained_rows()
    draw_carrier_map(rows, control, FIG / "e02b_carrier_map.png")
    draw_asymmetry(asymmetry_pairs(), FIG / "e02b_asymmetry_pairs.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
