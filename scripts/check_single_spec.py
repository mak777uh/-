"""check_single_spec.py — не должно быть двух документов, объявляющих одну версию требований.

Откуда (30.10, входящий аудит `lexspec`, находка M-2): «спека — единственный носитель требований, и если их две,
читатель не может узнать действующую». У них это было буквально: два файла по 211 и 362 КБ, оба объявляли
`v5.5-EXP FINAL Rev.7`, и ни один не был объявлен текущим.

У нас дублей сейчас нет, но проверки не было. Гейт ловит два случая:

1. **Две спецификации в одном каталоге** с одинаковым объявленным номером версии (регулярка по `Version`,
   `Версия`, `v\\d+\\.\\d+`, `Rev\\.?\\d+`) — ошибка.
2. **Файл с пометкой «копия»/«(1)»/«(2)» в имени** рядом с одноимённым — предупреждение.

Использование:
    python scripts/check_single_spec.py [--ci]
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_DIRS = (ROOT, ROOT / "docs", ROOT / "manuscript", ROOT / "reports")
VERSION_RE = re.compile(r"(?:версия|version)\s*[:：]?\s*v?(\d+\.\d+(?:[\w.\-]*)?)", re.IGNORECASE)
REV_RE = re.compile(r"(?:rev\.?|ревизия)\s*[:：]?\s*(\d+)", re.IGNORECASE)
DUP_NAME_RE = re.compile(r"\(\d+\)|копия|copy", re.IGNORECASE)


def declared_versions(path: Path) -> set[str]:
    try:
        head = "\n".join(path.read_text(encoding="utf-8", errors="replace").splitlines()[:40])
    except OSError:
        return set()
    out = set()
    for m in VERSION_RE.finditer(head):
        out.add(m.group(1).lower())
    for m in REV_RE.finditer(head):
        out.add("rev" + m.group(1))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="одна действующая спецификация")
    ap.add_argument("--ci", action="store_true")
    args = ap.parse_args(argv)

    errors: list[str] = []
    warns: list[str] = []

    for d in CANDIDATE_DIRS:
        if not d.exists():
            continue
        seen: dict[tuple[str, str], list[str]] = {}
        for f in sorted(d.glob("*.md")):
            for v in declared_versions(f):
                seen.setdefault((v, str(d)), []).append(f.name)
        for (v, dd), names in seen.items():
            if len(names) > 1:
                errors.append(f"{dd}: версия {v} объявлена в {len(names)} файлах: {', '.join(names)}")
        for f in sorted(d.glob("*.md")):
            if DUP_NAME_RE.search(f.name):
                base = DUP_NAME_RE.sub("", f.stem).strip(" -_")
                twins = [g.name for g in d.glob("*.md") if g.stem.strip(" -_") == base and g.name != f.name]
                if twins:
                    warns.append(f"{f.name}: похоже на копию рядом с {twins[0]}")

    print(f"[single-spec] каталогов проверено: {sum(1 for d in CANDIDATE_DIRS if d.exists())}")
    for w in warns:
        print("  предупреждение:", w)
    if errors:
        print(f"[single-spec] ОШИБОК: {len(errors)}")
        for e in errors:
            print("  ", e)
        print("[single-spec] объявите действующую версию в одном файле, остальные — ссылкой на неё")
        if args.ci:
            return 1
    else:
        print("[single-spec] каждая версия требований объявлена один раз")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
