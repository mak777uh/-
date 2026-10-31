"""make_scripts_index.py — автогенерируемый индекс всех скриптов.

Зачем. 31.10 из 160 скриптов только 59 были описаны в `docs/scripts.md`, а 20 не упомянуты нигде: внешний читатель
не мог найти команду за числом. Руками такой индекс поддерживать бессмысленно — он отстанет на третий день.
Все скрипты имеют docstring, поэтому индекс собирается из них и **никогда не отстаёт**: гейт
`check_script_index.py` падает, если файл отличается от результата генерации.

`docs/scripts.md` остаётся кураторской страницей (что важно и почему); этот файл — полный перечень.

Запуск:
    python scripts/make_scripts_index.py --write
    python scripts/make_scripts_index.py            # показать, не писать
"""
from __future__ import annotations

import argparse
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
OUT = ROOT / "docs" / "scripts-index.md"

# порядок групп важен: первое совпадение выигрывает
GROUPS = [
    ("Гейты и проверки", lambda n: n.startswith(("check_", "verify_", "claims_lint", "validate_", "lean_check"))),
    ("Лабораторный контур", lambda n: n.startswith(("lab", "cyc", "queue", "triage", "pool", "notices", "wake",
                                                     "insight", "preflight", "retention", "ci_", "export_", "zenodo"))),
    ("Библиотека и литература", lambda n: n.startswith(("lib", "lit_", "library_"))),
    ("Линия поля", lambda n: n.startswith(("field_", "te_", "ghost_", "adequacy_", "individuality", "individuation"))),
    ("Пруд и W1", lambda n: n.startswith(("pond_", "w1", "w2", "colony", "kill_keep", "generation", "invader",
                                          "mutation", "placement", "phase_", "r1_", "selection_", "trait_",
                                          "rhythmicity", "morphometry", "mspd", "idh_", "fisher_", "simple_world",
                                          "map_metrics", "metrics_registry", "signature", "census", "run_seed"))),
    ("Сборка отчётов и таблиц", lambda n: n.startswith(("make_", "aggregate_", "build_", "report"))),
]


def first_line(path: Path) -> str:
    try:
        doc = ast.get_docstring(ast.parse(path.read_text(encoding="utf-8", errors="replace"))) or ""
    except SyntaxError:
        return "(синтаксическая ошибка)"
    text = doc.strip().split("\n")[0].strip()
    return text or "(без описания)"


def group_of(name: str) -> str:
    for title, pred in GROUPS:
        if pred(name):
            return title
    return "Прочее"


def build() -> str:
    rows: dict[str, list[tuple[str, str]]] = {}
    for p in sorted(SCRIPTS.glob("*.py")):
        rows.setdefault(group_of(p.stem), []).append((p.stem, first_line(p)))
    order = [t for t, _ in GROUPS] + ["Прочее"]
    lines = [
        "# Index of every script",
        "",
        "**Generated file — do not edit by hand.** Regenerate with "
        "`python scripts/make_scripts_index.py --write`; the gate `check_script_index.py` fails when this file is stale.",
        "",
        "The curated page — what matters and why — is [`scripts.md`](scripts.md). This file is the complete list, so that "
        "every command behind a number in the record can be found.",
        "",
        f"Scripts: **{sum(len(v) for v in rows.values())}**.",
        "",
    ]
    for title in order:
        items = rows.get(title)
        if not items:
            continue
        lines.append(f"## {title} ({len(items)})")
        lines.append("")
        lines.append("| script | what it does (first line of its docstring) |")
        lines.append("| --- | --- |")
        for name, desc in items:
            desc = desc.replace("|", "\\|")
            lines.append(f"| `{name}.py` | {desc} |")
        lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="индекс всех скриптов")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    text = build()
    if args.write:
        OUT.write_text(text, encoding="utf-8", newline="\n")
        print(f"[scripts-index] записано: {OUT.relative_to(ROOT)} | скриптов: {text.count('| `')}")
    else:
        print(text[:1500])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
