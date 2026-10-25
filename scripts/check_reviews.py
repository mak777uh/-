#!/usr/bin/env python
"""check_reviews.py — ревью рецензента обязаны быть проверками, а не мнениями.

Зачем: 25.10 появилась роль `reviewer` — научный рецензент-скептик. У неё та же
болезнь, что у всех: «держится» можно написать, не пересчитав. Гейт требует:
  * вердикт из четырёх допустимых;
  * заполненные «Что пересчитано» и «Что убьёт утверждение»;
  * для вердикта «держится» — ссылку на артефакт или команду пересчёта;
  * индекс `lab/reviews/index.json`, покрывающий все файлы;
  * пометку устаревших ревью (старше 7 дней) по утверждениям, которые до сих пор
    помечены `подтверждено`.

Запуск (из корня):  python scripts/check_reviews.py
"""
from __future__ import annotations

import datetime as dt
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEWS = ROOT / "lab" / "reviews"
INDEX = REVIEWS / "index.json"
CLAIMS = ROOT / "manuscript" / "CLAIMS.md"

VERDICTS = {"держится", "не держится", "держится с оговоркой", "проверить нельзя"}
STALE_DAYS = 7
ARTIFACT_HINTS = ("morphogenesis/experiments", "scripts/", "reports/", "library/tools", "python ")


def parse_review(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    out = {"file": str(path.relative_to(ROOT)), "title": "", "verdict": "", "checked": "",
           "killer": "", "section": "", "date": ""}
    m = re.search(r"^#\s*Проверка:\s*(.+)$", text, re.M)
    if m:
        out["title"] = m.group(1).strip()
    for key, field in (("Вердикт", "verdict"), ("Что пересчитано", "checked"),
                       ("Что убьёт утверждение", "killer"), ("Раздел/строка CLAIMS", "section")):
        m = re.search(rf"^-\s*\*\*{re.escape(key)}:\*\*\s*(.*)$", text, re.M)
        if m:
            out[field] = m.group(1).strip()
    m = re.match(r"(\d{4}-\d{2}-\d{2})", path.name)
    out["date"] = m.group(1) if m else ""
    out["_text"] = text
    return out


def confirmed_claims() -> set[str]:
    """Строки CLAIMS со статусом «подтверждено» — чтобы ловить устаревшие ревью."""
    if not CLAIMS.exists():
        return set()
    out = set()
    for line in CLAIMS.read_text(encoding="utf-8").splitlines():
        if line.startswith("|") and "подтверждено" in line:
            cells = [c.strip() for c in line.strip("|").split("|")]
            if cells:
                out.add(cells[0][:80])
    return out


def main() -> int:
    if not REVIEWS.exists():
        print("[reviews] каталога lab/reviews нет — рецензент ещё не начинал")
        return 0
    files = sorted(p for p in REVIEWS.glob("*.md") if p.name != "README.md")
    if not files:
        print("[reviews] файлов ревью пока нет — проверять нечего")
        return 0

    problems: list[str] = []
    warnings: list[str] = []
    parsed = {}
    for path in files:
        r = parse_review(path)
        parsed[r["file"]] = r
        if r["verdict"] not in VERDICTS:
            problems.append(f"{r['file']}: вердикт «{r['verdict'] or '—'}» не из четырёх допустимых")
        if not r["checked"]:
            problems.append(f"{r['file']}: не заполнено «Что пересчитано» — это мнение, а не проверка")
        if not r["killer"]:
            problems.append(f"{r['file']}: не заполнено «Что убьёт утверждение»")
        if r["verdict"] == "держится":
            hint = [h for h in ARTIFACT_HINTS if h in r["_text"]]
            if not hint:
                problems.append(f"{r['file']}: вердикт «держится» без ссылки на артефакт или команду пересчёта")
        if not r["date"]:
            warnings.append(f"{r['file']}: в имени нет даты (YYYY-MM-DD)")

    # индекс
    index_ok = False
    if INDEX.exists():
        try:
            data = json.loads(INDEX.read_text(encoding="utf-8"))
            index_ok = True
        except Exception as exc:
            problems.append(f"index.json не читается: {exc}")
            data = {}
        if index_ok:
            listed = {e.get("file") for e in data.get("reviews", [])}
            missing = sorted(set(parsed) - listed)
            extra = sorted(listed - set(parsed))
            if missing:
                problems.append(f"index.json не содержит: {', '.join(missing)}")
            if extra:
                problems.append(f"index.json ссылается на несуществующие файлы: {', '.join(extra)}")
    else:
        problems.append("нет lab/reviews/index.json — ревью без индекса не проверяются машинно")

    # устаревание
    today = dt.date.today()
    live = confirmed_claims()
    for r in parsed.values():
        if not r["date"] or r["verdict"] != "держится":
            continue
        try:
            age = (today - dt.date.fromisoformat(r["date"])).days
        except ValueError:
            continue
        if age <= STALE_DAYS:
            continue
        still = any(r["title"][:40] in c or c[:40] in r["title"] for c in live) if live else False
        if still:
            warnings.append(f"{r['file']}: ревью {age} дн., утверждение до сих пор «подтверждено» — перепроверьте")

    print(f"[reviews] файлов: {len(parsed)}; вердикты: "
          f"{', '.join(sorted({r['verdict'] for r in parsed.values()})) or '—'}")
    for w in warnings:
        print(f"[reviews] ВНИМАНИЕ: {w}")
    if problems:
        for p in problems:
            print(f"[reviews] ОШИБКА: {p}")
        return 1
    print("[reviews] OK — ревью оформлены как проверки и покрыты индексом")
    return 0


if __name__ == "__main__":
    sys.exit(main())
