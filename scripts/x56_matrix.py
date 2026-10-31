"""x56_matrix.py — сходимость по шагу: контраст при dt = 1.0, 0.5, 2.0.

Зачем. Все числа линии поля получены при `dt = 1.0`. Стандартная проверка solution verification — меняется ли
результат при измельчении схемы — не делалась ни разу до 31.10. Здесь она сделана: то же физическое время
(`dt × steps = 6000`), два плеча, 10 сидов.

Мера — **временное среднее числа компонент** (наш стандарт для этой величины), не последний срез: у среза CV 0.78–0.93.

Запуск:
    python scripts/x56_matrix.py --write
    python scripts/x56_matrix.py
"""
from __future__ import annotations

import argparse
import json
import statistics as st
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_x56_matrix.json"

DT = [
    ("dt=1.0 (baseline)", "x18_pattern_s*.json", "x18_homog_s*.json", 1.0),
    ("dt=0.5", "x56_dt0.5_static_s*.json", "x56_dt0.5_homog_s*.json", 0.5),
    ("dt=2.0", "x56_dt2.0_static_s*.json", "x56_dt2.0_homog_s*.json", 2.0),
]


def integral(path: Path) -> float | None:
    d = json.loads(path.read_text(encoding="utf-8"))
    vals = [s["components"] for s in d.get("series") or []]
    return sum(vals) / len(vals) if vals else None


def collect(pattern: str) -> dict[int, float]:
    out: dict[int, float] = {}
    for p in sorted(L1.glob(pattern)):
        try:
            seed = int(p.stem.split("_s")[-1])
        except ValueError:
            continue
        v = integral(p)
        if v is not None:
            out[seed] = v
    return out


def build() -> dict:
    rows = []
    for label, pat_het, pat_hom, dt in DT:
        het, hom = collect(pat_het), collect(pat_hom)
        common = sorted(set(het) & set(hom))
        if not common:
            rows.append({"label": label, "dt": dt, "n": 0})
            continue
        hv = [het[s] for s in common]
        ov = [hom[s] for s in common]
        rows.append({
            "label": label, "dt": dt, "n": len(common),
            "hetero_median": round(st.median(hv), 3), "hetero_sd": round(st.pstdev(hv), 3),
            "homog_median": round(st.median(ov), 3), "homog_sd": round(st.pstdev(ov), 3),
            "contrast": round(st.median(hv) - st.median(ov), 3),
            "seeds": common,
        })
    base = next((r for r in rows if r.get("dt") == 1.0 and r.get("n")), None)
    for r in rows:
        if base and r.get("n"):
            r["contrast_rel"] = round(r["contrast"] / base["contrast"], 3) if base["contrast"] else None
    return {
        "kind": "l1_field_x56_matrix", "experiment": "X56",
        "command": "python scripts/x56_matrix.py --write",
        "metric": {
            "contrast": "медиана временного среднего числа компонент: неоднородный минус однородный",
            "note": "временное среднее по всем срезам, а не последний срез (у среза CV 0.78–0.93)",
        },
        "design": {"physical_time": 6000, "steps": {"1.0": 6000, "0.5": 12000, "2.0": 3000},
                   "grid": 96, "laplacian": "4 neighbours, periodic", "integrator": "explicit Euler"},
        "by_dt": rows,
        "not_claimed": [
            "при dt = 2.0 мир нестабилен: живых структур почти нет, контраст неинформативен — это предел схемы",
            "сетка 96 ниже диапазона, проверенного Пирсоном (256–1024), см. library/lit-reading-list.md",
            "10 сидов на точку; интервалы не считались",
        ],
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="сходимость по шагу")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    data = build()
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[x56] записано: {OUT.name}")
    for r in data["by_dt"]:
        if not r.get("n"):
            print(f"  {r['label']}: нет данных"); continue
        print("  %-18s n=%2d | неоднор. %5.2f | однор. %5.2f | контраст %+6.2f | от базового %s" % (
            r["label"], r["n"], r["hetero_median"], r["homog_median"], r["contrast"],
            f"{r.get('contrast_rel'):.0%}" if r.get("contrast_rel") is not None else "—"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
