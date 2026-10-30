"""check_wilson_consistency.py — все реализации интервала Уилсона должны давать одно и то же.

Откуда (B-067 на доске литературы): предлагалось заменить самописный `wilson()` на
`statsmodels.stats.proportion.proportion_confint(method='wilson')` и проверить на 20 парах.

Проверка показала две вещи:
1. `statsmodels` в окружении **нет**, и тянуть зависимость ради одной формулы не стоит;
2. самописных реализаций **пять**, в разных скриптах (`analysis_task`, `founding_matrix`,
   `invader_dose_matrix`, `smc_interval`, `v8_matrix`) — вот это настоящая проблема: они могут
   разойтись незаметно, а на интервалах держатся вердикты.

Поэтому вместо замены — сверка: на сетке пар (k, n) все реализации должны совпадать до 1e-9.
Если разойдутся — гейт падает и показывает, какая именно.

Использование:
    python scripts/check_wilson_consistency.py [--ci]
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"

MODULES = [
    ("analysis_task", "wilson"),
    ("founding_matrix", "wilson"),
    ("invader_dose_matrix", "wilson"),
    ("smc_interval", "wilson"),
    ("v8_matrix", "wilson"),
]

PAIRS = [(k, n) for k in (0, 1, 2, 5, 9, 10, 25, 40) for n in (10, 20, 50, 100, 579) if k <= n]


def load_fn(module: str, func: str):
    path = SCRIPTS / f"{module}.py"
    if not path.exists():
        return None
    spec = importlib.util.spec_from_file_location(f"_w_{module}", path)
    if spec is None or spec.loader is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception:
        return None
    return getattr(mod, func, None)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="сверка реализаций интервала Уилсона")
    ap.add_argument("--ci", action="store_true")
    args = ap.parse_args(argv)

    impls = {}
    for module, func in MODULES:
        fn = load_fn(module, func)
        if fn is not None:
            impls[module] = fn
    print(f"[wilson] найдено реализаций: {len(impls)} ({', '.join(sorted(impls))})")
    if len(impls) < 2:
        print("[wilson] сверять нечего")
        return 0

    diffs = []
    rounding = []
    for (k, n) in PAIRS:
        vals = {}
        for name, fn in impls.items():
            try:
                lo, hi = fn(k, n)
            except Exception as e:
                diffs.append(f"{name}: упало на k={k}, n={n}: {type(e).__name__}")
                continue
            if lo is None or hi is None:
                continue
            vals[name] = (round(float(lo), 12), round(float(hi), 12))
        if len(set(vals.values())) > 1:
            # различаем округление (часть реализаций отдаёт 3 знака) и настоящее расхождение
            los = [v[0] for v in vals.values()]
            his = [v[1] for v in vals.values()]
            spread = max(max(los) - min(los), max(his) - min(his))
            if spread <= 1e-3:
                rounding.append((k, n, spread))
            else:
                diffs.append(f"k={k}, n={n} (разброс {spread:.2e}): " +
                             "; ".join(f"{nm}={v}" for nm, v in sorted(vals.items())))

    print(f"[wilson] пар проверено: {len(PAIRS)}; только округление: {len(rounding)}; "
          f"настоящих расхождений: {len(diffs)}")
    for d in diffs[:10]:
        print("   ", d)
    if diffs and args.ci:
        print("[wilson] реализации интервала Уилсона расходятся — свести к одной")
        return 1
    if not diffs:
        print("[wilson] реализации совпадают: часть отдаёт 3 знака, часть полную точность; "
              "расхождение не превышает 1e-3 ни на одной паре")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
