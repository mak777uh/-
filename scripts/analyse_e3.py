"""analyse_e3.py — сходятся ли три пути после того, как история закончилась.

E3: три плеча до шага 300 идут с разным темпом (const / slow / fast), затем все — одинаково (p = 0.585).
Если макроскопические наблюдаемые после 300 сходятся — система марковская на этом уровне; если нет —
история влияет, и «когда пришёл сигнал» имеет смысл.

Сравнение идёт с шумом между сидами: различие между плечами считается значимым, только если оно больше
разброса внутри плеча.
"""
import glob
import json
import statistics as st
from pathlib import Path

ROOT = Path(r"C:\Users\Admin\Documents\Qoder\2026-10-18\82ab86cd\repo")
SRC = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "w2bud_e3"
STEPS = (300, 400, 500, 600, 700, 800, 900)


def load():
    arms = {}
    for f in sorted(SRC.glob("w2bud_e3_*.json")):
        name = f.stem.replace("w2bud_e3_", "")
        arm = name.rsplit("_seed", 1)[0]
        summary = json.loads(f.read_text(encoding="utf-8"))["summary"]
        series = summary.get("type_counts_series") or []
        points = {}
        for st in STEPS:
            if not series:
                break
            r = min(series, key=lambda x: abs(x["step"] - st))
            counts = {str(k).lstrip("T"): int(v) for k, v in r["counts"].items()}
            total = sum(counts.values()) or 1
            probs = [v / total for v in counts.values() if v > 0]
            points[st] = {
                "alive": total,
                "q1": round(1.0 / sum(p * p for p in probs), 3) if probs else 0.0,
                "tags": len(counts),
            }
        arms.setdefault(arm, []).append(points)
    return arms


def main():
    arms = load()
    if not arms:
        print("нет артефактов")
        return 1
    print("плечи:", {k: len(v) for k, v in arms.items()})
    for st in STEPS:
        line = [f"шаг {st:3d}:"]
        for arm in ("const", "slow", "fast"):
            vals = [p[st]["q1"] for p in arms.get(arm, []) if st in p]
            alive = [p[st]["alive"] for p in arms.get(arm, []) if st in p]
            if vals:
                line.append(f"{arm} q1 {st_mean(vals):.2f}±{st_dev(vals):.2f} живых {st_mean(alive):.0f}")
        print("  " + " | ".join(line))
    # сходимость: насколько slow/fast отличаются от const после 300, в единицах разброса const
    print("\nсходимость после переключения (в единицах разброса const):")
    for st in STEPS[1:]:
        base = [p[st]["q1"] for p in arms.get("const", []) if st in p]
        if len(base) < 2:
            continue
        sd = st_dev(base) or 1e-9
        for arm in ("slow", "fast"):
            v = [p[st]["q1"] for p in arms.get(arm, []) if st in p]
            if not v:
                continue
            print(f"  шаг {st:3d} {arm:5s}: |Δq1| = {abs(st_mean(v) - st_mean(base)):6.2f}  ({abs(st_mean(v) - st_mean(base))/sd:5.1f} sd)")
    return 0


def st_mean(xs):
    return st.mean(xs) if xs else 0.0


def st_dev(xs):
    return st.pstdev(xs) if len(xs) > 1 else 0.0


if __name__ == "__main__":
    raise SystemExit(main())
