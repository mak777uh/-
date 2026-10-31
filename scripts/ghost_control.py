"""ghost_control.py — X50: блокирует ли «призрак» предиктивную зависимость.

Зачем. Статья 028 утверждает: организм предсказывает **свой след** (ресурс, который сам выедает), а не мир:
`+0.0386` для ресурса под живыми и `0.0000` для ресурса в пустых клетках. Внешние разборы (31.10) возразили
точно: **наблюдательная взаимная информация не различает причинные пути** — и зависимость «состояние сейчас →
ресурс потом» может быть следствием собственного потребления. Нужна интервенция.

**Интервенция «призрак»** (`--ghost`, флаг `ghost_no_consumption`): организм получает доход, но **ресурс не
убывает** — его действие на среду заблокировано. Тогда:

* если предиктивная зависимость **исчезает** — она была следствием собственного следа; утверждение «самомодель»
  подтверждается интервенцией;
* если **сохраняется** — в зависимости есть внешняя компонента, и §4b надо переписать.

Та же мера, что в `scripts/adequacy_mi.py`: `I(Δэнергия_t ; Δресурс_{t+1})` минус перемешивание, по первым
разностям. (Мера консервативна и сама по себе спорна — см. §10dq-доп; здесь она используется **только для
сравнения двух плеч**, а не как абсолютное доказательство.)

Запуск:
    python scripts/ghost_control.py --write
    python scripts/ghost_control.py
"""
from __future__ import annotations

import argparse
import glob
import importlib.util
import json
import random
import statistics as st
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "ghost_control.json"
BINS = 8
SHUFFLES = 20


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def diffs(x: list[float]) -> list[float]:
    return [b - a for a, b in zip(x, x[1:])]


def analyse_run(run: dict, mi) -> dict:
    alive = run.get("alive_series") or []
    S = [s["energy"] for s in run.get("S") or []]
    idx = [i for i, v in enumerate(alive) if v > 0]
    out = {"seed": run.get("seed"), "alive_last": alive[-1] if alive else 0,
           "alive_max": max(alive) if alive else 0}
    if len(idx) < 40:
        out["skipped"] = "мало шагов с живыми"
        return out
    s_d = diffs([S[i] for i in idx])
    for label, key in (("under", "resource_under_alive"), ("empty", "resource_empty")):
        E = [(e.get(key) if e.get(key) is not None else 0.0) for e in run.get("E") or []]
        e_d = diffs([E[i] for i in idx])
        n = min(len(s_d), len(e_d)) - 1
        if n < 30:
            out[f"excess_{label}"] = None
            continue
        x, y = s_d[:n], e_d[1:n + 1]
        obs = mi(x, y, BINS)
        rng = random.Random((run.get("seed") or 0) * 31 + 5)
        sh = []
        for _ in range(SHUFFLES):
            y2 = y[:]
            rng.shuffle(y2)
            sh.append(mi(x, y2, BINS))
        out[f"excess_{label}"] = round(obs - st.median(sh), 4)
    return out


def build() -> dict:
    mi = _load("_indiv", ROOT / "scripts" / "individuality.py").mutual_information
    arms: dict[str, list[dict]] = {}
    for f in sorted(glob.glob(str(ROOT.parent / "_hourly" / "x50_*_s*.json"))):
        name = Path(f).name
        arm = "ghost" if "_ghost_" in name else "normal"
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        for run in d.get("runs") or []:
            arms.setdefault(arm, []).append(analyse_run(run, mi))
    summary = {}
    for arm, rows in arms.items():
        for label in ("under", "empty"):
            vals = [r[f"excess_{label}"] for r in rows if r.get(f"excess_{label}") is not None]
            if vals:
                summary.setdefault(arm, {})[label] = {
                    "n": len(vals), "median": round(st.median(vals), 4),
                    "positive": sum(1 for v in vals if v > 0),
                }
    verdict = None
    try:
        n_under = summary["normal"]["under"]["median"]
        g_under = summary.get("ghost", {}).get("under", {}).get("median")
        if g_under is not None:
            verdict = ("зависимость исчезла под «призраком»: она была следствием собственного действия"
                       if abs(g_under) < abs(n_under) / 2 else
                       "зависимость сохранилась: в ней есть внешняя компонента")
    except KeyError:
        pass
    return {
        "kind": "ghost_control", "experiment": "X50",
        "command": "python scripts/ghost_control.py --write",
        "metric": {"excess_under": "I(Δэнергия; Δресурс под живыми на t+1) минус перемешивание, бит",
                   "excess_empty": "то же для ресурса в пустых клетках"},
        "design": {"arms": ["normal", "ghost"], "steps": 700, "income": 0.02, "bins": BINS},
        "by_arm": summary,
        "verdict": verdict,
        "not_claimed": ["мера по первым разностям консервативна и спорна (§10dq-доп); здесь она только для сравнения плеч",
                        "10 сидов на плечо", "«призрак» блокирует потребление, но не дыхание/ремонт"],
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="контроль «призрак» для утверждения о самомодели")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    data = build()
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[ghost] записано: {OUT.name}")
    for arm, v in data["by_arm"].items():
        u = v.get("under", {})
        e = v.get("empty", {})
        print(f"  {arm}: под собой {u.get('median')} ({u.get('positive')}/{u.get('n')} > 0) | "
              f"в пустых {e.get('median')} ({e.get('positive')}/{e.get('n')} > 0)")
    if data.get("verdict"):
        print("  вердикт:", data["verdict"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
