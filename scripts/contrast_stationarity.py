"""contrast_stationarity.py — стационарен ли контраст «неоднородность минус однородность».

Зачем. 31.10 обнаружилось, что главное число линии (+3.57 компоненты) — это **интеграл по времени**, включающий
раннюю переходную фазу. Разбивка по четвертям физического времени показывает спад с +4.00 до плато +1.00 при
`dt = 1.0` и до нуля при `dt = 0.5`. Такое нельзя показывать одной цифрой без оговорки об оценке, и нельзя считать
скриптом из временного каталога.

Две оценки, обе законны и дают разные числа:

* `median_of_means` — медиана по сидам от временных средних (наш агрегат `l1_field_x56_matrix.json`);
* `pooled` — медиана пула срезов (взвешивает каждый срез, показывает динамику).

Здесь считается вторая, по четвертям физического времени, и печатается рядом с первой.

Запуск:
    python scripts/contrast_stationarity.py
    python scripts/contrast_stationarity.py --write       # записать агрегат
"""
from __future__ import annotations

import argparse
import json
import statistics as st
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "l1_field_stationarity.json"

SERIES = [
    ("dt=1.0, 12000 шагов", "x17_static_s*.json", "x17_homog_s*.json"),
    ("dt=1.0, 6000 шагов", "x18_pattern_s*.json", "x18_homog_s*.json"),
    ("dt=0.5, 12000 шагов", "x56_dt0.5_static_s*.json", "x56_dt0.5_homog_s*.json"),
]
QUARTERS = 4


def series_of(path: Path) -> list[tuple[float, int]]:
    d = json.loads(path.read_text(encoding="utf-8"))
    out = []
    for i, s in enumerate(d.get("series") or []):
        out.append((float(s.get("step") if s.get("step") is not None else i), int(s["components"])))
    return out


def collect(pattern: str) -> dict[int, list[tuple[float, int]]]:
    out: dict[int, list[tuple[float, int]]] = {}
    for p in sorted(L1.glob(pattern)):
        try:
            seed = int(p.stem.split("_s")[-1])
        except ValueError:
            continue
        out[seed] = series_of(p)
    return out


def pooled_contrast(het, hom, lo: float, hi: float) -> dict | None:
    vh, vo = [], []
    for seed in sorted(set(het) & set(hom)):
        for arr, acc in ((het[seed], vh), (hom[seed], vo)):
            steps = [s for s, _ in arr]
            smin, smax = min(steps), max(steps)
            span = (smax - smin) or 1.0
            acc.extend(c for s, c in arr if lo <= (s - smin) / span < hi)
    if not vh or not vo:
        return None
    h, o = st.median(vh), st.median(vo)
    return {"hetero": round(h, 3), "homog": round(o, 3), "contrast": round(h - o, 3),
            "n_slices": len(vh)}


def median_of_means(het, hom) -> float | None:
    diffs = []
    for seed in sorted(set(het) & set(hom)):
        mh = st.mean([c for _, c in het[seed]])
        mo = st.mean([c for _, c in hom[seed]])
        diffs.append(mh - mo)
    return round(st.median(diffs), 3) if diffs else None


def build() -> dict:
    rows = []
    for label, ph, po in SERIES:
        het, hom = collect(ph), collect(po)
        seeds = sorted(set(het) & set(hom))
        if not seeds:
            rows.append({"series": label, "n_seeds": 0})
            continue
        quarters = []
        for q in range(QUARTERS):
            lo = q / QUARTERS
            hi = (q + 1) / QUARTERS + (0.01 if q == QUARTERS - 1 else 0.0)
            r = pooled_contrast(het, hom, lo, hi)
            if r:
                quarters.append({"window": f"{q+1}/{QUARTERS}", **r})
        rows.append({"series": label, "n_seeds": len(seeds), "quarters": quarters,
                     "median_of_means": median_of_means(het, hom)})
    return {
        "kind": "l1_field_stationarity", "experiment": "X57 (pending)",
        "command": "python scripts/contrast_stationarity.py --write",
        "metric": {
            "pooled": "медиана пула срезов в окне (взвешивает каждый срез)",
            "median_of_means": "медиана по сидам от временных средних (наша основная оценка, как в агрегате X56)",
        },
        "design": {"quarters": QUARTERS, "note": "окна по доле физического времени каждого прогона"},
        "by_series": rows,
        "not_claimed": [
            "прогоны не длиннее 12 000 единиц: выход плато в ноль при dt=1.0 не проверен — это X57",
            "две оценки дают разные числа по построению; сравнивать можно только одинаковые",
        ],
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="стационарность контраста")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    data = build()
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[stationarity] записано: {OUT.name}")
    for row in data["by_series"]:
        if not row.get("n_seeds"):
            print(f"  {row['series']}: нет данных"); continue
        qs = " | ".join("%s %+0.2f" % (q["window"], q["contrast"]) for q in row["quarters"])
        print("  %-22s n=%2d | по четвертям: %s | медиана средних %+0.2f" % (
            row["series"], row["n_seeds"], qs, row.get("median_of_means") or float("nan")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
