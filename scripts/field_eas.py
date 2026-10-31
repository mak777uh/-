"""field_eas.py — две дороги сразу: дифференциал отбора (X37) и накопление новизны (X39).

Зачем. После §10dh-доп (форма не переносится, и ничто её не предсказывает) нужно ответить на два разных
вопроса **одними и теми же данными**:

1. **X37, дифференциал отбора.** Сдвиг среднего признака оказался вдвое меньше порога (§10dg-доп-2). Но сдвиг —
   грубая мера: он смешивает отбор с дрейфом. Тонкая мера — `S = mean(s при рождении у выживших) −
   mean(s при рождении у погибших)`. Она не зависит от общего тренда: если за признак платят, выжившие пришли в
   мир с другим признаком.

2. **X39, накопление новизны по Bedau–Packard, в форме Flow-Lenia.** Тип — бин признака `s`, активность типа
   накапливается через **массу** (площадь): `a_p(t) = [a_p(t−1) + M_p(t)] · I(p присутствует)`. Сравнение — с
   **нуль-моделью**: тот же прогон, где признак не влияет на распад (`beta = 0`). Всё, что выше тени, и есть
   накопление; всё, что не выше, — топтание.

Данные: прогоны `x37_sel_*` (beta = 1.2) и `x37_null_*` (beta = 0), поля `uid_outcomes` (uid, рождение, конец,
`s_at_birth`) и `series[].components_log` (uid, s, площадь по срезам).

Запуск:
    python scripts/field_eas.py --src ../_hourly --prefix x37 --out ../_hourly/x37_report.json
"""
from __future__ import annotations

import argparse
import glob
import json
import random
import statistics as st
from collections import defaultdict
from pathlib import Path


def load_runs(src: Path, prefix: str) -> dict[str, list[dict]]:
    arms: dict[str, list[dict]] = defaultdict(list)
    for f in sorted(glob.glob(str(src / f"{prefix}_*_s*.json"))):
        name = Path(f).name
        arm = name.split("_")[1]
        arms[arm].append(json.loads(Path(f).read_text(encoding="utf-8")))
    return arms


def selection_differential(run: dict) -> dict:
    """S по uid: признак при рождении у доживших до конца против погибших раньше."""
    outs = run.get("uid_outcomes") or []
    last_step = (run.get("series") or [{}])[-1].get("step", 0)
    alive = [o["s_at_birth"] for o in outs if o.get("s_at_birth") is not None and o["last"] >= last_step]
    dead = [o["s_at_birth"] for o in outs if o.get("s_at_birth") is not None and o["last"] < last_step]
    return {"n_alive": len(alive), "n_dead": len(dead),
            "mean_alive": st.mean(alive) if alive else None,
            "mean_dead": st.mean(dead) if dead else None,
            "S": (st.mean(alive) - st.mean(dead)) if alive and dead else None}


def activity(series: list[dict], nbins: int = 8) -> dict:
    """EAS в форме Flow-Lenia: тип = бин s, активность копится через площадь.

    a_p(t) = (a_p(t-1) + M_p(t)) если тип присутствует. Возвращает активность по типам и сводку.
    """
    acc: dict[int, float] = defaultdict(float)
    present_steps: dict[int, int] = defaultdict(int)
    for snap in series:
        cl = snap.get("components_log") or []
        per_bin: dict[int, float] = defaultdict(float)
        for c in cl:
            s = c.get("s")
            if s is None:
                continue
            b = int(round(float(s) * nbins)) % nbins
            per_bin[b] += float(c.get("area") or 0)
        for b, mass in per_bin.items():
            acc[b] += mass
            present_steps[b] += 1
    total = sum(acc.values()) or 1.0
    return {"activity_by_bin": {str(k): round(v, 2) for k, v in sorted(acc.items())},
            "share_by_bin": {str(k): round(v / total, 4) for k, v in sorted(acc.items())},
            "types_present": len(acc),
            "max_share": round(max(acc.values()) / total, 4) if acc else None}


def boot_ci(a: list[float], reps: int = 5000, seed: int = 11) -> tuple[float, float]:
    rng = random.Random(seed)
    meds = []
    for _ in range(reps):
        meds.append(st.median([rng.choice(a) for _ in a]))
    meds.sort()
    return meds[int(0.025 * len(meds))], meds[int(0.975 * len(meds))]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="X37 дифференциал отбора + X39 накопление")
    ap.add_argument("--src", default=str(Path(__file__).resolve().parents[1].parent / "_hourly"))
    ap.add_argument("--prefix", default="x37")
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    arms = load_runs(Path(args.src), args.prefix)
    report: dict = {"kind": "field_eas", "arms": {}, "not_claimed": [
        "число типов здесь — бины одного признака s, а не виды",
        "активность выше тени означает накопление, но не «эволюцию» в дарвиновском смысле",
    ]}

    for arm, runs in arms.items():
        S_vals = []
        rows = []
        for run in runs:
            sd = selection_differential(run)
            act = activity(run.get("series") or [])
            rows.append({"seed": (run.get("params") or {}).get("seed"),
                         "S": sd["S"], "n_alive": sd["n_alive"], "n_dead": sd["n_dead"],
                         "types_present": act["types_present"], "max_share": act["max_share"]})
            if sd["S"] is not None:
                S_vals.append(sd["S"])
        entry = {"n_runs": len(runs), "rows": rows,
                 "S_median": round(st.median(S_vals), 4) if S_vals else None,
                 "S_positive": sum(1 for v in S_vals if v > 0), "S_n": len(S_vals)}
        if len(S_vals) >= 3:
            lo, hi = boot_ci(S_vals)
            entry["S_boot95"] = [round(lo, 4), round(hi, 4)]
        report["arms"][arm] = entry

    Path(args.out).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"[eas] записано: {args.out}")
    for arm, e in report["arms"].items():
        print(f"  {arm}: прогонов {e['n_runs']}, S медиана {e['S_median']}, "
              f"положительных {e['S_positive']}/{e['S_n']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
