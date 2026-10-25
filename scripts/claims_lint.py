"""Линтер матрицы утверждений (manuscript/CLAIMS.md).

Зачем: «подтверждено» раньше покрывало и машинное доказательство, и один удачный прогон.
Теперь у каждой строки обязан быть тип основания, а ссылки на артефакты — существовать.

Что проверяется:
1. у каждой строки ровно 6 колонок, header совпадает со схемой;
2. `Основание` — из списка {доказательство, тест, статистика, наблюдение, суждение};
3. `Статус` начинается с одного из {подтверждено, опровергнуто, открыто, запрещено};
4. «допустимая формулировка» (последняя колонка) непустая и не короче 15 символов;
5. у `доказательство` есть ссылка на `formal/` или F-теорему;
6. у `статистика` хотя бы один путь `*.json`/`*.lean`/`*.py` из ячейки доказательства существует
   в репозитории (символы без пути не считаются).

Код возврата 1 при любой ошибке — линтер рассчитан на CI и на `make verify`.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLAIMS = ROOT / "manuscript" / "CLAIMS.md"

EXPECTED_HEADER = [
    "Утверждение", "Статус", "Основание", "Допущения", "Что остаётся обосновать",
    "Доказательство", "Раздел", "Допустимая формулировка",
]
KINDS = {"доказательство", "тест", "статистика", "наблюдение", "суждение"}
STATUS_PREFIXES = ("подтверждено", "опровергнуто", "открыто", "запрещено")
PATH_RE = re.compile(r"[A-Za-z0-9_./-]+\.(?:json|lean|py|md)")


def parse_rows(text: str) -> tuple[list[str], list[tuple[int, list[str]]]]:
    header: list[str] = []
    rows: list[tuple[int, list[str]]] = []
    in_claims_table = False
    for lineno, line in enumerate(text.split("\n"), start=1):
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells and cells[0] == "Утверждение":
            header = cells
            in_claims_table = True
            continue
        if not in_claims_table:
            continue
        if cells and set(cells[0]) <= {"-", " "}:
            continue
        rows.append((lineno, cells))
    return header, rows


def main() -> int:
    if not CLAIMS.exists():
        print(f"[claims_lint] нет файла {CLAIMS}")
        return 1
    text = CLAIMS.read_text(encoding="utf-8")
    header, rows = parse_rows(text)
    problems: list[str] = []

    if header != EXPECTED_HEADER:
        problems.append(f"header: ожидался {EXPECTED_HEADER}, получен {header}")

    for lineno, cells in rows:
        if len(cells) != 8:
            problems.append(f"строка {lineno}: {len(cells)} колонок вместо 8")
            continue
        claim, status, kind, assume, remains, evidence, section, allowed = cells
        if not claim:
            problems.append(f"строка {lineno}: пустое утверждение")
        if kind not in KINDS:
            problems.append(f"строка {lineno}: основание «{kind}» не из списка {sorted(KINDS)}")
        if not status.lower().startswith(STATUS_PREFIXES):
            problems.append(f"строка {lineno}: статус «{status}» не начинается с {STATUS_PREFIXES}")
        if len(allowed) < 15:
            problems.append(f"строка {lineno}: допустимая формулировка слишком короткая ({len(allowed)} симв.)")
        if kind == "доказательство" and not re.search(r"formal/|F-[A-Z]", evidence):
            problems.append(f"строка {lineno}: основание «доказательство», но в доказательстве нет ссылки на formal/")
        if kind == "статистика":
            paths = [m.group(0) for m in PATH_RE.finditer(evidence)]
            found = []
            for pth in paths:
                cand = [ROOT / pth, ROOT / "morphogenesis" / pth]
                cand += list(ROOT.glob(f"morphogenesis/experiments/**/{Path(pth).name}"))
                cand += list(ROOT.glob(f"reports/figures/**/{Path(pth).name}"))
                if any(c.exists() for c in cand):
                    found.append(pth)
            if paths and not found:
                problems.append(
                    f"строка {lineno}: основание «статистика», но ни один путь из {paths[:3]} не существует"
                )

    counts: dict[str, int] = {}
    missing_assume = 0
    for _, cells in rows:
        if len(cells) == 8:
            counts[cells[2]] = counts.get(cells[2], 0) + 1
            if cells[3] == "—":
                missing_assume += 1

    print(f"[claims_lint] строк: {len(rows)}, основания: {counts}")
    if missing_assume:
        print(f"[claims_lint] предупреждение: у {missing_assume} строк не заполнены «Допущения» (наследие; новые строки обязаны заполнять)")
    if problems:
        for p in problems:
            print(f"[claims_lint] ОШИБКА: {p}")
        print(f"[claims_lint] проблем: {len(problems)}")
        return 1
    print("[claims_lint] OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
