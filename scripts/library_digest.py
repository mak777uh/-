#!/usr/bin/env python
"""Дайджест библиотеки: что прочитано, что цитируется, что лежит мёртвым грузом.

Зачем: конспекты в `library/` растут быстрее, чем мы их читаем. Гипотезы должны
опираться на источники (AGENTS §3a, стадия 1), а не на память; для этого перед
каждой новой волной нужно видеть, какие пункты библиотеки **ещё не использованы**
и какие уже процитированы в отчётах, статьях и рукописи.

Скрипт ничего не меняет и не лезет в науку: он собирает инвентарь.

Запуск (из корня репозитория):

    python scripts/library_digest.py                 # сводка в stdout
    python scripts/library_digest.py --write _hourly/library-digest.md
    python scripts/library_digest.py --check         # 1, если у гипотез нет ссылок

Формат входа — конспекты вида:

    ## C. Порядок данных и точность
    ### R5. Порядок примеров как фактор
    **[Curriculum Learning](https://doi.org/10.1145/...)** — авторы...
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LIBRARY = REPO / "library"
CITED_IN = [
    REPO / "reports",
    REPO / "articles",
    REPO / "manuscript",
]
SECTION_RE = re.compile(r"^##\s+(?P<title>.+?)\s*$")
ENTRY_RE = re.compile(r"^###\s+(?P<id>[A-Za-z0-9._-]+)\.\s*(?P<title>.+?)\s*$")
LINK_RE = re.compile(r"\[(?P<label>[^\]]+)\]\((?P<url>[^)]+)\)")


def _display_path(path: Path) -> str:
    """Путь относительно репозитория; для внешних файлов (тесты) — как есть."""
    try:
        return str(path.relative_to(REPO)).replace("\\", "/")
    except ValueError:
        return str(path)


def parse_entries(path: Path) -> list[dict]:
    """Разобрать конспект на пункты: id, заголовок, ссылка, секция."""
    entries: list[dict] = []
    section = ""
    current: dict | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        section_match = SECTION_RE.match(line)
        if section_match:
            section = section_match.group("title").strip()
            current = None
            continue
        entry_match = ENTRY_RE.match(line)
        if entry_match:
            current = {
                "id": entry_match.group("id"),
                "title": entry_match.group("title").strip(),
                "section": section,
                "file": _display_path(path),
                "url": "",
            }
            entries.append(current)
            continue
        if current is not None and not current["url"]:
            link = LINK_RE.search(line)
            if link:
                current["url"] = link.group("url")
    return entries


def collect_entries() -> list[dict]:
    entries: list[dict] = []
    if LIBRARY.is_dir():
        for path in sorted(LIBRARY.rglob("*.md")):
            if path.name.upper() == "README.MD":
                continue
            entries.extend(parse_entries(path))
    return entries


def corpus() -> str:
    """Тексты, где может быть цитата: отчёты, статьи, рукопись, registry."""
    parts: list[str] = []
    for root in CITED_IN:
        if root.is_dir():
            for path in root.rglob("*.md"):
                parts.append(path.read_text(encoding="utf-8", errors="ignore"))
    registry = REPO / "lab" / "registry.json"
    if registry.is_file():
        parts.append(registry.read_text(encoding="utf-8", errors="ignore"))
    return "\n".join(parts)


def mark_usage(entries: list[dict], text: str) -> list[dict]:
    for entry in entries:
        needles = [entry["id"], entry["title"]]
        if entry["url"]:
            needles.append(entry["url"])
            # DOI без префикса тоже встречается в текстах
            if "doi.org/" in entry["url"]:
                needles.append(entry["url"].split("doi.org/")[-1])
        used = any(needle and needle in text for needle in needles)
        entry["cited"] = used
    return entries


def build_report(entries: list[dict]) -> str:
    by_file: dict[str, list[dict]] = {}
    for entry in entries:
        by_file.setdefault(entry["file"], []).append(entry)
    total = len(entries)
    used = [e for e in entries if e.get("cited")]
    unused = [e for e in entries if not e.get("cited")]

    lines = [
        "# Дайджест библиотеки",
        "",
        f"Пунктов всего: **{total}**; процитировано в отчётах/статьях/рукописи: "
        f"**{len(used)}**; не использовано: **{len(unused)}**.",
        "",
        "## По файлам",
        "",
        "| Файл | Пунктов | Из них процитировано |",
        "|---|---|---|",
    ]
    for file, items in sorted(by_file.items()):
        cited = sum(1 for e in items if e.get("cited"))
        lines.append(f"| `{file}` | {len(items)} | {cited} |")

    if unused:
        lines += ["", "## Не использовано (кандидаты в гипотезы)", ""]
        for entry in unused:
            lines.append(
                f"- **{entry['id']}** · {entry['title']} — `{entry['file']}`, "
                f"секция «{entry['section']}»{(' · ' + entry['url']) if entry['url'] else ''}"
            )
    if used:
        lines += ["", "## Уже процитировано", ""]
        for entry in used:
            lines.append(f"- **{entry['id']}** · {entry['title']} — `{entry['file']}`")
    lines += [
        "",
        "## Как пользоваться",
        "",
        "1. Перед новой волной взять 2–3 пункта из «не использовано» и ответить",
        "   на вопрос: что они меняют в нашей гипотезе или в формулировке вывода.",
        "2. Если меняют — записать гипотезу с ссылкой на пункт (AGENTS §3a, стадия 1).",
        "3. Если не меняют — так и записать: «проверено, не влияет» (иначе через",
        "   неделю снова будем читать то же самое).",
        "",
    ]
    return "\n".join(lines)


def hypotheses_without_sources() -> list[str]:
    """Гипотезы из registry, в которых нет ссылки на library/."""
    registry = REPO / "lab" / "registry.json"
    if not registry.is_file():
        return []
    data = json.loads(registry.read_text(encoding="utf-8"))
    missing: list[str] = []
    for item in data.get("program", {}).get("next_hypotheses", []) or []:
        blob = json.dumps(item, ensure_ascii=False)
        if "library/" not in blob and "doi.org" not in blob and "arxiv.org" not in blob:
            missing.append(str(item.get("id")))
    return missing


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", help="куда сохранить дайджест (markdown)")
    ap.add_argument(
        "--check",
        action="store_true",
        help="код 1, если у гипотез из registry нет ни одной ссылки на источник",
    )
    args = ap.parse_args(argv)

    entries = mark_usage(collect_entries(), corpus())
    report = build_report(entries)
    if args.write:
        out = Path(args.write)
        if not out.is_absolute():
            out = REPO.parent / out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report, encoding="utf-8")
        print(f"[library] дайджест записан: {out}")
    else:
        print(report)

    missing = hypotheses_without_sources()
    if missing:
        print(
            f"[library] гипотез без ссылки на источник: {len(missing)} "
            f"({', '.join(missing[:8])}{'…' if len(missing) > 8 else ''})"
        )
    if args.check and missing:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
