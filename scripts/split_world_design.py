"""split_world_design.py — разложить план линии по файлам, оставив индекс.

Зачем. К 31.10 `docs/world-design.md` вырос до 8080 строк и 102 разделов (§10aa…§10du). Это главный документ линии,
и его нельзя ни прочитать целиком, ни отревьюить, ни спокойно править вдвоём. При этом каждый раздел — рабочая
запись с числами и ссылками на артефакты, терять нельзя ничего.

Разбиение — по **буквенным диапазонам идентификаторов**, а не по догадкам о теме: так оно детерминировано и
проверяемо. Границы при этом совпадают со смыслом (a — начало пруда, b — отбор и сосуществование в пруду,
c — неоднородность поля, d — метрики и форма, дальше — обитаемость и каналы).

`docs/world-design.md` остаётся **индексом**: назначение, как читать, полная таблица «раздел → файл». Ссылки вида
«§10dc» продолжают работать: идентификатор находится по индексу.

Проверка: `scripts/check_plan_split.py` (каждый раздел ровно в одном файле, ничего не потеряно).

Запуск:
    python scripts/split_world_design.py            # показать план разбиения
    python scripts/split_world_design.py --write    # записать файлы и индекс
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "docs" / "world-design.md"
PLAN_DIR = ROOT / "docs" / "plan"

# (файл, первая буква после «10», границы по второй букве, заголовок)
PARTS = [
    ("10a-pond-organization.md", "a", None, None,
     "Pond: how organisation and a line appeared (24–25.10, §10aa–§10az)"),
    ("10b-pond-selection.md", "b", None, None,
     "Pond: selection, the price of a trait, coexistence (25–28.10, §10ba–§10bz)"),
    ("10c-field-heterogeneity.md", "c", None, None,
     "Field: heterogeneity of inflow and its dose (30.10, §10ca–§10cz)"),
    ("10d-field-metrics-and-form.md", "d", "a", "l",
     "Field: what the counter measures, lifetime, percolation, form (30–31.10, §10da–§10dl)"),
    ("10e-habitability-and-channels.md", "d", "m", "u",
     "Habitability, the self-model, channels and memory (31.10, §10dm–§10du)"),
]

SECTION_RE = re.compile(r"^## (10[a-z]{2}(?:-[a-z])?)\. (.+)$")


def parse(text: str) -> tuple[str, list[tuple[str, str, str]]]:
    """Вернуть (шапка до первого раздела, [(id, заголовок, тело)])."""
    lines = text.split("\n")
    starts = [i for i, ln in enumerate(lines) if SECTION_RE.match(ln)]
    if not starts:
        raise SystemExit("в файле нет разделов вида `## 10xx.`")
    header = "\n".join(lines[: starts[0]]).rstrip("\n")
    sections: list[tuple[str, str, str]] = []
    for k, i in enumerate(starts):
        end = starts[k + 1] if k + 1 < len(starts) else len(lines)
        block = "\n".join(lines[i:end]).rstrip("\n")
        m = SECTION_RE.match(lines[i])
        sections.append((m.group(1), m.group(2), block))
    return header, sections


def target_for(sid: str) -> str:
    second = sid[2]          # a, b, c, d
    third = sid[3] if len(sid) > 3 else ""
    for name, want_second, lo, hi, _title in PARTS:
        if second != want_second:
            continue
        if lo is None:
            return name
        if lo <= third <= hi:
            return name
    raise SystemExit(f"раздел {sid} не попал ни в одну часть")


def build_index(sections: list[tuple[str, str, str]]) -> str:
    by_part: dict[str, list[tuple[str, str]]] = {}
    for sid, title, _body in sections:
        by_part.setdefault(target_for(sid), []).append((sid, title))
    lines = [
        "# Plan of the line: index",
        "",
        "This file is the **index** of the working plan. The plan itself lives in [`plan/`](plan/), split by identifier",
        "range so that it can be read, reviewed and edited without opening eight thousand lines.",
        "",
        "Why it is split: on 31.10 this file reached **8080 lines and 102 sections** and stopped being readable. The",
        "sections were not rewritten, only moved; each one keeps its identifier, so every reference of the form",
        "«§10dc» still resolves through the table below.",
        "",
        "## Where the sections live",
        "",
        "| file | covers | what is inside |",
        "| --- | --- | --- |",
    ]
    for name, _second, _lo, _hi, title in PARTS:
        ids = by_part.get(name, [])
        if not ids:
            continue
        span = f"§{ids[0][0]}–§{ids[-1][0]}" if len(ids) > 1 else f"§{ids[0][0]}"
        lines.append(f"| [`plan/{name}`](plan/{name}) | {span} ({len(ids)}) | {title} |")
    lines += [
        "",
        "## Full table: section → file",
        "",
        "| id | title | file |",
        "| --- | --- | --- |",
    ]
    for name, _s, _l, _h, _t in PARTS:
        for sid, title in by_part.get(name, []):
            safe = title.replace("|", "\\|")
            lines.append(f"| §{sid} | {safe} | [`plan/{name}`](plan/{name}) |")
    lines += [
        "",
        "## How to use this",
        "",
        "1. Find the identifier in the table above (or search this file for it).",
        "2. Open the file it points to; sections are in the same order as they were written.",
        "3. Numbers in a section name the aggregate or artifact they come from; the script index is",
        "   [`scripts-index.md`](scripts-index.md).",
        "",
        "**Machine check.** `scripts/check_plan_split.py` verifies that every section of the original file exists exactly",
        "once across `plan/`, and that this index lists all of them.",
        "",
    ]
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="разложить план по файлам, оставив индекс")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    text = SRC.read_text(encoding="utf-8")
    header, sections = parse(text)
    by_part: dict[str, list[tuple[str, str, str]]] = {}
    for sid, title, body in sections:
        by_part.setdefault(target_for(sid), []).append((sid, title, body))

    print(f"разделов: {len(sections)}")
    for name, _s, _l, _h, _t in PARTS:
        items = by_part.get(name, [])
        if items:
            print(f"  {name:38s} {len(items):3d}  §{items[0][0]}…§{items[-1][0]}")

    if not args.write:
        print("(сухой прогон; добавьте --write)")
        return 0

    PLAN_DIR.mkdir(parents=True, exist_ok=True)
    for name, _s, _l, _h, title in PARTS:
        items = by_part.get(name, [])
        if not items:
            continue
        parts = [
            f"# {title}",
            "",
            "Part of the working plan. The index and the full section table are in "
            "[`../world-design.md`](../world-design.md).",
            "",
            "Sections are in the order they were written; identifiers are preserved, so references elsewhere still",
            "resolve.",
            "",
        ]
        for _sid, _ttl, body in items:
            parts.append(body)
            parts.append("")
        (PLAN_DIR / name).write_text("\n".join(parts).rstrip("\n") + "\n", encoding="utf-8", newline="\n")
        print(f"  записано: docs/plan/{name}")

    index = build_index(sections)
    SRC.write_text(index.rstrip("\n") + "\n", encoding="utf-8", newline="\n")
    print(f"  индекс: docs/world-design.md ({len(index.splitlines())} строк вместо 8080)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
