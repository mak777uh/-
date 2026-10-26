#!/usr/bin/env python
"""make_arxiv_figures.py — четыре фигуры для черновика (26.10).

Данные берутся ТОЛЬКО из агрегатов в git (`morphogenesis/experiments/E09_pond/*.json`).
Имена файлов: `reports/figures/2026-10-26-arxiv-fig{N}.png`.

    рис. 1 — I_obs против I_null(95 %) по сидам для четырёх конструкций размножения;
    рис. 2 — rho_partial по конструкциям (медиана + IQR), порог −0.3, невалидные серии помечены;
    рис. 3 — время до переписывания: keep против majority, по раскладкам и дозам;
    рис. 4 — (а) доля занятых подготовленных клеток против числа живых соседей;
             (б) парные разницы legacy − adjacency_exact по пригодным сидам.

Запуск (из корня):

    python scripts/make_arxiv_figures.py
"""
from __future__ import annotations

import json
import statistics
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
POND = ROOT / "morphogenesis" / "experiments" / "E09_pond"
OUT = ROOT / "reports" / "figures"
DPI = 200


def load(name: str) -> dict:
    return json.loads((POND / name).read_text(encoding="utf-8"))


def rows_of(agg: dict, arm: str) -> list[dict]:
    return [r for r in agg.get("rows", []) if r.get("arm") == arm]


def fig1() -> None:
    """I_obs против I_null по сидам: четыре конструкции."""
    cell = load("w2bud_rep_uniform_matrix.json")
    pair = load("w2bud_pair_matrix.json")
    pair_any = load("w2bud_pairany_matrix.json")
    colony = load("w2bud_rep_uniform_matrix.json")

    series = [
        ("cell-level budding", rows_of(cell, "cell"), "#1f77b4", "o"),
        ("pair, same tag", rows_of(pair, "pair"), "#ff7f0e", "s"),
        ("pair, any tag", rows_of(pair_any, "pair"), "#2ca02c", "^"),
        ("colony (control)", rows_of(colony, "colony"), "#7f7f7f", "D"),
    ]
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    for label, rows, color, marker in series:
        xs, ys = [], []
        for r in rows:
            obs, nul = r.get("I_obs"), r.get("I_null_95")
            if obs is None:
                continue
            xs.append(nul if nul is not None else 0.0)   # x = нуль
            ys.append(obs)                               # y = наблюдение
        if not xs:
            continue
        ax.scatter(xs, ys, label=label, color=color, marker=marker, s=42, alpha=0.85,
                   edgecolor="white", linewidth=0.6)
    lim = 2.4
    ax.plot([0, lim], [0, lim], color="black", lw=1.0, ls="--")
    ax.text(lim * 0.52, lim * 0.58, "$I_{obs} = I_{null}$", fontsize=8, rotation=38)
    ax.text(lim * 0.40, lim * 0.86, "excess over noise\n(above the line)", fontsize=7.5,
            color="#444444", ha="center")
    ax.set_xlim(-0.05, lim)
    ax.set_ylim(-0.05, lim)
    ax.set_xlabel("null model, $I_{null}$ (95 %)")
    ax.set_ylabel("observed opportunity for selection, $I_{obs}$")
    ax.set_title("Fig. 1. Selection opportunity against its null model\n"
                 "(points above the dashed line exceed demographic noise)", fontsize=9)
    ax.legend(fontsize=7.5, frameon=False, loc="upper left")
    ax.annotate("seeds 102 and 108:\na second lineage appeared", xy=(0.066, 1.55),
                xytext=(0.42, 1.72), fontsize=7, color="#444444",
                arrowprops=dict(arrowstyle="->", lw=0.8, color="#444444"))
    ax.grid(alpha=0.25, lw=0.5)
    fig.tight_layout()
    fig.savefig(OUT / "2026-10-26-arxiv-fig1.png", dpi=DPI)
    plt.close(fig)


def fig2() -> None:
    """rho_partial по конструкциям: медиана и IQR, порог −0.3."""
    configs = [
        ("uniform, N=1 (cell)", "w2bud4s_matrix.json"),
        ("N=3 buds, seeds 1–10", "w2budd2_matrix.json"),
        ("N=3 buds, seeds 101–110", "w2budd2_rep_matrix.json"),
        ("one bud per lineage", "w2bud_onebud_matrix.json"),
    ]
    fig, ax = plt.subplots(figsize=(6.6, 4.0))
    labels, medians, q1s, q3s, ns, evaluable, agg_valid = [], [], [], [], [], [], []
    for label, name in configs:
        agg = load(name)
        arm = "cell"
        vals = [r["rho_partial_energy"] for r in rows_of(agg, arm)
                if r.get("rho_partial_energy") is not None]
        by = [a for a in agg["by_arm"] if a["arm"] == arm]
        valid = by[0].get("valid_n", 0) if by else 0
        agg_valid.append(not bool(agg.get("criteria", {}).get("invalid_by_data")))
        labels.append(label)
        ns.append(len(vals))
        evaluable.append(len(vals) >= 3 and valid > 0)
        if len(vals) >= 2:
            medians.append(statistics.median(vals))
            q = statistics.quantiles(vals, n=4)
            q1s.append(q[0])
            q3s.append(q[2])
        else:
            medians.append(0.0)
            q1s.append(0.0)
            q3s.append(0.0)
    ys = range(len(labels))
    for i, (m, a, b, ok) in enumerate(zip(medians, q1s, q3s, evaluable)):
        invalid = not agg_valid[i]
        if ok:
            ax.plot([a, b], [i, i], color="#1f77b4", lw=5, alpha=0.45, solid_capstyle="butt")
            ax.plot([m], [i], "o" if not invalid else "o", ms=8,
                    markerfacecolor="white" if invalid else "#1f77b4",
                    markeredgecolor="#1f77b4", markeredgewidth=1.6)
            if invalid:
                ax.annotate("invalid by data", (m, i), textcoords="offset points",
                            xytext=(0, 11), fontsize=7, ha="center", color="#b22222")
        else:
            ax.text(-0.02, i, "not evaluable", va="center", ha="right",
                    fontsize=8, color="#b22222", style="italic")
    ax.axvline(-0.3, color="#b22222", ls="--", lw=1.2, label="criterion −0.3")
    ax.legend(fontsize=7.5, frameon=False, loc="upper right")
    ax.set_yticks(list(ys))
    ax.set_yticklabels([f"{l}\ncomputable n={n}" for l, n in zip(labels, ns)], fontsize=8)
    ax.set_xlim(-1.05, 0.25)
    ax.set_xlabel("partial rank correlation (trait vs cell-steps | energy)")
    ax.set_title("Fig. 2. Cost of the trait (median and IQR); negative = costlier", fontsize=9)
    fig.text(0.02, 0.035,
             "n = runs where the partial correlation is computable.\n"
             "The lineage gate (≥5 lineages) is a different denominator: 4/10 for N=3 replication, "
             "8/10 for one bud per lineage.",
             fontsize=6.5, color="#444444", ha="left", va="bottom")
    ax.grid(axis="x", alpha=0.25, lw=0.5)
    fig.tight_layout(rect=(0, 0.09, 1, 1))
    fig.savefig(OUT / "2026-10-26-arxiv-fig2.png", dpi=DPI)
    plt.close(fig)


def fig3() -> None:
    """Две панели: доля выживших и время до перезаписи (только для перезаписанных)."""
    uni = load("placement_matrix.json")
    pat = load("placement_patches_matrix.json")
    groups = [("uniform", "keep", uni, "#2ca02c"),
              ("uniform", "majority", uni, "#d62728"),
              ("patches", "keep", pat, "#2ca02c"),
              ("patches", "majority", pat, "#d62728")]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.8, 3.9))

    xs, shares, labels, colors = [], [], [], []
    for i, (layout, arm, agg, color) in enumerate(groups):
        rows = [r for r in agg["rows"] if r["arm"] == arm]
        surv = sum(1 for r in rows if (r.get("final_cells") or 0) > 0)
        xs.append(i)
        shares.append(surv / len(rows) if rows else 0.0)
        labels.append(f"{layout}\n{arm}")
        colors.append(color)
        ax1.text(i, surv / len(rows) + 0.04 if rows else 0.04, f"{surv}/{len(rows)}",
                 ha="center", fontsize=8)
    ax1.bar(xs, shares, color=colors, alpha=0.85)
    ax1.set_xticks(xs)
    ax1.set_xticklabels(labels, fontsize=8)
    ax1.set_ylim(0, 1.15)
    ax1.set_ylabel("share of runs where the invader survived")
    ax1.set_title("(a) survival of a 20-cell propagule", fontsize=9)
    ax1.grid(axis="y", alpha=0.25, lw=0.5)

    for i, (layout, arm, agg, color) in enumerate(groups):
        rows = [r for r in agg["rows"] if r["arm"] == arm]
        tt = [r["time_to_rewrite"] for r in rows if r.get("time_to_rewrite") is not None]
        if not tt:
            ax2.text(i, 50, "no overwrite\nin 10 runs\n(lifetime undefined)",
                     ha="center", va="center", fontsize=7, color=color, style="italic")
            continue
        ax2.scatter([i] * len(tt), tt, color=color, s=40, alpha=0.85,
                    edgecolor="white", linewidth=0.6)
        ax2.plot([i - 0.18, i + 0.18], [statistics.median(tt)] * 2, color=color, lw=2)
        ax2.text(i, 84, f"median {statistics.median(tt):.0f}", ha="center",
                 fontsize=7.5, color=color)
    ax2.set_xticks(range(len(groups)))
    ax2.set_xticklabels([f"{l}\n{a}" for l, a, _, _ in groups], fontsize=8)
    ax2.set_ylabel("steps until the invader is overwritten")
    ax2.set_ylim(0, 88)
    ax2.set_title("(b) lifetime, only runs that were overwritten", fontsize=9)
    ax2.grid(axis="y", alpha=0.25, lw=0.5)

    fig.suptitle("Fig. 3. Invasion of a 20-cell propagule: survival and lifetime", fontsize=9.5)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(OUT / "2026-10-26-arxiv-fig3.png", dpi=DPI)
    plt.close(fig)


def fig4() -> None:
    """(а) доля занятых против n4; (б) парные разницы legacy − exact."""
    agg = load("w1niche_matrix.json")
    levels: dict[int, list[int]] = {}
    for name in sorted((POND / "w1niche").glob("w1niche6_adjacency_exact_seed*.json")):
        summary = json.loads(name.read_text(encoding="utf-8")).get("summary") or {}
        for lvl, (prep, hit) in (summary.get("niche_levels") or {}).items():
            slot = levels.setdefault(int(lvl), [0, 0])
            slot[0] += int(prep)
            slot[1] += int(hit)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.6, 3.8))
    xs = sorted(levels)
    shares = [levels[x][1] / levels[x][0] for x in xs]
    ax1.plot(xs, shares, "o-", color="#1f77b4", ms=7)
    for x, s_ in zip(xs, shares):
        ax1.annotate(f"{levels[x][1]}/{levels[x][0]}", (x, s_), textcoords="offset points",
                     xytext=(0, -14), fontsize=6.5, ha="center", color="#444444")
    ax1.set_xlabel("number of live 4-neighbours at preparation")
    ax1.set_ylabel("share of prepared cells later occupied")
    ax1.set_ylim(0.6, 1.0)
    ax1.grid(alpha=0.25, lw=0.5)
    ax1.set_title("(a) occupancy grows with neighbour count", fontsize=9)

    leg = {r["seed"]: r for r in rows_of(agg, "legacy")}
    exact = {r["seed"]: r for r in rows_of(agg, "adjacency_exact")}
    seeds, diffs = [], []
    for s in sorted(set(leg) & set(exact)):
        a, b = leg[s], exact[s]
        if a.get("underpowered") or b.get("underpowered"):
            continue
        if a.get("same_share") is None or b.get("same_share") is None:
            continue
        seeds.append(s)
        diffs.append(a["same_share"] - b["same_share"])
    colors = ["#2ca02c" if d > 0 else "#d62728" for d in diffs]
    ax2.bar([str(s) for s in seeds], diffs, color=colors, alpha=0.85)
    ax2.axhline(0, color="black", lw=1.0)
    ax2.set_xlabel("seed")
    ax2.set_ylabel("legacy − adjacency_exact")
    ax2.set_title(f"(b) paired differences, n = {len(diffs)} evaluable seeds", fontsize=9)
    ax2.grid(axis="y", alpha=0.25, lw=0.5)
    ax2.tick_params(axis="x", labelsize=7.5)
    fig.tight_layout()
    fig.savefig(OUT / "2026-10-26-arxiv-fig4.png", dpi=DPI)
    plt.close(fig)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for fn in (fig1, fig2, fig3, fig4):
        fn()
        print(f"  {fn.__name__}: ok")
    print(f"фигуры в {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
