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
    r"w2bud[\w]*_(?P<arm>colony|cell|cellkw02|cellkw05|pair)_seed(?P<seed>\d+)\.json$")
ARMS = {"cell": 0.0, "cellkw02": 0.02, "cellkw05": 0.05}


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
                    help="порог пре-регистрации для медианы и верхней границы ДИ")
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

    verdict = {}
    for arm, d in by_arm.items():
        verdict[arm] = {
            "median_below_threshold": (d["rho_median"] is not None and d["rho_median"] < args.criterion),
            "upper_ci_below_threshold": (d["ci_high"] is not None and d["ci_high"] < args.criterion),
            "criterion_met": bool(d["rho_median"] is not None and d["ci_high"] is not None
                                  and d["rho_median"] < args.criterion and d["ci_high"] < args.criterion),
        }

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
        "criterion_threshold": args.criterion,
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
              f"pop_time {d['pop_time_median']} | критерий: {'ВЫПОЛНЕН' if verdict[arm]['criterion_met'] else 'не выполнен'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
