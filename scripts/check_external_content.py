"""check_external_content.py — секреты и попытки инъекции во внешнем контенте, попавшем в репозиторий.

Откуда идея (28.10, nearai/ironclaw). Их ассистент строит защиту в глубину: изоляция секретов, поиск
утечек, детекция prompt injection с уровнями Block/Warn/Review/Sanitize. У нас нет WASM-песочницы, но риск
тот же: мы постоянно кладём в репозиторий **внешний текст** (страницы, README чужих проектов, посты,
замечания доски), и он попадает в контекст агентов.

Проверяется:
1. Секреты (ошибка): `sk-…`, `ghp_…`, `AKIA…`, приватные ключи, `Bearer …`, секрет в присваивании.
2. Инъекции (ошибка, если не цитата): «ignore previous instructions», «you are now», «system prompt»,
   «игнорируй инструкции», «агент обязан» — разрешено внутри цитаты (`>`) или с пометкой [цитата].
3. Пути с именами пользователей (предупреждение).

Область: reports/, library/, articles/, docs/, README.md, lab/lit-board.json.
Использование:
    python scripts/check_external_content.py [--strict]
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SECRET_PATTERNS = [
    ("openai-подобный ключ", re.compile(r"\bsk-[A-Za-z0-9]{16,}")),
    ("github-токен", re.compile(r"\bghp_[A-Za-z0-9]{20,}")),
    ("aws-ключ", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("приватный ключ", re.compile(r"-----BEGIN (RSA |OPENSSH |EC )?PRIVATE KEY-----")),
    ("bearer-токен", re.compile(r"\bBearer\s+[A-Za-z0-9._\-]{20,}")),
    ("секрет в присваивании", re.compile(r"(?i)\b(api[_-]?key|secret|token|password)\b\s*[:=]\s*['\"][A-Za-z0-9._\-]{16,}['\"]")),
]

INJECTION_PATTERNS = [
    ("англ. «игнорируй инструкции»", re.compile(r"(?i)ignore (all )?(previous|prior|above) instructions")),
    ("англ. «ты теперь»", re.compile(r"(?i)\byou are now (a|an|the)\b")),
    ("англ. «system prompt»", re.compile(r"(?i)\bsystem prompt\b")),
    ("рус. «игнорируй инструкции»", re.compile(r"(?i)игнорируй(те)?\s+(все\s+)?(предыдущие\s+)?инструкц")),
    ("рус. приказ агенту", re.compile(r"(?i)\bагент\s+(обязан|должен|немедленно)\b")),
    ("рус. «ты теперь»", re.compile(r"(?i)\bты\s+теперь\s+\w+")),
]

USER_PATH = re.compile(r"[A-Za-z]:\\\\?Users\\\\?([A-Za-z0-9_.\-]+)")

# Где искать секреты — везде, включая наши спецификации.
SECRET_TARGETS = [
    *sorted((ROOT / "reports").glob("*.md")),
    *sorted((ROOT / "library").glob("*.md")),
    *sorted((ROOT / "articles").glob("*.md")),
    *sorted((ROOT / "docs").glob("*.md")),
    ROOT / "README.md",
    ROOT / "lab" / "lit-board.json",
]

# Где искать инъекции — только там, куда попадает ВНЕШНИЙ текст. Наши собственные спецификации
# (docs/, README) содержат правила вида «агент обязан» совершенно законно, и проверять их этим
# шаблоном значит ловить себя за руку (проверено: первая версия падала ровно на docs/cycle.md:64).
INJECTION_TARGETS = [
    *sorted((ROOT / "reports").glob("*.md")),
    *sorted((ROOT / "library").glob("*.md")),
    *sorted((ROOT / "articles").glob("*.md")),
    ROOT / "lab" / "lit-board.json",
]


QUOTE_CHARS = "«»\"'`"


def match_is_quoted(line: str, start: int, end: int) -> bool:
    """Попадание считается данными, если оно целиком лежит внутри «…», "…" или `…`.

    Зачем так: гейт должен уметь описывать шаблоны инъекций в собственной документации, не краснея на себе
    (это второй такой случай за вечер — первый был с «агент обязан» в контракте).
    """
    pairs = [("«", "»"), ('"', '"'), ("`", "`")]
    for op, cl in pairs:
        pos = line.find(op)
        while pos != -1:
            close = line.find(cl, pos + 1)
            if close != -1 and pos < start and end <= close:
                return True
            pos = line.find(op, pos + 1)
    # кавычки прямо по краям попадания
    if start > 0 and end < len(line) and line[start - 1] in QUOTE_CHARS and line[end] in QUOTE_CHARS:
        return True
    return False


def is_quote_context(line: str, i: int, lines: list[str]) -> bool:
    if line.lstrip().startswith(">"):
        return True
    window = " ".join(lines[max(0, i - 3): i + 1]).lower()
    return "[цитата]" in window or "[внешний текст]" in window or "цитата:" in window


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="секреты и инъекции во внешнем контенте")
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args(argv)

    errors: list[str] = []
    warnings: list[str] = []
    scanned = 0
    injection_set = {p.resolve() for p in INJECTION_TARGETS if p.exists()}
    for path in sorted(set(SECRET_TARGETS) | set(INJECTION_TARGETS)):
        if not path.exists() or path.is_dir():
            continue
        scanned += 1
        lines = path.read_text(encoding="utf-8", errors="replace").split("\n")
        rel = path.relative_to(ROOT)
        check_injections = path.resolve() in injection_set
        for i, line in enumerate(lines, start=1):
            for name, rx in SECRET_PATTERNS:
                if rx.search(line):
                    errors.append(f"{rel}:{i}: возможный секрет ({name})")
            for name, rx in (INJECTION_PATTERNS if check_injections else []):
                m = rx.search(line)
                if m and not is_quote_context(line, i - 1, lines) and not match_is_quoted(line, m.start(), m.end()):
                    errors.append(f"{rel}:{i}: похоже на инъекцию ({name}) — пометьте как цитату или перепишите")
            for m in USER_PATH.finditer(line):
                if m.group(1).lower() not in {"admin", "public"}:
                    warnings.append(f"{rel}:{i}: путь с именем пользователя «{m.group(1)}»")

    if warnings and args.strict:
        errors += warnings
        warnings = []
    for w in warnings[:8]:
        print("[external]", w)
    if errors:
        print(f"[external] ОШИБКА: {len(errors)} проблем (файлов {scanned})")
        for e in errors[:15]:
            print("   ", e)
        return 1
    print(f"[external] OK — файлов {scanned}, секретов и немаркированных инъекций нет")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
