"""w2bud_killwinner_matrix.py — агрегат серий kill-the-winner (H-ALIVE-54/55).

Зачем отдельный файл: общий `w2bud_matrix.py` распознаёт плечи только по именам
`colony|cell|pair`, а у этих серий плечи `cell`, `cellkw02`, `cellkw05`. Метрику не
переопределяем: вызываем `analyse()` общего агрегатора, а здесь добавляем сравнение
плеч, среднее по Фишеру и проверку критерия пре-регистрации.

Запуск:
    python scripts/w2bud_killwinner_matrix.py --src morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm \\
        --out morphogenesis/experiments/E09_pond/w2bud_killwinner_confirm_matrix.json
"""
from __future__ import annotations

import argparse
import json
import math
import re
import statistics as st
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import w2bud_matrix as W  # noqa: E402

W.NAME = re.compile(
    r"w2bud[\w]*_(?P<arm>colony|cell|cellkw02|cellkw05|cellupd|cellp10|cellp07|cellp05|cellp10kw|cellp05kw|horizonc|horizonp05|horizonboth|k2_ctrl|k2_async|k3_real|k3_iaaft|k3_shuffle|k3_const|live_net|live_system|live_crypto|liverhythm_net|liverhythm_system|liverhythm_crypto|pair)_seed(?P<seed>\d+)\.json$")
ARMS = {"cell": 0.0, "cellkw02": 0.02, "cellkw05": 0.05, "cellupd": 0.05,
        "cellp10": 1.0, "cellp07": 0.7, "cellp05": 0.5,
        "cellp10kw": 1.0, "cellp05kw": 0.5,
        "horizonc": 1.0, "horizonp05": 0.5, "horizonboth": 0.5,
        "k2_ctrl": 1.0, "k2_async": 0.5,
        "k3_real": 0.454, "k3_iaaft": 0.454, "k3_shuffle": 0.454, "k3_const": 0.454,
        "live_net": 0.0, "live_system": 0.0, "live_crypto": 0.0,
        "liverhythm_net": 0.0, "liverhythm_system": 0.0, "liverhythm_crypto": 0.0}


def fisher(values: list[float]) -> tuple[float | None, float | None, float | None, float | None]:
    n = len(values)
    if n < 2:
        return (None, None, None, None)
    z = [math.atanh(max(-0.999999, min(0.999999, v))) for v in values]
    mz = sum(z) / n
    sd = st.stdev(z)
    se = sd / math.sqrt(n)
    return (math.tanh(mz), math.tanh(mz - 1.96 * se), math.tanh(mz + 1.96 * se), sd)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--src", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--criterion", type=float, default=-0.3,
                    help="порог пре-регистрации для медианы и верхней границы ДИ (ценовой критерий)")
    ap.add_argument("--criterion-kind", default="price", choices=["price", "coexistence", "none"],
                    help="какой критерий записан в пре-регистрации: price (ρ), coexistence (1/Σp² и линии) "
                         "или none. Смешивать нельзя: иначе агрегат серии про сосуществование несёт "
                         "ценовой verdict и читается как провал (B-089)")
    ap.add_argument("--control-arm", default=None,
                    help="плечо-контроль для coexistence-критерия (например cellp10)")
    args = ap.parse_args(argv)

    src = Path(args.src)
    rows: list[dict] = []
    for path in sorted(src.glob("*.json")):
        r = W.analyse(path)
        if r is None:
            continue
        s = json.loads(path.read_text(encoding="utf-8")).get("summary") or {}
        cells = {str(k).lstrip("T"): int(v) for k, v in (s.get("type_counts") or {}).items()}
        tot = sum(cells.values()) or 1
        p = [v / tot for v in cells.values() if v > 0]
        r["effective_lineages"] = round(1.0 / sum(x * x for x in p), 3) if p else None
        r["pop_time"] = s.get("pop_time")
        r["kill_winner_death_share"] = s.get("kill_winner_death_share")
        r["git_code_commit"] = (s.get("config") or {}).get("git_code_commit")
        rows.append(r)

    by_arm: dict[str, dict] = {}
    for arm, s_val in ARMS.items():
        sel = [r for r in rows if r.get("arm") == arm]
        if not sel:
            continue
        rhos = [r["rho_partial_energy"] for r in sel if r.get("rho_partial_energy") is not None]
        center, lo, hi, sd = fisher(rhos)
        lines = [r["lineages_with_data"] for r in sel if r.get("lineages_with_data") is not None]
        eff = [r["effective_lineages"] for r in sel if r.get("effective_lineages") is not None]
        pop = [r["pop_time"] for r in sel if r.get("pop_time")]
        share = [r["kill_winner_death_share"] for r in sel if r.get("kill_winner_death_share") is not None]
        by_arm[arm] = {
            "kill_winner": s_val,
            "runs": len(sel),
            "valid_n": len(rhos),
            "seeds_without_rho": len(sel) - len(rhos),
            "rho_median": round(st.median(rhos), 3) if rhos else None,
            "fisher_center": round(center, 3) if center is not None else None,
            "ci_low": round(lo, 3) if lo is not None else None,
            "ci_high": round(hi, 3) if hi is not None else None,
            "sd_z": round(sd, 3) if sd is not None else None,
            "lineages_with_data_median": st.median(lines) if lines else None,
            "effective_lineages_median": round(st.median(eff), 3) if eff else None,
            "pop_time_median": st.median(pop) if pop else None,
            "death_share_median": round(st.median(share), 3) if share else None,
        }

    verdict: dict[str, dict] = {}
    coexistence: dict[str, dict] = {}
    if args.criterion_kind == "price":
        for arm, d in by_arm.items():
            verdict[arm] = {
                "median_below_threshold": (d["rho_median"] is not None and d["rho_median"] < args.criterion),
                "upper_ci_below_threshold": (d["ci_high"] is not None and d["ci_high"] < args.criterion),
                "criterion_met": bool(d["rho_median"] is not None and d["ci_high"] is not None
                                      and d["rho_median"] < args.criterion and d["ci_high"] < args.criterion),
            }
    elif args.criterion_kind == "coexistence":
        ctrl = args.control_arm or next(iter(by_arm))
        base = by_arm.get(ctrl) or {}
        base_eff = base.get("effective_lineages_median")
        base_lin = base.get("lineages_with_data_median")
        for arm, d in by_arm.items():
            eff_r = (d["effective_lineages_median"] / base_eff) if (base_eff and d.get("effective_lineages_median")) else None
            lin_r = (d["lineages_with_data_median"] / base_lin) if (base_lin and d.get("lineages_with_data_median")) else None
            coexistence[arm] = {
                "control_arm": ctrl,
                "effective_lineages_ratio_vs_control": round(eff_r, 3) if eff_r else None,
                "lineages_ratio_vs_control": round(lin_r, 3) if lin_r else None,
                "criterion_met": bool(arm != ctrl and eff_r is not None and eff_r >= 3.0
                                      and lin_r is not None and lin_r >= 2.0),
            }
        verdict = coexistence

    out = {
        "kind": "w2bud-killwinner-matrix",
        "world": "W2-bud with kill-the-winner mortality (H-ALIVE-54/55)",
        "metric": {
            "rho_partial_energy": "частная ранговая корреляция признак → клетко-шаги клетки при контроле "
                                   "энергии по времени; определение взято из w2bud_matrix.analyse",
            "effective_lineages": "1/Σp² по живым клеткам (обратный индекс Симпсона)",
            "fisher_center": "tanh(среднее artanh ρ) по прогонам с вычислимой ρ",
            "ci": "по z: mean ± 1.96·SD/√n, обратно tanh",
            "death_share": "доля смертей, созданных механизмом (killed / died_total)",
        },
        "not_claimed": [
            "что мир ведёт себя так же при другом размере поля или другом правиле",
            "что величина воспроизведётся на другой видеокарте (окружение в манифестах, но не в агрегате)",
            "что выбранный критерий — единственный разумный для этой серии",
            "что числа остаются теми же при другом горизонте прогона",
        ],
        "criterion_kind": args.criterion_kind,
        "criterion_threshold": (args.criterion if args.criterion_kind == "price" else None),
        "criterion_note": ("цена: медиана и верхняя граница ДИ ρ < порога" if args.criterion_kind == "price"
                           else "сосуществование: 1/Σp² ≥ 3× контроля и линий ≥ 2× контроля"
                           if args.criterion_kind == "coexistence"
                           else "критерий этой серии считается отдельным инструментом "
                                "(для взаимодействия — scripts/additivity_interaction.py); "
                                "агрегат одной серии о нём не судит"),
        "by_arm": by_arm,
        "verdict": verdict,
        "provenance": {
            "git_code_commit": sorted({r["git_code_commit"] for r in rows if r.get("git_code_commit")}),
            "series_mask": str(src.name),
        },
        "rows": rows,
    }
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n",
                             encoding="utf-8", newline="\n")
    print(f"[killwinner] {args.out}: строк {len(rows)}")
    for arm, d in by_arm.items():
        print(f"  {arm} (s={d['kill_winner']}): прогонов {d['runs']}, ρ {d['valid_n']} | "
              f"медиана {d['rho_median']} | Фишер {d['fisher_center']} [{d['ci_low']}, {d['ci_high']}] | "
              f"линий {d['lineages_with_data_median']} | 1/Σp² {d['effective_lineages_median']} | "
              f"pop_time {d['pop_time_median']} | критерий: "
              f"{'не оценивается (criterion_kind=none)' if arm not in verdict else ('ВЫПОЛНЕН' if verdict[arm]['criterion_met'] else 'не выполнен')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
