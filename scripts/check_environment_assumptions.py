"""check_environment_assumptions.py — гейты не должны зависеть от календаря и концов строк.

Откуда (29.10). За сутки три «научных» падения оказались падениями окружения:

1. `lean_axioms.py` объявил 31 теорему грязной, потому что у тулчейна не было `Init`/`olean`. Провал
   инструмента выглядел как провал математики.
2. Тест `test_accepted_with_insight_passes` держал `decided_at="2026-10-23"`; гейт «старения принятых»
   через шесть дней начал считать его просроченным, и ночная сборка покраснела **из-за календаря**.
3. `runs_chain.py` падал в CI на «манифест изменился»: локально CRLF, в CI LF. Перевод строки — не
   часть артефакта, но хеш считался по сырым байтам.

Эти три класса ловятся машинно. Проверка дешёвая (стандартная библиотека) и не требует GPU.

Что проверяется:
* **A. Календарные литералы.** В гейтах и тестах запрещены жёсткие даты вида `2026-10-23`, если они
  попадают в окно «свежести» (по умолчанию — последние 90 дней и ближайшие 90): такой тест состарится
  и упадёт сам. Разрешены относительные даты (`today - timedelta(...)`) и даты вне окна (исторические).
* **B. Хеш по сырым байтам.** Функция, в имени которой есть `sha`/`hash` и которая вызывает
  `read_bytes()`, обязана нормализовать переводы строк (`replace(b"\\r\\n", b"\\n")`) — иначе CI и
  рабочая копия дают разные хеши одного и того же файла.

Использование:
    python scripts/check_environment_assumptions.py            # проверка
    python scripts/check_environment_assumptions.py --today 2026-10-29
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCAN_DIRS = [ROOT / "scripts", ROOT / "morphogenesis" / "tests"]
WINDOW_DAYS = 90

ISO_DATE = re.compile(r"(?<![\d-])(20\d{2})-(\d{2})-(\d{2})(?![\d-])")
# Дата считается «влияющей на поведение», только если она в коде, а не в прозе: аргумент с датой
# (`decided_at=...`), либо сравнение. Иначе гейт ловит даты в докстрингах и становится шумом.
CODE_DATE = re.compile(
    r"(?:^|\s|\()(?:decided_at|created_at|review_at|closed_at|date|today|t0)\s*=\s*[\"']?20\d{2}-\d{2}-\d{2}"
    r"|(?:==|!=|>=|<=|>|<)\s*[\"']?20\d{2}-\d{2}-\d{2}"
    r"|20\d{2}-\d{2}-\d{2}[\"']?\s*(?:==|!=|>=|<=|>|<)"
)
HASH_FUNC = re.compile(r"def\s+\w*(?:sha|hash)\w*\s*\(")
READ_BYTES = re.compile(r"read_bytes\(\)")
CRLF_NORM = re.compile(r"replace\(\s*b?['\"]\\r\\n['\"]\s*,\s*b?['\"]\\n['\"]\s*\)")


def calendar_literals(today: dt.date, window_days: int) -> list[str]:
    problems: list[str] = []
    for base in SCAN_DIRS:
        if not base.exists():
            continue
        for path in sorted(base.rglob("*.py")):
            rel = path.relative_to(ROOT)
            for lineno, line in enumerate(path.read_text(encoding="utf-8", errors="replace").split("\n"), 1):
                if not CODE_DATE.search(line):
                    continue
                for m in ISO_DATE.finditer(line):
                    try:
                        stamp = dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
                    except ValueError:
                        continue
                    if abs((stamp - today).days) <= window_days:
                        problems.append(
                            f"{rel}:{lineno}: жёсткая дата {stamp} в окне ±{window_days} дней от "
                            f"{today} — тест состарится; используйте относительную дату"
                        )
    return problems


def raw_byte_hashes() -> list[str]:
    problems: list[str] = []
    for base in SCAN_DIRS:
        if not base.exists():
            continue
        for path in sorted(base.rglob("*.py")):
            text = path.read_text(encoding="utf-8", errors="replace")
            lines = text.split("\n")
            for i, line in enumerate(lines):
                if not HASH_FUNC.search(line):
                    continue
                # тело функции — до следующего def того же уровня (грубо, но достаточно)
                body = "\n".join(lines[i: i + 40])
                body = body.split("\ndef ")[0]
                if READ_BYTES.search(body) and not CRLF_NORM.search(body):
                    rel = path.relative_to(ROOT)
                    problems.append(
                        f"{rel}:{i + 1}: хеш считается по сырым байтам без нормализации переводов строк — "
                        f"в CI (LF) и локально (CRLF) получится разный хеш"
                    )
    return problems


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="гейты не зависят от календаря и концов строк")
    ap.add_argument("--today", default=None, help="дата проверки (YYYY-MM-DD), по умолчанию сегодня")
    ap.add_argument("--window-days", type=int, default=WINDOW_DAYS)
    args = ap.parse_args(argv)

    today = dt.date.fromisoformat(args.today) if args.today else dt.date.today()
    problems = calendar_literals(today, args.window_days) + raw_byte_hashes()
    if problems:
        print(f"[environment] ОШИБКА: {len(problems)} проблем (зависимость гейтов от окружения)")
        for p in problems[:15]:
            print("   ", p)
        return 1
    print(f"[environment] OK — календарных литералов в окне ±{args.window_days} дней нет, "
          f"сырых байтовых хешей без нормализации нет")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
