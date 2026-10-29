"""entrainment.py — захватывает ли мир ритм входного потока (энтрейнмент), и связано ли это с «энергией».

Гипотеза владельца (29.10): контакт с живым в настоящем моменте соединяет систему с общим ритмом, это даёт
энергию и делает её «живой»; чем больше связь, тем больше энергии.

До сих пор мы мерили **разнообразие** (§10bo) и делали выводы о **связи**. Это разные величины: мир может
не менять число линий и при этом синхронизироваться с потоком. Энтрейнмент измеряется корреляцией
активности мира с входом на разных лагах.

Что считается для каждого прогона:
* `peak_r` — максимальная корреляция (Пирсон) между рядом входа и рядом активности мира по лагам;
* `peak_lag` — на каком лаге достигается максимум (в шагах);
* `coherence_ratio` — доля дисперсии активности, объяснённая входом на лучшем лаге (r²);
* `energy_ratio` — средняя энергия на клетку относительно контроля плеча (если есть контроль);
* `pop_time`, `types_alive` — «живость» в наших терминах.

Проверка нуля: у плеча `shuffle` (то же распределение, время разрушено) когерентность должна быть на уровне
шума; если у `real` она выше, значит мир действительно захватывает ритм, а не просто реагирует на средний
уровень.

Использование:
    python scripts/entrainment.py --src morphogenesis/experiments/E09_pond/w2bud_k3
    python scripts/entrainment.py --src <каталог> --out <json>
"""
from __future__ import annotations

import argparse
import glob
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def pearson(a: list[float], b: list[float]) -> float:
    n = min(len(a), len(b))
    if n < 3:
        return 0.0
    a, b = a[:n], b[:n]
    ma = sum(a) / n
    mb = sum(b) / n
    va = sum((x - ma) ** 2 for x in a)
    vb = sum((y - mb) ** 2 for y in b)
    if va <= 0 or vb <= 0:
        return 0.0
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    return cov / math.sqrt(va * vb)


STREAM_HINTS = {
    "real": "mic-2026-10-28.json",
    "iaaft": "mic_iaaft-2026-10-29.json",
    "shuffle": "mic_shuffle-2026-10-29.json",
}


def stream_for(run_name: str, stream_dir: Path | None) -> list[float]:
    """Ряд, который РЕАЛЬНО подавался в мир.

    Важно: `values_seen` пишется только в живом режиме (`--inflow-live`). При проигрывании файла
    (`--inflow-stream`) он пуст, и без этой подстановки корреляция считается с нулевым рядом — получаются
    «нули», которые выглядят как результат, а являются ошибкой чтения (поймано 29.10).
    """
    if stream_dir is None:
        return []
    for key, fname in STREAM_HINTS.items():
        if f"_{key}_" in f"_{run_name}_":
            f = stream_dir / fname
            if f.exists():
                raw = json.loads(f.read_text(encoding="utf-8"))
                return list(raw.get("values") or [])
    return []


def analyse_run(path: Path, stream_dir: Path | None = None) -> dict | None:
    d = json.loads(path.read_text(encoding="utf-8"))
    s = d.get("summary") or d
    stream = s.get("live_stream") or {}
    values = stream.get("values_seen") or stream_for(path.stem, stream_dir)
    series = s.get("event_series") or []
    if not series:
        return None
    # активность мира: births за интервал между срезами
    steps = [r.get("step") for r in series]
    births = [r.get("births") for r in series]
    act = []
    for i in range(1, len(series)):
        ds = (steps[i] or 0) - (steps[i - 1] or 0)
        db = (births[i] or 0) - (births[i - 1] or 0)
        act.append(db / ds if ds else 0.0)
    if len(act) < 5:
        return None

    if values:
        # приводим вход к той же длине: берём значения в моменты срезов
        n = len(act)
        m = len(values)
        fed = [values[int(round(i * (m - 1) / max(1, n - 1)))] for i in range(n)]
    else:
        fed = [0.0] * len(act)

    best_r, best_lag = 0.0, 0
    for lag in range(-10, 11):
        if lag >= 0:
            a, b = fed[: len(fed) - lag], act[lag:]
        else:
            a, b = fed[-lag:], act[: len(act) + lag]
        if len(a) < 5:
            continue
        r = pearson(a, b)
        if abs(r) > abs(best_r):
            best_r, best_lag = r, lag

    counts = s.get("type_counts") or {}
    alive = sum(counts.values()) or 0
    return {
        "run": path.stem,
        "peak_r": round(best_r, 3),
        "peak_lag": best_lag,
        "coherence_r2": round(best_r ** 2, 3),
        "pop_time": s.get("pop_time"),
        "types_alive": s.get("types_alive"),
        "alive": alive,
        "n_points": len(act),
        "has_stream": bool(values),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="энтрейнмент: захватывает ли мир ритм входа")
    ap.add_argument("--src", required=True)
    ap.add_argument("--out", default=None)
    ap.add_argument("--stream-dir", default="lab/streams",
                    help="где искать ряды, поданные через проигрывание (по имени плеча)")
    args = ap.parse_args(argv)

    files = sorted(Path(p) for p in glob.glob(str(Path(args.src) / "*.json")))
    rows = [r for r in (analyse_run(f, Path(args.stream_dir) if args.stream_dir else None) for f in files) if r]
    if not rows:
        print("[entrainment] нет прогонов с event_series")
        return 1

    rows.sort(key=lambda r: (r["run"].split("_")[2] if "_" in r["run"] else "", r["run"]))
    print(f"{'прогон':38s} {'peak_r':>7s} {'lag':>4s} {'r²':>6s} {'pop_time':>10s} {'линий':>6s}")
    for r in rows:
        print(f"{r['run'][:38]:38s} {r['peak_r']:7.3f} {r['peak_lag']:4d} {r['coherence_r2']:6.3f} "
              f"{str(r['pop_time']):>10s} {str(r['types_alive']):>6s}")

    # сводка по плечам (имя прогона вида w2bud_k3_<arm>_seed<N>)
    arms: dict[str, list[dict]] = {}
    for r in rows:
        parts = r["run"].split("_")
        arm = parts[2] if len(parts) > 2 else "?"
        arms.setdefault(arm, []).append(r)
    print("\nпо плечам (медиана |peak_r|):")
    for arm, rs in arms.items():
        vals = sorted(abs(x["peak_r"]) for x in rs)
        med = vals[len(vals) // 2]
        print(f"  {arm:10s} n={len(rs)} медиана |r| = {med:.3f}")

    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps({"runs": rows}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"\n[entrainment] записано: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
