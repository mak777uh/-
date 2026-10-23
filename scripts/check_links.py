"""Проверить относительные ссылки в markdown-файлах репозитория.

Зачем: рукопись, отчёты и карточки читают люди и ревьюеры, а битая относительная
ссылка — это либо потерянный артефакт, либо файл, который переименовали и забыли
поправить. `lab.py validate` проверяет журнал README и карту рукописи, но не
ссылки, поэтому дырка закрывается здесь.

Правила:

- проверяются только относительные ссылки и картинки; `http(s)://`, `mailto:`
  и ссылки-якоря (`#...`) не трогаются (внешние URL проверит отдельный прогон,
  а якоря зависят от рендера);
- `#fragment` у относительной ссылки отбрасывается: существование файла — да,
  существование заголовка — нет (это не задача линтера);
- цель может быть файлом **или** каталогом (`reports/figures/`);
- содержимое блоков кода (``` и ~~~) не сканируется: там примеры, а не ссылки;
- `dist/` и `.venv/` по умолчанию не обходятся: `dist/` в git не едет.

Запуск:

    python scripts/check_links.py                 # публичные документы
    python scripts/check_links.py --all           # весь репозиторий
    python scripts/check_links.py manuscript/paper.md

Код возврата 1, если хоть одна ссылка битая.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

REPO = Path(__file__).resolve().parents[1]
LINK_RE = re.compile(r"!?\[[^\]]*\]\(\s*([^)\s]+)(?:\s+\"[^\"]*\")?\s*\)")
SKIP_DIRS = {".git", ".venv", "venv-cuda", "dist", "__pycache__", ".ruff_cache", ".pytest_cache"}
# замороженные рукописи сохраняются как были: их относительные ссылки не сверяем
SKIP_PATHS = {"manuscript/archive"}
EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "tel:", "ftp://")

# Публичные документы: то, что читает человек снаружи репозитория.
DEFAULT_TARGETS = (
    "README.md",
    "AGENTS.md",
    "lab/README.md",
    "lab/notices.md",
    "manuscript/README.md",
    "manuscript/paper.md",
    "manuscript/CLAIMS.md",
    "manuscript/CHANGELOG.md",
    "manuscript/SUPPLEMENT.md",
    "reports/README.md",
    "articles/README.md",
    "colab/README.md",
    "kaggle/README.md",
    "library/README.md",
    "library/publications/README.md",
    "docs/dataset/DATASET_CARD.md",
    "docs/benchmark/BENCHMARK_v0.md",
)


def iter_markdown(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    out = []
    for item in path.rglob("*.md"):
        rel_parts = item.relative_to(REPO).parts
        if SKIP_DIRS & set(rel_parts):
            continue
        if any("/".join(rel_parts[: i + 1]) in SKIP_PATHS for i in range(len(rel_parts) - 1)):
            continue

            continue
        out.append(item)
    return sorted(out)


def links_in(text: str):
    """(номер строки, цель) для ссылок вне блоков кода."""
    in_fence = False
    fence_marker = ""
    for lineno, line in enumerate(text.splitlines(), 1):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            marker = stripped[:3]
            if not in_fence:
                in_fence, fence_marker = True, marker
            elif marker == fence_marker:
                in_fence, fence_marker = False, ""
            continue
        if in_fence:
            continue
        for match in LINK_RE.finditer(line):
            yield lineno, match.group(1)


def resolve(source: Path, target: str) -> Path | None:
    if not target or target.startswith(EXTERNAL_PREFIXES):
        return None
    clean = unquote(target.split("#", 1)[0])
    if not clean:
        return None  # чисто якорная ссылка
    return (source.parent / clean).resolve()


def display_path(path: Path) -> str:
    """Путь для сообщения: относительно репозитория, если он внутри него."""
    try:
        return str(path.relative_to(REPO))
    except ValueError:
        return str(path)


def _git_ignored(path: Path) -> bool:
    """Игнорируется ли путь гитом (то есть в репозиторий он не едет).

    Ссылки на веса (`nca_final.pt`) и на сырые per-run строки (`*.jsonl`) ведут
    на файлы, которых в git нет по контракту §5/§5a. Локально они существуют, и
    проверка проходила; на чистой машине (CI) они отсутствуют — это не битая
    ссылка, а «локальный артефакт, в git не едет». Иначе любой честный прогон
    проверок на чужой машине краснел бы из-за того, что веса не коммитятся.
    """
    try:
        proc = subprocess.run(
            ["git", "check-ignore", "-q", str(path)],
            cwd=REPO,
            capture_output=True,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return proc.returncode == 0


def check(paths: list[Path]) -> tuple[int, list[str]]:
    checked, broken = 0, []
    local_only = 0
    for md in paths:
        text = md.read_text(encoding="utf-8", errors="ignore")
        for lineno, target in links_in(text):
            dest = resolve(md, target)
            if dest is None:
                continue
            checked += 1
            if not dest.exists():
                if _git_ignored(dest):
                    local_only += 1
                    continue
                broken.append(f"{display_path(md)}:{lineno}: нет цели {target!r}")
    if local_only:
        print(f"локальных артефактов вне git (ссылки не считаются битыми): {local_only}")
    return checked, broken


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("paths", nargs="*", help="файлы или каталоги (по умолчанию — публичные документы)")
    ap.add_argument("--all", action="store_true", help="обойти весь репозиторий")
    args = ap.parse_args(argv)

    if args.paths:
        targets = [Path(p) if Path(p).is_absolute() else REPO / p for p in args.paths]
    elif args.all:
        targets = [REPO]
    else:
        targets = [REPO / p for p in DEFAULT_TARGETS if (REPO / p).is_file()]

    paths: list[Path] = []
    for target in targets:
        if not target.exists():
            print(f"нет файла/каталога: {target}")
            return 2
        paths.extend(iter_markdown(target))

    checked, broken = check(paths)
    print(f"файлов: {len(paths)}, относительных ссылок: {checked}, битых: {len(broken)}")
    for item in broken:
        print(f"БИТАЯ {item}")
    return 0 if not broken else 1


if __name__ == "__main__":
    sys.exit(main())
