"""adequacy_mi.py — адекватность: числа статьи 028 §4b из артефактов, с названной командой.

Почему отдельный скрипт. Библиотекарь (аудит 31.10) заметил и был прав: числа «+0.0386 против 0.0000» стояли в
статье, а в `adequacy_matrix.json` лежали только `alive_last`/`energy_last` — **ни меры, ни команды**. Мера
считалась вручную и не сохранялась. Здесь она считается из сырых рядов `S`/`E`, которые есть в артефактах.

Мера (фиксирована в пре-регистрации `reports/2026-10-31-adequacy-plan.md`):

    адекватность = I(Δэнергия_t ; Δресурс_{t+1}) − I(Δэнергия_t ; перемешанный Δресурс_{t+1})

по первым разностям (иначе мера ловит общий тренд), только по шагам, где есть живые; перемешивание — 20
перестановок, берётся медиана. Считается **две цели**:

  * `resource_under_alive` — ресурс под живыми клетками (то, что организм сам выедает);
  * `resource_empty` — ресурс в пустых клетках (то, чего он не касается).

Запуск:
    python scripts/adequacy_mi.py --write     # пересобрать агрегат
    python scripts/adequacy_mi.py             # только напечатать
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
SRC = ROOT / "morphogenesis" / "experiments" / "E09_pond" / "adequacy"
OUT = SRC / "adequacy_mi.json"
BINS = 8
SHUFFLES = 20


def _mi_func():
    spec = importlib.util.spec_from_file_location("_indiv", ROOT / "scripts" / "individuality.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.mutual_information


def diffs(x: list[float]) -> list[float]:
    return [b - a for a, b in zip(x, x[1:])]


def per_run(run: dict, mi) -> dict:
    alive = run.get("alive_series") or []
    S = [s["energy"] for s in run.get("S") or []]
    idx = [i for i, v in enumerate(alive) if v > 0]
    out: dict = {"seed": run.get("seed"), "alive_last": alive[-1] if alive else 0,
                 "alive_max": max(alive) if alive else 0}
    if len(idx) < 40:
        out["skipped"] = "мало шагов с живыми"
        return out
    s_d = diffs([S[i] for i in idx])
    for label, key in (("under", "resource_under_alive"), ("empty", "resource_empty")):
        E = [((e.get(key) if e.get(key) is not None else 0.0)) for e in run.get("E") or []]
        e_d = diffs([E[i] for i in idx])
        n = min(len(s_d), len(e_d)) - 1
        if n < 30:
            out[f"mi_{label}"] = None
            continue
        x, y = s_d[:n], e_d[1:n + 1]
        obs = mi(x, y, BINS)
        rng = random.Random((run.get("seed") or 0) * 31 + 5)
        sh = []
        for _ in range(SHUFFLES):
            y2 = y[:]
            rng.shuffle(y2)
            sh.append(mi(x, y2, BINS))
        out[f"mi_{label}"] = round(obs, 4)
        out[f"noise_{label}"] = round(st.median(sh), 4)
        out[f"excess_{label}"] = round(obs - st.median(sh), 4)
    return out


def build() -> dict:
    mi = _mi_func()
    by_arm: dict[str, list[dict]] = {}
    for f in sorted(glob.glob(str(SRC / "x44_*_s*.json"))):
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        for run in d.get("runs") or []:
            by_arm.setdefault(run.get("arm"), []).append(per_run(run, mi))
    summary = {}
    for arm, rows in by_arm.items():
        for label in ("under", "empty"):
            vals = [r.get(f"excess_{label}") for r in rows if r.get(f"excess_{label}") is not None]
            if vals:
                summary.setdefault(arm, {})[label] = {
                    "n": len(vals), "median_excess": round(st.median(vals), 4),
                    "positive": sum(1 for v in vals if v > 0),
                }
    return {
        "kind": "adequacy_mi",
        "experiment": "X44",
        "command": "python scripts/adequacy_mi.py --write",
        "metric": {
            "excess_under": "I(Δэнергия; Δресурс под живыми на t+1) минус перемешанный контроль, бит",
            "excess_empty": "то же для ресурса в пустых клетках (то, чего организм не касается)",
        },
        "design": {"bins": BINS, "shuffles": SHUFFLES, "steps": 700, "income": 0.02,
                   "arms": ["cost", "cheap", "free"]},
        "by_arm": summary,
        "runs": by_arm,
        "not_claimed": ["5 сидов на плечо", "resource_empty — среднее по пустым клеткам, а не конкретная точка"],
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="адекватность: мера и контроль")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    data = build()
    if args.write:
        OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[adequacy] записано: {OUT.name}")
    for arm, v in data["by_arm"].items():
        u = v.get("under", {})
        e = v.get("empty", {})
        print(f"  {arm}: под собой {u.get('median_excess')} ({u.get('positive')}/{u.get('n')} > 0) | "
              f"в пустых {e.get('median_excess')} ({e.get('positive')}/{e.get('n')} > 0)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
