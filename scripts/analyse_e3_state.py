"""analyse_e3_state.py — сравнение по СОСТОЯНИЮ, а не по времени.

Проблема наивного теста E3: плечо `slow` к шагу 300 отстаёт (13 клеток против 405–562), поэтому «сошлись ли
траектории после 300» — тривиально нет: разные состояния, а не разная история.

Правильный тест марковости: **сравнить будущее из сопоставимого состояния**. Для каждого медленного прогона
находим шаг `t*`, где население впервые достигает населения контроля на шаге 300 (эталон `n*`), и сравниваем
`q1` на `t* + k` с `q1` контроля на `300 + k`.

Если при равном населении будущее совпадает — состояние достаточно, история не важна (марковость на этом
уровне). Если расходится — история влияет.
"""
import glob
import json
import statistics as st
from pathlib import Path

ROOT = Path(r"C:\Users\Admin\Documents\Qoder\2026-10-18\82ab86cd\repo")
SRC = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "w2bud_e3"


def series_of(path):
    s = json.loads(path.read_text(encoding="utf-8"))["summary"]
    out = []
    for r in s.get("type_counts_series") or []:
        counts = {str(k).lstrip("T"): int(v) for k, v in r["counts"].items()}
        total = sum(counts.values()) or 1
        probs = [v / total for v in counts.values() if v > 0]
        out.append({"step": r["step"], "alive": total,
                    "q1": round(1.0 / sum(p * p for p in probs), 3) if probs else 0.0})
    return out


def at(series, step):
    if not series:
        return None
    return min(series, key=lambda x: abs(x["step"] - step))


def first_at_least(series, n):
    for r in series:
        if r["alive"] >= n:
            return r
    return None


def main():
    runs = {}
    for f in sorted(SRC.glob("w2bud_e3_*.json")):
        arm = f.stem.replace("w2bud_e3_", "").rsplit("_seed", 1)[0]
        runs.setdefault(arm, []).append(series_of(f))
    if not runs.get("const"):
        print("нет контроля")
        return 1

    ref_step = 300
    refs = [at(s, ref_step) for s in runs["const"]]
    refs = [r for r in refs if r]
    n_star = int(st.median([r["alive"] for r in refs]))
    print(f"эталон: контроль на шаге {ref_step}, население {n_star} (по {len(refs)} сидам)")
    print(f"q1 контроля при этом: {[r['q1'] for r in refs]}")

    for arm in ("slow", "fast"):
        if not runs.get(arm):
            continue
        print(f"\nплечо {arm}:")
        for i, s in enumerate(runs[arm]):
            hit = first_at_least(s, n_star)
            if not hit:
                print(f"  сид{i}: не догнал эталонное население")
                continue
            t_star = hit["step"]
            print(f"  сид{i}: догнал на шаге {t_star} (население {hit['alive']}, q1 {hit['q1']})")
            for k in (0, 100, 200):
                a = at(s, t_star + k)
                b = at(refs[0] if False else runs["const"][i] if i < len(runs["const"]) else runs["const"][0], ref_step + k)
                if a and b:
                    print(f"     +{k:3d}: q1 {a['q1']:5.2f} против контроля {b['q1']:5.2f} "
                          f"(Δ {a['q1'] - b['q1']:+.2f})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
