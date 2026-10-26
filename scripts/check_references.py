"""Проверить, что каждая ссылка из References рукописи есть в индексе библиотеки.

Правило контракта ([`AGENTS.md`](../AGENTS.md) §3a, [`library/publications/README.md`](../library/publications/README.md)):
ссылка в статьях и рукописи берётся из курированного индекса, а не из памяти и
не из чужой статьи. Если источник процитирован, но строки в индексе нет — это
дырка, а не стиль.

Что проверяется:

- блок `## References` в рукописи: все `http(s)://`-ссылки/DOI;
- тот же набор в `library/publications/README.md`;
- ссылка считается известной, если тот же нормализованный URL/DOI есть в индексе
  (регистр хоста и завершающая пунктуация не важны);
- отсутствие блока References — ошибка конфигурации (код 2), а не «всё хорошо».

Запуск:

    python scripts/check_references.py
    python scripts/check_references.py --paper manuscript/paper.md --index library/publications/README.md
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

REPO = Path(__file__).resolve().parents[1]
DEFAULT_PAPER = REPO / "manuscript" / "paper.md"
DEFAULT_INDEX = REPO / "library" / "publications" / "README.md"
URL_RE = re.compile(r"https?://[^\s)\]>,;]+")
TRAILING = ".,;:)"

# Разделы, которые идут после References и не содержат ссылок на источники.
STOP_HEADINGS = ("## Кратко", "## Appendix", "## Приложение")


def references_block(text: str) -> str | None:
    match = re.search(r"^##\s*References\s*$", text, re.MULTILINE)
    if not match:
        return None
    rest = text[match.end():]
    for heading in STOP_HEADINGS:
        idx = rest.find(heading)
        if idx != -1:
            rest = rest[:idx]
    return rest


def normalize(url: str) -> str:
    url = url.strip().rstrip(TRAILING)
    parts = urlsplit(url)
    host = parts.netloc.lower()
    path = parts.path.rstrip("/")
    query = f"?{parts.query}" if parts.query else ""
    return f"{parts.scheme.lower()}://{host}{path}{query}"


def urls_in(text: str) -> set[str]:
    return {normalize(u) for u in URL_RE.findall(text)}


def check(paper: Path, index: Path) -> tuple[int, list[str]]:
    paper_text = paper.read_text(encoding="utf-8")
    block = references_block(paper_text)
    if block is None:
        # Контракт: отсутствие блока References — ошибка конфигурации (код 2),
        # а не «всё хорошо». Терпимость к коду 2 настраивается в CI-шаге, не здесь.
        raise SystemExit(f"{paper}: нет блока '## References' — проверять нечего")
    cited = urls_in(block)
    known = urls_in(index.read_text(encoding="utf-8"))
    missing = sorted(cited - known)
    return len(cited), missing


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--paper", default=str(DEFAULT_PAPER))
    ap.add_argument("--index", default=str(DEFAULT_INDEX))
    args = ap.parse_args(argv)

    paper = Path(args.paper) if Path(args.paper).is_absolute() else REPO / args.paper
    index = Path(args.index) if Path(args.index).is_absolute() else REPO / args.index
    for path in (paper, index):
        if not path.is_file():
            print(f"нет файла: {path}")
            return 2

    count, missing = (0, [])
    try:
        count, missing = check(paper, index)
    except SystemExit as exc:  # нет блока References — это ошибка конфигурации
        print(str(exc))
        return 2
    print(f"ссылок в References: {count}, отсутствуют в индексе: {len(missing)}")
    for url in missing:
        print(f"НЕТ В ИНДЕКСЕ {url}")
    return 0 if not missing else 1


if __name__ == "__main__":
    sys.exit(main())
