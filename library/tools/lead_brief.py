#!/usr/bin/env python
"""lead_brief.py — краткая сводка главному агенту: результат -> число -> артефакт -> что меняет.

Зачем: важные результаты у меня ложились в `library/` (science-review, claims-evidence, answers), а к
главному не попадали, пока он сам не прочитает. Здесь — один канал с отметкой «отправлено», чтобы
результат не терялся и не дублировался.

Запуск:
  python library/tools/lead_brief.py add --result "..." --number "..." --artifact "..." --changes "..."
  python library/tools/lead_brief.py pending          # что ещё не отправлено
  python library/tools/lead_brief.py flush            # дописать pending в lab/notices.md и пометить
Коды: 0 — ок; 1 — добавить не удалось (нет обязательного поля).
"""
from __future__ import annotations

import argparse
import datetime
import io
import json
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[2]
BRIEF = REPO / "library" / "lead-brief.md"
STATE = REPO / "library" / ".lead-brief.json"
NOTICES = REPO / "lab" / "notices.md"


def load() -> list[dict]:
    if not STATE.exists():
        return []
    try:
        return json.loads(STATE.read_text(encoding="utf-8")).get("items", [])
    except Exception:
        return []


def save(items: list[dict]) -> None:
    STATE.write_text(json.dumps({"items": items}, ensure_ascii=False, indent=2) + "\n",
                     encoding="utf-8", newline="\n")
    lines = ["# Сводка главному агенту", "",
             "Один канал для важных результатов: каждый пункт несёт число, артефакт и «что меняет».",
             "Пункты без даты отправки — ещё не отправлены (см. `lead_brief.py pending`).", ""]
    for it in reversed(items):
        sent = it.get("sent_at") or "НЕ ОТПРАВЛЕНО"
        lines += [f"## {it['at']} — {it['result']}", "",
                  f"- **число:** {it['number']}",
                  f"- **артефакт:** {it['artifact']}",
                  f"- **что меняет:** {it['changes']}",
                  f"- **отправлено:** {sent}"]
        if it.get("note"):
            lines.append(f"- **оговорка:** {it['note']}")
        lines.append("")
    BRIEF.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="сводка главному")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add")
    for f in ("result", "number", "artifact", "changes"):
        a.add_argument(f"--{f}", required=True)
    a.add_argument("--note", default="")
    sub.add_parser("pending")
    sub.add_parser("flush")
    args = ap.parse_args(argv)

    items = load()
    if args.cmd == "add":
        items.append({"at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                      "result": args.result, "number": args.number,
                      "artifact": args.artifact, "changes": args.changes,
                      "note": args.note, "sent_at": None})
        save(items)
        print(f"добавлено; всего пунктов: {len(items)}; не отправлено: "
              f"{sum(1 for i in items if not i.get('sent_at'))}")
        return 0

    pending = [i for i in items if not i.get("sent_at")]
    if args.cmd == "pending":
        if not pending:
            print("неотправленных нет")
            return 0
        for it in pending:
            print(f"- {it['at']} | {it['result']} | {it['number']}")
        print(f"всего не отправлено: {len(pending)}")
        return 0

    # flush
    if not pending:
        print("нечего отправлять")
        return 0
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    block = [f"\n\n### {now} — библиотекарь → **главному**: сводка результатов ({len(pending)})", ""]
    for it in pending:
        block.append(f"- **{it['result']}** — {it['number']}; артефакт: `{it['artifact']}`; "
                     f"меняет: {it['changes']}" + (f" (оговорка: {it['note']})" if it.get("note") else ""))
    block.append("")
    with io.open(NOTICES, "a", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(block) + "\n")
    for it in pending:
        it["sent_at"] = now
    save(items)
    print(f"отправлено главному: {len(pending)} | дописано в lab/notices.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
