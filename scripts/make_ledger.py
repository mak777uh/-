"""make_ledger.py — журнал экспериментов в README: id и статусы генерируются, не правятся руками.

Зачем. Таблица между `<!-- ledger:start -->` и `<!-- ledger:end -->` в `README.md` обязана
совпадать с `lab/registry.json` (это проверяет `lab.py validate`). Ручное ведение уже ломалось:
дубли id, пропущенные строки, статус, отставший от registry. Здесь машинно-выводимая часть
(id, порядок, статус) **собирается из registry**, а описательные колонки (period, question,
outcome, evidence) остаются авторскими: генератор их **не трогает**.

Режимы:
    python scripts/make_ledger.py --check   # гейт: id-набор и статусы совпадают с registry
    python scripts/make_ledger.py --sync    # привести статусы и добавить недостающие строки

Правило: колонки `period`, `question`, `outcome`, `evidence` заполняет человек; `id` и `status` —
только скрипт. Новая строка получает `TODO` в описательных колонках и красный `--check`,
пока человек (или учёный) не заполнит её из артефактов.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
REGISTRY = ROOT / "lab" / "registry.json"
START = "<!-- ledger:start -->"
END = "<!-- ledger:end -->"
HEADER = ("| id | status | period | question | outcome | evidence |\n"
          "| --- | --- | --- | --- | --- | --- |\n")


# Контракт §6a допускает метки статусов на двух языках. Здесь — какие написания
# считаются одним и тем же статусом; генератор их НЕ переписывает, а признаёт равными.
STATUS_ALIASES = {
    "closed": {"closed", "закрыто"},
    "running": {"running", "идёт", "идет"},
    "planned": {"planned", "план"},
    "blocked": {"blocked", "заблокировано"},
    "not_run": {"not_run", "not run", "not started", "не запускался"},
}
PREFERRED_LABEL = {
    "closed": "closed", "running": "running", "planned": "planned",
    "blocked": "blocked", "not_run": "not started",
}


def status_ok(registry_value: str, cell: str) -> bool:
    accepted = STATUS_ALIASES.get(registry_value)
    if accepted is None:
        return cell == registry_value
    return cell.strip().lower() in {a.lower() for a in accepted}


def registry_statuses() -> dict[str, str]:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    return {e["id"]: e.get("status") for e in data.get("experiments") or []}


def parse_rows(block: str) -> list[list[str]]:
    rows = []
    for line in block.splitlines():
        line = line.strip()
        if not line.startswith("|") or line.startswith("| ---") or line.startswith("| id |"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        rows.append(cells)
    return rows


def format_row(cells: list[str]) -> str:
    cells = (cells + [""] * 6)[:6]
    return "| " + " | ".join(cells) + " |"


def split_readme(text: str) -> tuple[str, str, str]:
    i = text.index(START) + len(START)
    j = text.index(END)
    return text[:i], text[i:j], text[j:]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--sync", action="store_true")
    args = ap.parse_args(argv)

    statuses = registry_statuses()
    text = README.read_text(encoding="utf-8")
    head, block, tail = split_readme(text)
    rows = parse_rows(block)
    errors: list[str] = []

    seen: dict[str, int] = {}
    for idx, cells in enumerate(rows):
        # контракт §6a: в первой ячейке можно перечислить НЕСКОЛЬКО id через запятую
        ids = [x.strip() for x in cells[0].split(",") if x.strip()]
        if not ids:
            errors.append(f"строка {idx + 1}: пустой id")
            continue
        for rid in ids:
            if rid in seen:
                errors.append(f"дубль id: {rid}")
            seen[rid] = idx
            if rid not in statuses:
                errors.append(f"id {rid} есть в README, но нет в registry")
                continue
            want = statuses[rid]
            if want and not status_ok(want, cells[1]):
                errors.append(f"{rid}: status «{cells[1]}», а в registry «{want}»")
        if any(c == "TODO" for c in cells[2:]):
            errors.append(f"{cells[0]}: описательные колонки не заполнены (TODO)")

    missing = [rid for rid in statuses if rid not in seen]
    for rid in missing:
        errors.append(f"id {rid} есть в registry, но нет строки в README")

    if args.check:
        if errors:
            print(f"[ledger] ОШИБКА: {len(errors)} расхождений")
            for e in errors[:12]:
                print("   ", e)
            return 1
        print(f"[ledger] OK — {len(rows)} строк совпадают с registry ({len(statuses)} экспериментов)")
        return 0

    if args.sync:
        changed = 0
        new_rows: list[list[str]] = []
        for cells in rows:
            rid = cells[0]
            if rid in statuses and statuses[rid] and not status_ok(statuses[rid], cells[1]):
                cells[1] = PREFERRED_LABEL.get(statuses[rid], statuses[rid])
                changed += 1
            new_rows.append(cells)
        for rid in missing:
            new_rows.append([rid, PREFERRED_LABEL.get(statuses[rid] or "", statuses[rid] or ""),
                             "TODO", "TODO", "TODO", "TODO"])
            changed += 1
        body = "\n" + HEADER + "\n".join(format_row(c) for c in new_rows) + "\n"
        README.write_text(head + body + tail, encoding="utf-8")
        print(f"[ledger] синхронизировано: {changed} правок, строк {len(new_rows)}")
        if missing:
            print("   заполните описательные колонки для:", ", ".join(missing))
        return 0

    print(f"[ledger] строк {len(rows)}, экспериментов в registry {len(statuses)}; "
          f"режимы: --check, --sync")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
