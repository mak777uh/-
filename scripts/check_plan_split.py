"""check_plan_split.py — план разложен по файлам без потерь и без дублей.

Зачем. 31.10 `docs/world-design.md` (8080 строк, 99 разделов) разложен по `docs/plan/`, а сам файл стал индексом.
Такое разбиение опасно ровно одним: **раздел может потеряться или задвоиться**, и заметить это глазами в пяти файлах
труднее, чем в одном. Гейт проверяет:

1. каждый раздел `## 10xx.` существует **ровно в одном** файле `docs/plan/`;
2. все они перечислены в индексе `docs/world-design.md`;
3. в индексе нет ссылок на разделы, которых нет в файлах;
4. индекс не отстал (число строк таблицы совпадает с числом найденных разделов).

Запуск:
    python scripts/check_plan_split.py
    python scripts/check_plan_split.py --ci
"""
from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "plan"
INDEX = ROOT / "docs" / "world-design.md"
SECTION_RE = re.compile(r"^## (10[a-z]{2}(?:-[a-z])?)\. ", re.M)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="целостность разбиения плана")
    ap.add_argument("--fix-index", action="store_true",
                    help="пересобрать таблицу «раздел → файл» в docs/world-design.md из файлов плана")
    ap.add_argument("--ci", action="store_true")
    args = ap.parse_args(argv)

    if args.fix_index:
        rows = []
        for p in sorted(PLAN.glob("*.md")):
            for m in re.finditer(r"^## (10[a-z]{2}(?:-[a-z])?)\. (.+)$",
                                 p.read_text(encoding="utf-8"), re.M):
                rows.append((m.group(1), m.group(2).replace("|", "\\|"), p.name))
        rows.sort(key=lambda r: r[0])
        text = INDEX.read_text(encoding="utf-8")
        head, sep, _tail = text.partition("## Full table: section → file")
        table = ["## Full table: section → file", "", "| id | title | file |", "| --- | --- | --- |"]
        table += [f"| §{sid} | {title} | [`plan/{name}`](plan/{name}) |" for sid, title, name in rows]
        INDEX.write_text(head + "\n".join(table) + "\n", encoding="utf-8", newline="\n")
        print(f"[plan-split] индекс пересобран: {len(rows)} разделов")
        return 0

    problems: list[str] = []
    # часть 0 — спецификация мира, разделов §10xx в ней нет; проверяем, что она не пуста и на месте
    spec = PLAN / "00-pond-specification.md"
    if not spec.is_file() or spec.stat().st_size < 5000:
        problems.append("нет или подозрительно мала часть 0 (docs/plan/00-pond-specification.md)")
    in_files: dict[str, list[str]] = {}
    for p in sorted(PLAN.glob("*.md")):
        ids = SECTION_RE.findall(p.read_text(encoding="utf-8"))
        in_files[p.name] = ids
    all_ids = [i for ids in in_files.values() for i in ids]
    if not all_ids:
        problems.append("в docs/plan/ не найдено ни одного раздела `## 10xx.`")

    dup = {k: v for k, v in Counter(all_ids).items() if v > 1}
    for sid, n in dup.items():
        where = [name for name, ids in in_files.items() if sid in ids]
        problems.append(f"раздел §{sid} встречается {n} раз: {', '.join(where)}")

    if not INDEX.is_file():
        problems.append("нет docs/world-design.md (индекс)")
        index_text = ""
    else:
        index_text = INDEX.read_text(encoding="utf-8")
        listed = set(re.findall(r"\|\s*§(10[a-z]{2}(?:-[a-z])?)\s*\|", index_text))
        missing_in_index = sorted(set(all_ids) - listed)
        extra_in_index = sorted(listed - set(all_ids))
        for sid in missing_in_index[:10]:
            problems.append(f"раздел §{sid} есть в файлах, но не в индексе")
        for sid in extra_in_index[:10]:
            problems.append(f"индекс ссылается на §{sid}, которого нет в файлах")
        if len(listed) != len(all_ids):
            problems.append(f"индекс перечисляет {len(listed)} разделов, в файлах {len(all_ids)}")

    for msg in problems[:20]:
        print("  ВНИМАНИЕ:", msg)
    if len(problems) > 20:
        print(f"  … и ещё {len(problems) - 20}")
    if problems:
        print(f"[plan-split] проблем: {len(problems)}")
        return 1 if args.ci else 0
    print(f"[plan-split] целостно: {len(all_ids)} разделов в {len(in_files)} файлах, все в индексе")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
