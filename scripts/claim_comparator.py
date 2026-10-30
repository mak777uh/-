"""claim_comparator.py — независимый аудит утверждения против его Setup (перенос идеи LongTails).

Откуда (30.10). LongTails ([github.com/k3nfalt/longtails](https://github.com/k3nfalt/longtails)) устроен так:
**Setup** (допущения + критерий успеха) отдельно от результата, **budget** (цена) явно, и **Comparator**,
который отказывает теореме, если она выходит за Setup. У нас допущения жили в прозе, и за сутки семь выводов
пришлось отменить — почти все потому, что утверждение жило вне области, где было проверено.

Здесь то же самое в нашей форме, без Lean:

  `lab/claims/<id>.json`:
    statement   — текст утверждения;
    status      — confirmed | retracted;
    setup.params     — допустимые значения (сетка, амплитуда, горизонт);
    setup.admissible — условия, при которых утверждение ОПРЕДЕЛЕНО (метрика, минимум сидов, контроли);
    setup.successful — правило решения (интервал не включает ноль, минимальный эффект);
    budget      — сколько сидов/прогонов/часов оплачено;
    evidence    — артефакты (агрегат + плечи);
    check       — что именно пересчитать (kind: field_integral_contrast).

Компаратор:
  1. пересчитывает метрику из артефактов, а не берёт из текста;
  2. отказывает, если хоть один прогон вне `params` (сетка/горизонт/амплитуда);
  3. отказывает, если бюджет не оплачен (сидов < admissible.min_seeds_per_arm);
  4. для `confirmed` требует, чтобы правило выполнялось;
  5. для `retracted` требует, чтобы правило НЕ выполнялось — иначе отмена была необоснованной.

Использование:
    python scripts/claim_comparator.py            # отчёт
    python scripts/claim_comparator.py --ci       # падение при любом нарушении
"""
from __future__ import annotations

import argparse
import glob
import json
import random
import statistics as st
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLAIMS = ROOT / "lab" / "claims"


def field_rows(aggregate: Path) -> list[dict]:
    d = json.loads(aggregate.read_text(encoding="utf-8"))
    return d.get("rows") or []


def arm_values(rows: list[dict], arm_files: dict[str, list[str]], metric: str) -> dict[str, list[float]]:
    """Значения метрики по плечам: принадлежность определяется шаблонами имён файлов."""
    out: dict[str, list[float]] = {}
    for arm, patterns in arm_files.items():
        vals = []
        for pat in patterns:
            prefix = pat.split("*")[0]
            for r in rows:
                if r["file"].startswith(prefix):
                    v = r.get(metric)
                    if isinstance(v, (int, float)):
                        vals.append(float(v))
        out[arm] = vals
    return out


def filter_by_params(rows: list[dict], params: dict) -> tuple[list[dict], list[str]]:
    """Отбросить прогоны вне допустимых параметров; вернуть (годные, нарушения)."""
    grids = params.get("grid")
    horizons = params.get("horizon")
    bad = []
    good = []
    for r in rows:
        g = r.get("grid")
        h = r.get("steps")
        if grids and g is not None and g not in grids:
            bad.append(f"{r['file']}: сетка {g} вне {grids}")
            continue
        if horizons and h is not None and h not in horizons:
            bad.append(f"{r['file']}: горизонт {h} вне {horizons}")
            continue
        good.append(r)
    return good, bad


def boot_ci(a: list[float], b: list[float], reps: int = 5000, seed: int = 21) -> tuple[float, float, float]:
    rng = random.Random(seed)
    d = []
    for _ in range(reps):
        sa = [rng.choice(a) for _ in a]
        sb = [rng.choice(b) for _ in b]
        d.append(st.median(sa) - st.median(sb))
    d.sort()
    return st.median(a) - st.median(b), d[int(0.025 * len(d))], d[int(0.975 * len(d))]


def check_claim(path: Path) -> tuple[bool, list[str], list[str]]:
    c = json.loads(path.read_text(encoding="utf-8"))
    notes: list[str] = []
    problems: list[str] = []

    kind = (c.get("check") or {}).get("kind")
    agg_rel = (c.get("evidence") or {}).get("aggregate")
    if kind != "field_integral_contrast" or not agg_rel:
        return True, [f"проверка вида «{kind}» не реализована — пропущено"], problems

    agg = ROOT / agg_rel
    status0 = str(c.get("status"))
    if not agg.exists():
        if status0 == "planned":
            return True, [f"ожидает доказательств: нет агрегата {agg_rel}"], problems
        return False, notes, [f"нет агрегата {agg_rel}"]
    rows = field_rows(agg)
    params = (c.get("setup") or {}).get("params") or {}
    adm = (c.get("setup") or {}).get("admissible") or {}
    suc = (c.get("setup") or {}).get("successful") or {}
    budget = c.get("budget") or {}
    metric = adm.get("metric", "components_integral")

    arms = (c.get("evidence") or {}).get("arms") or {}
    # Сначала отбираем строки, относящиеся к ЭТОМУ утверждению (по шаблонам плеч), и только потом
    # проверяем params: иначе чужие плечи агрегата (другая сетка/горизонт) ложно нарушают допущения.
    own_prefixes = [pat.split("*")[0] for pats in arms.values() for pat in pats]
    own_rows = [r for r in rows if any(r["file"].startswith(pf) for pf in own_prefixes)]
    rows, violations = filter_by_params(own_rows, params)
    if violations:
        problems.append(f"прогоны вне допустимых параметров: {len(violations)} (напр. {violations[0]})")
    else:
        notes.append(f"все {len(rows)} прогонов утверждения внутри params "
                     f"(сетка {params.get('grid')}, горизонт {params.get('horizon')})")

    vals = arm_values(rows, arms, metric)
    for arm, v in vals.items():
        notes.append(f"плечо {arm}: n={len(v)}, медиана={round(st.median(v), 3) if v else None}")

    min_seeds = int(adm.get("min_seeds_per_arm", 1))
    short = [arm for arm, v in vals.items() if len(v) < min_seeds]
    if short:
        msg = (f"бюджет не оплачен: в плечах {short} меньше {min_seeds} прогонов "
               f"(объявлено budget.seeds={budget.get('seeds')})")
        if status0 == "planned":
            notes.append("ожидает: " + msg)
            return True, notes, problems
        problems.append(msg)

    contrast = (c.get("check") or {}).get("contrast") or ["static", "homog"]
    a = vals.get(contrast[0]) or []
    b = vals.get(contrast[1]) or []
    if not a or not b:
        problems.append(f"не хватает плеч {contrast} для контраста")
        return False, notes, problems

    diff, lo, hi = boot_ci(a, b)
    excludes_zero = not (lo <= 0 <= hi)
    min_effect = float(suc.get("min_effect", 0.0))
    rule = str(suc.get("rule", "bootstrap_ci_excludes_zero"))
    if rule == "bootstrap_ci_includes_zero":
        # утверждение ОБ ОТСУТСТВИИ различия: правило выполнено, если интервал накрывает ноль
        rule_ok = not excludes_zero
    else:
        rule_ok = excludes_zero and abs(diff) >= min_effect
    notes.append(f"контраст: медианы {round(st.median(a), 3)} против {round(st.median(b), 3)}, "
                 f"разница {round(diff, 3)}, CI [{round(lo, 3)}; {round(hi, 3)}]")

    status = status0
    if status == "planned":
        notes.append("утверждение запланировано — правило пока не проверяется как вердикт")
        return True, notes, problems
    if status == "confirmed" and not rule_ok:
        problems.append(f"утверждение confirmed, но правило не выполнено (правило: {rule})")
    if status == "retracted":
        if rule_ok:
            problems.append("утверждение помечено retracted, но правило ВЫПОЛНЯЕТСЯ — отмена необоснованна")
        else:
            failed = c.get("failed_condition") or "правило не выполнено"
            notes.append(f"отмена подтверждена: правило «{rule}» не выполнено ({failed})")
    return (not problems), notes, problems


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="аудит утверждений против их Setup")
    ap.add_argument("--ci", action="store_true")
    args = ap.parse_args(argv)

    files = sorted(glob.glob(str(CLAIMS / "*.json")))
    if not files:
        print("[claims] файлов утверждений нет")
        return 0

    total_bad = 0
    for f in files:
        cid = Path(f).stem
        ok, notes, problems = check_claim(Path(f))
        mark = "OK  " if ok else "ОТКАЗ"
        print(f"[claims] {mark} {cid}")
        for n in notes:
            print(f"        · {n}")
        for p in problems:
            print(f"        ✗ {p}")
        if not ok:
            total_bad += 1

    print(f"[claims] утверждений: {len(files)}, отказов: {total_bad}")
    if total_bad and args.ci:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
