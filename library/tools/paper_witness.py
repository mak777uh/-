#!/usr/bin/env python
"""Witness-таблица для публикации: каждое число -> поле агрегата -> что доказывает / чего не доказывает.

Идея из портфеля владельца (`audits`: «what is checkable here, and by which command» +
«what is *not* claimed»): утверждение без команды проверки — мнение; утверждение без границы —
обещание. Инструмент перегенерирует таблицу **с проверкой**, поэтому она не стареет молча.

Запуск:
  python library/tools/paper_witness.py --spec library/witnesses/arxiv.json
  python library/tools/paper_witness.py --spec ... --write library/witnesses/arxiv.md
Коды: 0 — все числа совпали; 1 — есть расхождения (таблица показывает, где).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def get_field(data, dotted: str):
    cur = data
    for part in dotted.split("."):
        if isinstance(cur, list):
            if not part.isdigit() or int(part) >= len(cur):
                return None, False
            cur = cur[int(part)]
        elif isinstance(cur, dict):
            if part not in cur:
                return None, False
            cur = cur[part]
        else:
            return None, False
    return cur, True


def close(a, b) -> bool:
    try:
        fa, fb = float(a), float(b)
    except (TypeError, ValueError):
        return str(a) == str(b)
    if fb == 0:
        return abs(fa) <= 1e-9
    return abs(fa - fb) / abs(fb) <= 1e-4


def check_one(claim: dict) -> tuple[bool, str, str]:
    """(ok, значение, комментарий)."""
    path = REPO / claim["artifact"]
    if not path.exists():
        return False, "—", "файла нет"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return False, "—", f"не читается: {exc}"
    value, found = get_field(data, claim["field"])
    if not found:
        return False, "—", f"нет поля {claim['field']}"
    ok = close(value, claim["expect"])
    return ok, str(value), "" if ok else f"ожидалось {claim['expect']}"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Witness-таблица публикации")
    ap.add_argument("--spec", required=True)
    ap.add_argument("--write", default=None)
    args = ap.parse_args(argv)

    spec = json.loads((REPO / args.spec).read_text(encoding="utf-8"))
    rows, bad = [], []
    for claim in spec["claims"]:
        ok, value, note = check_one(claim)
        if not ok:
            bad.append((claim["id"], note))
        rows.append((claim, ok, value, note))

    out = [f"# Witness-таблица: {spec.get('paper', '')}", ""]
    if spec.get("note"):
        out += [spec["note"], ""]
    out += ["| id | утверждение | поле | значение | сходится | что доказывает | чего НЕ доказывает |",
            "|---|---|---|---|---|---|---|"]
    for claim, ok, value, _ in rows:
        mark = "да" if ok else "**нет**"
        out.append(f"| {claim['id']} | {claim['statement']} | `{claim['artifact']}` :: `{claim['field']}` | "
                   f"`{value}` | {mark} | {claim.get('proves','—')} | {claim.get('not_proves','—')} |")
    out += ["", "## Как воспроизвести", "",
            "```", f"python library/tools/paper_witness.py --spec {args.spec}", "```", "",
            "Таблица генерируется этим запуском: значение в столбце «значение» — прочитано из артефакта сейчас, "
            "а не взято из текста статьи."]
    text = "\n".join(out) + "\n"
    if args.write:
        (REPO / args.write).write_text(text, encoding="utf-8", newline="\n")
        print(f"записано: {args.write} | строк: {len(rows)} | расхождений: {len(bad)}")
    else:
        print(text)
    for cid, note in bad:
        print(f"РАСХОЖДЕНИЕ {cid}: {note}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
