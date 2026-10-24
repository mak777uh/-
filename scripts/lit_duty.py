"""Обязательный шаг литературы в каждом цикле.

Почему появился: в дежурстве литература была условным шагом («нет источника — поищи»),
и при наличии экспериментов он выпадал. Здесь очередь вопросов фиксирована файлом
`library/lit-questions.md`; каждый проход берёт следующий открытый вопрос, ищет по нему
и отмечает результат. Это делает работу с источниками **наблюдаемой**, а не обещанной.

    python scripts/lit_duty.py --list          # очередь вопросов
    python scripts/lit_duty.py --next          # взять следующий, найти кандидатов, отметить
    python scripts/lit_duty.py --mark Q2 --status searched-0 --note "..."

Формат `library/lit-questions.md` — таблица:

    | id | вопрос | статус | дата | заметка |
    | Q1 | ... | open | — | — |

Статусы: `open` (не искали), `searched-0` (искали, ничего не взяли), `searched-1` (взяли
источник), `done` (вопрос закрыт). `--next` берёт первый `open`.
"""
from __future__ import annotations

import argparse
import datetime as dt
import io
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
QUESTIONS = ROOT / "library" / "lit-questions.md"
sys.path.insert(0, str(ROOT / "scripts"))
import lit_search  # noqa: E402


def load_rows() -> list[dict]:
    if not QUESTIONS.exists():
        return []
    text = io.open(QUESTIONS, encoding="utf-8").read()
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|") or "---" in line:
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 5 or cells[0] == "id":
            continue
        rows.append({"id": cells[0], "question": cells[1], "status": cells[2],
                     "date": cells[3], "note": cells[4]})
    return rows


def save_rows(rows: list[dict]) -> None:
    head = "# Вопросы литературы (очередь обязательного шага)\n\n" \
           "Каждый проход дежурства берёт первый `open` и ищет по нему. " \
           "Статусы: `open`, `searched-0`, `searched-1`, `done`.\n\n" \
           "| id | вопрос | статус | дата | заметка |\n| --- | --- | --- | --- | --- |\n"
    lines = [head]
    for r in rows:
        lines.append(f"| {r['id']} | {r['question']} | {r['status']} | {r['date']} | {r['note']} |\n")
    lines.append("\n## Как пополнять\n\n"
                 "- Вопрос формулируем на английском (научные термины), в таблицу можно по-русски.\n"
                 "- Один вопрос = 1–2 запроса; если ничего не подошло — `searched-0` с пояснением.\n"
                 "- Взяли работу — заводим запись в `hypotheses/` и `searched-1` со ссылкой на P-номер.\n")
    QUESTIONS.write_text("".join(lines), encoding="utf-8", newline="\n")


def today() -> str:
    return dt.date.today().isoformat()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Очередь вопросов литературы")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--next", action="store_true")
    ap.add_argument("--mark", default=None)
    ap.add_argument("--status", default="searched-0")
    ap.add_argument("--note", default="")
    ap.add_argument("--from", dest="since", default="2023-01-01")
    ap.add_argument("--rows", type=int, default=6)
    args = ap.parse_args(argv)

    rows = load_rows()
    if args.list:
        for r in rows:
            print(f"{r['id']:3} [{r['status']:11}] {r['question'][:90]}  ({r['date']})")
        return 0

    if args.mark:
        for r in rows:
            if r["id"] == args.mark:
                r["status"] = args.status
                r["date"] = today()
                if args.note:
                    r["note"] = args.note
        save_rows(rows)
        print(f"{args.mark}: {args.status} ({today()})")
        return 0

    if args.next:
        pending = [r for r in rows if r["status"] == "open"]
        if not pending:
            print("открытых вопросов нет — дополните library/lit-questions.md")
            return 0
        q = pending[0]
        print(f"вопрос {q['id']}: {q['question']}")
        items = lit_search.search(q["question"], args.since, args.rows, False, True)
        if not items:
            print("кандидатов нет — отметить searched-0")
            return 0
        for it in items:
            print(f"{it['year']} | {it['doi']} | {it['journal']} | {it['title'][:100]}")
            if it["abstract"]:
                print(f"     ABS: {it['abstract'][:200]}…")
        print(f"\nкандидатов: {len(items)}; отметить: --mark {q['id']} --status searched-0|searched-1")
        return 0

    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
