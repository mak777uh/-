"""aggregate_check.py — сверка агрегатов с артефактами и внутренняя согласованность.

Зачем: за сутки было две ошибки агрегатов (утечка типа между строками; мнимая
инверсия направлений). Правило: каждая строка агрегата воспроизводится из файла
в `artifact`, а поля-доли согласованы со своим типом.

Проверки:
1. **Внутренние (всегда, без артефактов):** если в строке есть `direction` и
   `invader_share_final`, то `invader_share_final` обязан равняться
   `a_share_final` для инвайдера A и `1 − a_share_final` для инвайдера B; стартовая
   доля A (`a_share_start`) обязана быть ~1.0 у резидента A и ~0.0 у резидента B.
2. **Сверка с артефактом (когда файл доступен):** `pop_time`, `alive_final`,
   `born`, `died`, `invader_share_after`, `a_share_final` совпадают с `summary`
   первичного прогона.

Артефакты прогонов лежат вне git (`_hourly/polish`), поэтому в CI проверка 2
пропускается с предупреждением, а проверка 1 работает всегда.

Запуск:
    python scripts/aggregate_check.py                 # все агрегаты
    python scripts/aggregate_check.py FILE ...        # конкретные
    python scripts/aggregate_check.py --strict        # отсутствие артефакта = ошибка
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGG_DIR = ROOT / "morphogenesis" / "experiments" / "E09_pond"


def _invader_type(direction: str) -> int:
    # "invade-A-into-B-resident" -> инвайдер A (0); "...-B-into-A..." -> тип 1
    return 0 if direction.split("-")[1] == "A" else 1


def _resident_is_a(direction: str) -> bool:
    return "invade-B-into-A" in direction


def check_row(row: dict, strict: bool) -> tuple[list[str], list[str]]:
    """Возвращает (ошибки, предупреждения) для одной строки."""
    errors: list[str] = []
    warns: list[str] = []

    direction = row.get("direction")
    if direction and "invader_share_final" in row and "a_share_final" in row:
        itype = _invader_type(direction)
        a_final = row["a_share_final"]
        if a_final is not None:
            want = a_final if itype == 0 else round(1.0 - a_final, 6)
            got = row["invader_share_final"]
            if got is None or abs(float(got) - want) > 1e-3:
                errors.append(
                    f"invader_share_final={got} != {want} "
                    f"(a_share_final={a_final}, инвайдер {'A' if itype == 0 else 'B'})"
                )
    if direction and row.get("a_share_start") is not None:
        start = float(row["a_share_start"])
        resident_a = _resident_is_a(direction)
        ok = start > 0.75 if resident_a else start < 0.25
        if not ok:
            errors.append(
                f"a_share_start={start:.2f} не соответствует резиденту "
                f"{'A' if resident_a else 'B'} (ожидалось ~1.0/~0.0)"
            )

    rel = row.get("artifact")
    if not rel:
        if strict:
            errors.append("нет поля artifact")
        return errors, warns
    art = ROOT / rel
    if not art.is_file():
        art = ROOT.parent / rel
    if not art.is_file():
        (errors if strict else warns).append(f"артефакт не найден: {rel}")
        return errors, warns

    summary = json.loads(art.read_text(encoding="utf-8"))["summary"]
    pairs = {
        "pop_time": summary.get("pop_time"),
        "alive_final": (summary.get("final") or {}).get("alive_cells"),
        "born": (summary.get("final") or {}).get("born"),
        "died": (summary.get("final") or {}).get("died"),
        "invader_share_after": summary.get("invader_share_after"),
        "a_share_final": summary.get("a_share_final"),
    }
    for field, want in pairs.items():
        if field not in row or want is None or row[field] is None:
            continue
        try:
            got_v, want_v = float(row[field]), float(want)
        except (TypeError, ValueError):
            continue
        if abs(got_v - want_v) > 1e-3:
            errors.append(f"{field}={row[field]} != артефакт {want}")
    return errors, warns


def check_medians(rows: list[dict]) -> list[str]:
    """Внутренние проверки для агрегатов-медиан (одна строка = несколько прогонов)."""
    errors: list[str] = []
    for i, row in enumerate(rows):
        n = row.get("n")
        median = row.get("median")
        if not isinstance(n, int) or n <= 0:
            errors.append(f"[{i}]: n должно быть положительным ({n})")
            continue
        if median is None:
            errors.append(f"[{i}]: нет median")
            continue
        lo, hi = row.get("min"), row.get("max")
        if isinstance(lo, (int, float)) and isinstance(hi, (int, float)) and not (lo <= median <= hi):
            errors.append(f"[{i}]: median {median} вне [{lo}, {hi}]")
        collapses = row.get("collapses")
        if isinstance(collapses, int) and collapses > n:
            errors.append(f"[{i}]: collapses {collapses} > n {n}")
    return errors


def check_invasion(rows: list[dict]) -> list[str]:
    """Проверки агрегата инвазии: рост согласован с долями, невалидные помечены."""
    errors: list[str] = []
    for i, row in enumerate(rows):
        start = row.get("invader_share_start")
        end = row.get("invader_share_end")
        growth = row.get("growth")
        if start is None or end is None:
            errors.append(f"[{i}]: нет invader_share_start/end")
            continue
        if start < 0 or start > 1 or end < 0 or end > 1:
            errors.append(f"[{i}]: доля вне [0,1] (start {start}, end {end})")
        if start > 0 and growth is not None:
            expected = end / start
            if abs(growth - expected) > 1e-6:
                errors.append(f"[{i}]: growth {growth} != end/start {expected:.4f}")
        if start > 0.05 and not row.get("invalid_reason"):
            errors.append(f"[{i}]: доля подсадки {start:.3f} > 0.05 без invalid_reason "
                          "(похоже на переворот компонента)")
    return errors


def check_probe(rows: list[dict]) -> list[str]:
    """Проверки сводки зонда: положительный полураспад и невозрастающий decay."""
    errors: list[str] = []
    for i, row in enumerate(rows):
        half = row.get("half_life_steps")
        if not isinstance(half, (int, float)) or half <= 0:
            errors.append(f"[{i}]: half_life_steps должно быть положительным ({half})")
        decay = row.get("decay") or []
        if len(decay) < 3:
            errors.append(f"[{i}]: decay короче 3 точек")
            continue
        for a, b in zip(decay, decay[1:]):
            if isinstance(a, (int, float)) and isinstance(b, (int, float)) and b > a + 1e-6:
                errors.append(f"[{i}]: decay растёт ({a} → {b}) — метрика сломана")
                break
    return errors


def check_file(path: Path, strict: bool = False) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warns: list[str] = []
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("rows")
    if not rows:
        return errors, warns  # не агрегат
    if payload.get("kind") == "invasion_runs":
        return [f"{path.name}{e}" for e in check_invasion(rows)], warns
    if payload.get("kind") == "probe_summary":
        return [f"{path.name}{e}" for e in check_probe(rows)], warns
    if payload.get("kind") == "aggregate_medians":
        return [f"{path.name}{e}" for e in check_medians(rows)], warns
    for i, row in enumerate(rows):
        errs, ws = check_row(row, strict)
        errors += [f"{path.name}[{i}]: {e}" for e in errs]
        warns += [f"{path.name}[{i}]: {w}" for w in ws]
    return errors, warns


def main(argv: list[str]) -> int:
    strict = "--strict" in argv
    files = [Path(a) for a in argv if not a.startswith("--")] or sorted(AGG_DIR.glob("*.json"))
    total_err = total_warn = 0
    for f in files:
        errs, warns = check_file(f, strict=strict)
        if errs:
            total_err += len(errs)
            print(f"✗ {f.name}: {len(errs)} расхождений")
            for e in errs[:8]:
                print(f"    {e}")
        elif warns:
            total_warn += len(warns)
            print(f"~ {f.name}: ок по внутренним проверкам, {len(warns)} без артефактов")
        else:
            print(f"✓ {f.name}")
    print(f"\nошибок: {total_err}, без артефактов: {total_warn}")
    return 1 if total_err else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
