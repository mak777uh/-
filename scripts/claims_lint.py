"""Линтер матрицы утверждений (manuscript/CLAIMS.md).

Зачем: «подтверждено» раньше покрывало и машинное доказательство, и один удачный прогон.
Теперь у каждой строки обязан быть тип основания, а ссылки на артефакты — существовать.

Строгие правила (ошибка — код возврата 1):
1. у каждой строки ровно 8 колонок, header совпадает со схемой;
2. `Основание` — из списка {доказательство, тест, статистика, наблюдение, суждение};
3. `Статус` начинается с одного из {подтверждено, опровергнуто, открыто, запрещено};
4. «допустимая формулировка» (последняя колонка) непустая и не короче 15 символов;
5. у `доказательство` есть ссылка на `formal/` или F-теорему;
6. у `статистика` есть хотя бы один **существующий** файл-артефакт;
7. у `тест` есть хотя бы один существующий тест (`tests/test_*.py` или путь с `test_`);
8. «новая» строка (дата 2026-10-25+ в утверждении или доказательстве) обязана заполнить
   «Допущения».

Предупреждения (не ошибка, чтобы не ломать наследие):
- у `статистика`/`тест` нет путей вовсе, и строка наследуемая;
- у `наблюдение` в допустимой формулировке стоит «доказано/установлено/показано»;
- у `опровергнуто` нет строки в `docs/eliminations.md` (сверка по имени артефакта).

Почему «ошибка/предупреждение»: наследуемые строки писались до введения правила, переписывать их
задним числом нельзя (§6b), а новые строки должны быть чистыми с первого раза.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLAIMS = ROOT / "manuscript" / "CLAIMS.md"
ELIMINATIONS = ROOT / "docs" / "eliminations.md"

EXPECTED_HEADER = [
    "Утверждение", "Статус", "Основание", "Допущения", "Что остаётся обосновать",
    "Доказательство", "Раздел", "Допустимая формулировка",
]
KINDS = {"доказательство", "тест", "статистика", "наблюдение", "суждение"}
STATUS_PREFIXES = ("подтверждено", "опровергнуто", "открыто", "запрещено")
PATH_RE = re.compile(r"[A-Za-z0-9_./-]+\.(?:json|lean|py|md)")
STRONG_WORDS = ("доказано", "установлено", "показано", "доказывает")
NEW_ROW_DATE = "2026-10-25"


def parse_rows(text: str) -> tuple[list[str], list[tuple[int, list[str]]]]:
    header: list[str] = []
    rows: list[tuple[int, list[str]]] = []
    in_table = False
    for lineno, line in enumerate(text.split("\n"), start=1):
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells and cells[0] == "Утверждение":
            header = cells
            in_table = True
            continue
        if not in_table:
            continue
        if cells and set(cells[0]) <= {"-", " "}:
            continue
        rows.append((lineno, cells))
    return header, rows


def resolve(path: str) -> list[Path]:
    """Где может лежать артефакт: корень, morphogenesis/, любой подкаталог экспериментов."""
    name = Path(path).name
    cand = [ROOT / path, ROOT / "morphogenesis" / path]
    cand += list(ROOT.glob(f"morphogenesis/experiments/**/{name}"))
    cand += list(ROOT.glob(f"morphogenesis/tests/{name}"))
    cand += list(ROOT.glob(f"reports/**/{name}"))
    cand += list(ROOT.glob(f"formal/**/{name}"))
    return cand


def is_new_row(claim: str, evidence: str) -> bool:
    return NEW_ROW_DATE in claim or NEW_ROW_DATE in evidence


def main() -> int:
    if not CLAIMS.exists():
        print(f"[claims_lint] нет файла {CLAIMS}")
        return 1
    text = CLAIMS.read_text(encoding="utf-8")
    header, rows = parse_rows(text)
    elim_text = ELIMINATIONS.read_text(encoding="utf-8") if ELIMINATIONS.exists() else ""

    errors: list[str] = []
    warnings: list[str] = []

    if header != EXPECTED_HEADER:
        errors.append(f"header: ожидался {EXPECTED_HEADER}, получен {header}")

    counts: dict[str, int] = {}
    for lineno, cells in rows:
        if len(cells) != 8:
            errors.append(f"строка {lineno}: {len(cells)} колонок вместо 8")
            continue
        claim, status, kind, assume, remains, evidence, section, allowed = cells
        new = is_new_row(claim, evidence)
        counts[kind] = counts.get(kind, 0) + 1

        if not claim:
            errors.append(f"строка {lineno}: пустое утверждение")
        if kind not in KINDS:
            errors.append(f"строка {lineno}: основание «{kind}» не из списка {sorted(KINDS)}")
        if not status.lower().startswith(STATUS_PREFIXES):
            errors.append(f"строка {lineno}: статус «{status}» не начинается с {STATUS_PREFIXES}")
        if len(allowed) < 15:
            errors.append(f"строка {lineno}: допустимая формулировка слишком короткая ({len(allowed)} симв.)")

        paths = [m.group(0) for m in PATH_RE.finditer(evidence)]
        existing = [p for p in paths if any(c.exists() for c in resolve(p))]

        if kind == "доказательство" and not re.search(r"formal/|F-[A-Z]", evidence):
            errors.append(f"строка {lineno}: основание «доказательство», но нет ссылки на formal/")
        if kind == "статистика" and not existing:
            msg = f"строка {lineno}: основание «статистика», но ни один артефакт не существует ({paths[:3]})"
            (errors if new else warnings).append(msg)
        if kind == "тест" and not any("test" in p for p in existing):
            msg = f"строка {lineno}: основание «тест», но нет существующего теста"
            (errors if new else warnings).append(msg)
        if kind == "наблюдение" and any(w in allowed.lower() for w in STRONG_WORDS):
            warnings.append(
                f"строка {lineno}: основание «наблюдение», но формулировка звучит как доказательство"
            )
        if new and assume.strip() in ("", "—"):
            errors.append(f"строка {lineno}: новая строка без «Допущений»")
        if new and status.lower().startswith("опровергнуто") and elim_text:
            if not any(Path(p).name in elim_text for p in paths):
                warnings.append(
                    f"строка {lineno}: «опровергнуто», но в docs/eliminations.md нет строки с этим артефактом"
                )

    print(f"[claims_lint] строк: {len(rows)}, основания: {counts}")
    for w in warnings:
        print(f"[claims_lint] предупреждение: {w}")
    if errors:
        for e in errors:
            print(f"[claims_lint] ОШИБКА: {e}")
        print(f"[claims_lint] ошибок: {len(errors)}, предупреждений: {len(warnings)}")
        return 1
    print(f"[claims_lint] OK (предупреждений: {len(warnings)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
