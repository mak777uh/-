"""w2bud_quota_matrix.py — агрегат серии с квотой (H-ALIVE-53).

Зачем отдельный файл: общий агрегатор `w2bud_matrix.py` распознаёт плечи только по
именам `colony|cell|pair`, а у серии квоты плечи `cell`, `cellq50`, `cellq30`. Считать
заново метрику нельзя (получились бы два определения цены), поэтому здесь вызывается
`analyse()` из общего агрегатора, а этот файл добавляет только сравнение плеч.

Запуск: python scripts/w2bud_quota_matrix.py --src morphogenesis/experiments/E09_pond/w2bud_quota \\
          --out morphogenesis/experiments/E09_pond/w2bud_quota_matrix.json
"""
from __future__ import annotations

import argparse
import json
import statistics as st
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import re  # noqa: E402

import w2bud_matrix as _W  # noqa: E402

# Общий агрегатор распознаёт только плечи colony|cell|pair; для серии квоты расширяем шаблон,
# не трогая ни метрику, ни код: иначе `analyse` вернёт None и агрегат покажет «нет строк».
_W.NAME = re.compile(r"w2bud[\w]*_(?P<arm>colony|cell|cellq50|cellq30|pair)_seed(?P<seed>\d+)\.json$")
analyse = _W.analyse  # то же определение цены, без второго мнения

ARM_RE = {"cell": ("q=1.0", 1.0), "cellq50": ("q=0.5", 0.5), "cellq30": ("q=0.3", 0.3)}


def arm_of(name: str) -> str | None:
    stem = name.replace(".json", "")
    for arm in ARM_RE:
        if f"_{arm}_seed" in stem:
            return arm
    return None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--src", default="morphogenesis/experiments/E09_pond/w2bud_quota")
    ap.add_argument("--out", default="morphogenesis/experiments/E09_pond/w2bud_quota_matrix.json")
    args = ap.parse_args(argv)

    src = Path(args.src)
    rows: list[dict] = []
    for path in sorted(src.glob("*.json")):
        arm = arm_of(path.name)
        if arm is None:
            continue
        # общий агрегатор ищет имя по своему шаблону; подменяем имя на канонический вид
        res = analyse(path)
        if res is None:
            continue
        res["arm"] = arm
        res["arm_label"], res["quota"] = ARM_RE[arm]
        res["seed"] = int(path.stem.split("seed")[-1])
        summary = json.loads(path.read_text(encoding="utf-8")).get("summary") or {}
        res["buds_blocked_share"] = summary.get("buds_blocked_share")
        res["buds_blocked_by_quota"] = summary.get("buds_blocked_by_quota")
        rows.append(res)

    by_arm: dict[str, dict] = {}
    for arm in ARM_RE:
        sel = [r for r in rows if r["arm"] == arm]
        rhos = [r["rho_partial_energy"] for r in sel if r.get("rho_partial_energy") is not None]
        lines = [r.get("lineages_with_data") for r in sel
                 if r.get("lineages_with_data") is not None]
        blk = [r["buds_blocked_share"] for r in sel if r.get("buds_blocked_share") is not None]
        by_arm[arm] = {
            "arm_label": ARM_RE[arm][0],
            "quota": ARM_RE[arm][1],
            "runs": len(sel),
            "valid_n": len(rhos),
            "rho_partial_energy_median": round(st.median(rhos), 3) if rhos else None,
            "rho_partial_energy_negative": sum(1 for v in rhos if v < 0),
            "lineages_with_data_median": st.median(lines) if lines else None,
            "lineages_with_data_min": min(lines) if lines else None,
            "lineages_with_data_max": max(lines) if lines else None,
            "buds_blocked_share_median": round(st.median(blk), 3) if blk else None,
        }

    out = {
        "kind": "w2bud-quota-matrix",
        "world": "W2-bud with lineage quota (H-ALIVE-53)",
        "metric": {
            "rho_partial_energy": "частная ранговая корреляция признак → доля спор при контроле энергии "
                                   "(определение взято из w2bud_matrix.analyse, не переопределяется)",
            "lineages_with_data": "линий с >=5 клетками и >=1 споре — поле lineages_with_data "
                                  "общего агрегатора (MIN_CELLS = 5)",
            "buds_blocked_share": "заблокированные квотой деления / (заблокированные + успешные)",
        },
        "design": {"arms": {k: v[0] for k, v in ARM_RE.items()}, "seeds": "1–10",
                   "steps": 600, "one_bud_per_lineage": True},
        "by_arm": by_arm,
        "rows": rows,
    }
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n",
                             encoding="utf-8", newline="\n")
    print(f"[quota] {args.out}: строк {len(rows)}")
    for arm, v in by_arm.items():
        med = v["lineages_with_data_median"]
        span = f" ({v['lineages_with_data_min']}–{v['lineages_with_data_max']})" if med is not None else ""
        print(f"  {v['arm_label']}: прогонов {v['runs']} (ρ вычислима {v['valid_n']}) | "
              f"медиана ρ {v['rho_partial_energy_median']} | отрицательных {v['rho_partial_energy_negative']} | "
              f"линий с данными {med}{span} | заблокировано {v['buds_blocked_share_median']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
