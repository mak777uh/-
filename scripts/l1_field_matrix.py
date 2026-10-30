"""l1_field_matrix.py — агрегат линии поля: медианы, разброс и интервалы по плечам.

Зачем. §4k рукописи опирается на 140 прогонов поля (неоднородность против гомогенного), которые до 30.10
лежали **вне репозитория** — в `_hourly/`. Утверждение без артефакта в git не проверяется внешним читателем,
поэтому артефакты перенесены в `morphogenesis/experiments/L1_field/`, а здесь собирается агрегат: медианы,
bootstrap-интервалы разницы и величины, на которые ссылается текст.

Метрики (все — по интегралу числа компонент за прогон, `series[].components`):
  * `components_integral` — среднее число компонент по срезам (основная метрика: конечный счётчик шумен, CV 0.8–0.9);
  * `components_final` — число компонент на последнем срезе (публикуется как иллюстрация);
  * `hill_q2` — `1/Σp²` по площадям последнего среза (нужна запись `areas`).

Плечи:
  * `homog` — однородный приток;
  * `static` — статичный пространственный узор;
  * `p300`, `p3000` — узор меняется с периодом 300 / 3000 шагов.

Использование:
    python scripts/l1_field_matrix.py --write                      # собрать агрегат
    python scripts/l1_field_matrix.py --check                      # сверить с артефактами (CI)
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import random
import statistics as st
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "morphogenesis" / "experiments" / "L1_field"
OUT = SRC / "l1_field_matrix.json"

ARMS = {
    "homog": ["x15_homog_s*.json", "x16_homog_s*.json", "x17_homog_s*.json", "n20_homog_s*.json",
              "x18_homog_s*.json"],
    "static": ["n20_static_s*.json", "x16_static_s*.json", "x17_static_s*.json",
               "x18_pattern_s*.json", "x21_pattern_s*.json"],
    "globalnoise": ["x18_globalnoise_s*.json", "x21_globalnoise_s*.json"],
    "p300": ["n20_p300_s*.json"],
    "p3000": ["x14_p3000_s*.json"],
    # H-L1-1: амплитуда узора 0.2 и 0.8 (статика и гомогенное плечо при той же амплитуде)
    "amp02_static": ["hl1_amp0.2_static_s*.json"],
    "amp02_homog": ["hl1_amp0.2_homog_s*.json"],
    "amp08_static": ["hl1_amp0.8_static_s*.json"],
    "amp08_homog": ["hl1_amp0.8_homog_s*.json"],
}
GRID_HINT = {"x16": 128, "x17": 96, "n20": 96, "x15": 96, "x14": 96}


def hills(areas):
    tot = sum(areas)
    if tot <= 0:
        return None
    p = [a / tot for a in areas if a > 0]
    return 1.0 / sum(x * x for x in p)


def load_arm(patterns):
    rows = []
    for pat in patterns:
        for f in sorted(glob.glob(str(SRC / pat))):
            path = Path(f)
            d = json.loads(path.read_text(encoding="utf-8"))
            ser = d.get("series") or []
            if not ser:
                continue
            comps = [r["components"] for r in ser]
            last = ser[-1]
            rows.append({
                "file": path.name,
                "grid": GRID_HINT.get(path.name.split("_")[0], None),
                "steps": last["step"],
                "components_integral": round(sum(comps) / len(comps), 4),
                "components_final": int(last["components"]),
                "hill_q2": round(hills(last["areas"]), 4) if last.get("areas") else None,
                "sigma": (d.get("params") or {}).get("s_ref"),
            })
    return rows


def boot_median_diff(a, b, reps=5000, seed=21):
    rng = random.Random(seed)
    diffs = []
    for _ in range(reps):
        sa = [rng.choice(a) for _ in a]
        sb = [rng.choice(b) for _ in b]
        diffs.append(st.median(sa) - st.median(sb))
    diffs.sort()
    return round(diffs[int(0.025 * len(diffs))], 3), round(diffs[int(0.975 * len(diffs))], 3)


def build():
    out = {"kind": "l1_field_matrix", "world": "L1_field",
           "note": ("агрегат линии поля: §4k рукописи и §§10cw–10cy. Основная метрика — интеграл числа компонент "
                    "по срезам; конечный счётчик шумен (CV 0.8–0.9) и публикуется как иллюстрация"),
           "metric": {
               "components_integral": "среднее число компонент по срезам прогона (series[].components)",
               "components_final": "число компонент на последнем срезе — шумная метрика, только для иллюстрации",
               "hill_q2": "1/Σp² по площадям компонент последнего среза (series[].areas)",
           },
           "by_arm": {}, "rows": []}
    for arm, pats in ARMS.items():
        rows = load_arm(pats)
        out["rows"].extend(rows)
        if not rows:
            out["by_arm"][arm] = {"n": 0}
            continue
        vals = [r["components_integral"] for r in rows]
        q2 = [r["hill_q2"] for r in rows if r["hill_q2"]]
        out["by_arm"][arm] = {
            "n": len(rows),
            "components_integral_median": round(st.median(vals), 3),
            "components_integral_mean": round(st.mean(vals), 3),
            "components_integral_sd": round(st.stdev(vals), 3) if len(vals) > 1 else None,
            "components_final_median": round(st.median([r["components_final"] for r in rows]), 3),
            "hill_q2_median": round(st.median(q2), 3) if q2 else None,
            "grids": sorted({r["grid"] for r in rows if r["grid"]}),
        }
    a = [r["components_integral"] for r in out["rows"] if r["file"] in {x["file"] for x in load_arm(ARMS["static"])}]
    b = [r["components_integral"] for r in out["rows"] if r["file"] in {x["file"] for x in load_arm(ARMS["homog"])}]
    if a and b:
        lo, hi = boot_median_diff(a, b)
        out["contrast_static_vs_homog"] = {
            "median_static": round(st.median(a), 3),
            "median_homog": round(st.median(b), 3),
            "median_difference": round(st.median(a) - st.median(b), 3),
            "bootstrap_95ci": [lo, hi],
            "zero_outside_ci": not (lo <= 0 <= hi),
            "n_static": len(a), "n_homog": len(b),
        }
    out["not_claimed"] = [
        "что эффект сохранится при другой амплитуде узора или другом его масштабе",
        "что «компонента» — это организм: это связная область поля по порогу, определённая постфактум",
        "что Hill q=2 ≈ 1 означает разнообразие: он означает доминирование одной структуры",
        "что живой сигнал с железа ведёт себя иначе, чем перемешанный: на 3 сидах различия не было",
    ]
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="агрегат линии поля")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)

    fresh = build()
    if args.write:
        OUT.write_text(json.dumps(fresh, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[l1] записано: {OUT.name} | плеч {len(fresh['by_arm'])} | строк {len(fresh['rows'])}")
    if args.check:
        if not OUT.exists():
            print("[l1] агрегата нет — запустите --write")
            return 1
        old = json.loads(OUT.read_text(encoding="utf-8"))
        if old.get("by_arm") != fresh.get("by_arm"):
            print("[l1] агрегат расходится с артефактами — пересоберите --write")
            return 1
        print("[l1] агрегат совпадает с артефактами")
    if not (args.write or args.check):
        c = fresh.get("contrast_static_vs_homog") or {}
        print(json.dumps(fresh["by_arm"], ensure_ascii=False, indent=1))
        if c:
            print("контраст статика↔гомогенно:", json.dumps(c, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
