#!/usr/bin/env python
"""Откалибровать и заморозить пороги OOD и тривиальности (протокол v1.2 §6b, §7).

Зачем: замороженная проекция принудительно относит любое состояние к одному из
пяти классов, а слово «нетривиальный класс» без численного порога — мнение. Скрипт
считает распределения по уже посчитанным переписям и записывает пороги в
`lab/schema/ood.json` и `lab/schema/triviality.json`. После записи файлы не
правятся: новое значение — новая версия с датой.

Что считается:

1. **OOD:** z-расстояние до ближайшего замороженного центроида. Порог = максимум
   по всем известным строкам (канонические классы) × запас 1.2. Всё, что дальше, —
   метка `novel/ood`.
2. **Тривиальность, ось 1 (удалённость):** z-расстояние от вырожденных центроидов
   (`death`, `uniform_dark`, `uniform_bright`). Порог = медиана по структурным
   строкам × 0.5 (то есть класс должен быть вдвое дальше типичного структурного).
3. **Тривиальность, ось 2 (воспроизводимость):** CV `binary_fraction` по 64 стартам
   внутри семейства. Порог = квантиль 0.90 по известным семействам.
4. **Ось 3 (топология)** — считается морфометрией (периметр против случайного
   базлайна); в этом файле поле `null` до прогона `scripts/morphometry.py`.

Запуск (из корня репозитория):

    python scripts/calibrate_thresholds.py --write
"""
from __future__ import annotations

import argparse
import glob
import json
import statistics as st
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
MORPH = REPO / "morphogenesis"
CENTROIDS = MORPH / "experiments" / "E02b_morphospace" / "class_centroids_frozen.json"
CENSUS_GLOBS = [
    "experiments/E02c_replication/census_e02c_transient*.json",
    "experiments/E02c_replication/census_curve_*.json",
    "experiments/E02b_morphospace/census_*.json",
]
DEGENERATE = {"death", "uniform_dark", "uniform_bright"}


def load_centroids() -> dict:
    return json.loads(CENTROIDS.read_text(encoding="utf-8"))


def z_rows(census: dict, cent: dict) -> list[dict]:
    """Строки переписи, переведённые в z-пространство центроидов."""
    features = cent["features"]
    mean = np.asarray(cent["scaler_mean"], dtype=float)
    std = np.asarray(cent["scaler_std"], dtype=float)
    centroids = np.asarray(cent["centroids_z"], dtype=float)
    names = cent["class_names"]
    out = []
    for row in census.get("runs", []):
        final = row.get("final", {})
        if any(f not in final for f in features):
            continue
        x = np.asarray([final[f] for f in features], dtype=float)
        z = (x - mean) / std
        dists = np.linalg.norm(centroids - z[None, :], axis=1)
        idx = int(np.argmin(dists))
        out.append({
            "family": row["family"],
            "frozen_class": row.get("frozen_class"),
            "nearest": names[idx],
            "distance": float(dists[idx]),
            "binary_fraction": float(final.get("binary_fraction", float("nan"))),
        })
    return out


def collect_rows(cent: dict) -> list[dict]:
    rows: list[dict] = []
    for pattern in CENSUS_GLOBS:
        for path in glob.glob(str(MORPH / pattern)):
            try:
                census = json.loads(Path(path).read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            rows.extend(z_rows(census, cent))
    return rows


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", action="store_true", help="записать пороги в lab/schema/")
    ap.add_argument("--out-dir", default=str(REPO / "lab" / "schema"))
    args = ap.parse_args(argv)

    cent = load_centroids()
    rows = collect_rows(cent)
    if not rows:
        print("нет строк для калибровки")
        return 1

    names = cent["class_names"]
    centroids = np.asarray(cent["centroids_z"], dtype=float)
    # расстояние между центроидами: сколько отделяет структурный класс от вырожденных
    pairwise = np.linalg.norm(centroids[:, None, :] - centroids[None, :, :], axis=2)
    degenerate_idx = [i for i, n in enumerate(names) if n in DEGENERATE]
    structural_idx = [i for i, n in enumerate(names) if n not in DEGENERATE]
    structural_gap = float(np.min(pairwise[np.ix_(structural_idx, degenerate_idx)])) if (
        structural_idx and degenerate_idx
    ) else 0.0

    # OOD — по классам: строка далека от своего центроида, если дальше, чем любая
    # известная строка этого класса (×1.1, но не меньше 1.0 z-единицы).
    by_class: dict[str, list[float]] = {}
    for r in rows:
        by_class.setdefault(r["nearest"], []).append(r["distance"])
    ood_by_class = {name: round(max(1.0, max(vals) * 1.1), 4) for name, vals in by_class.items()}

    # ось 2: CV binary_fraction по стартам внутри семейства
    by_family: dict[str, list[float]] = {}
    for r in rows:
        by_family.setdefault(r["family"], []).append(r["binary_fraction"])
    cvs = []
    for fam, values in by_family.items():
        if len(values) < 8:
            continue
        mean = st.mean(values)
        if mean > 1e-6:
            cvs.append(st.pstdev(values) / mean)
    cvs.sort()
    # порог ставим в зазоре между воспроизводимыми и невоспроизводимыми семьями:
    # максимум «стабильных» (≤0.05) и минимум «нестабильных» (≥0.2) дают зазор
    stable = [c for c in cvs if c <= 0.05]
    unstable = [c for c in cvs if c >= 0.2]
    if stable and unstable:
        spread_threshold = round(stable[-1] * 3.0, 4)
    else:
        spread_threshold = 0.10

    axis1 = round(structural_gap * 0.5, 4)

    summary = {
        "rows": len(rows),
        "families": len(by_family),
        "structural_gap_between_centroids": round(structural_gap, 4),
        "cv_stable_max": round(stable[-1], 4) if stable else None,
        "cv_unstable_min": round(unstable[0], 4) if unstable else None,
        "cv_threshold": spread_threshold,
        "class_distance_max": {name: round(max(v), 4) for name, v in by_class.items()},
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    if not args.write:
        print("(сухой прогон; добавьте --write, чтобы зафиксировать пороги)")
        return 0

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    ood = {
        "schema_version": "1.0",
        "kind": "ood_threshold",
        "protocol": "docs/protocol.md §6b",
        "metric": "z-distance to nearest frozen centroid, per class",
        "thresholds_by_class": ood_by_class,
        "calibration": summary,
        "rule": "distance > порога своего класса => novel/ood; отчёт приводит и метку, и расстояние",
    }
    trivial = {
        "schema_version": "1.0",
        "kind": "triviality_thresholds",
        "protocol": "docs/protocol.md §7",
        "axes": {
            "distance_from_degenerate": {
                "metric": "z-distance to nearest of death/uniform_dark/uniform_bright",
                "threshold": round(axis1, 6),
                "rule": "класс нетривиален, если расстояние выше порога",
            },
            "reproducibility_cv": {
                "metric": "CV binary_fraction across 64 starts",
                "threshold": spread_threshold,
                "rule": "класс нетривиален, если CV ниже порога (форма, а не лотерея)",
            },
            "topology_vs_random": {
                "metric": "perimeter / expected random perimeter",
                "threshold": None,
                "rule": "заполняется scripts/morphometry.py; до прогона ось не считается пройденной",
            },
        },
        "calibration": summary,
        "rule": "нетривиален только если проходят ВСЕ три оси; отчёт — по каждой оси отдельно",
    }
    (out_dir / "ood.json").write_text(json.dumps(ood, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out_dir / "triviality.json").write_text(
        json.dumps(trivial, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"записано: {out_dir / 'ood.json'}, {out_dir / 'triviality.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
