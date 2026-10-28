"""check_commit_claims.py — сообщение коммита не должно утверждать того, чего нет в диффе.

Зачем (B-088, 28.10). Коммит `f1d870c` утверждал «пре-регистрация записана», а файла в диффе не было
(неверный путь) — сообщение проверялось глазами, а не гейтом. Здесь проверяются два слова, за которыми
стоит формальный артефакт:

  * «пре-регистрация» / «пререгистрация» / «prereg» → в диффе обязан быть файл `reports/*.md`;
  * «агрегат» → в диффе обязан быть `*.json` в `morphogenesis/experiments/E09_pond/`.

Проверяется HEAD (один коммит) или диапазон `--range A..B`. Режим `--warn` печатает, но не падает.

Использование:
    python scripts/check_commit_claims.py            # HEAD
    python scripts/check_commit_claims.py --range origin/main..HEAD
    python scripts/check_commit_claims.py --warn
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

RULES = [
    {
        "name": "пре-регистрация",
        "subject": re.compile(r"пре-?регистрац|prereg", re.IGNORECASE),
        "path": re.compile(r"^reports/.+-plan\.md$"),
        "hint": "в диффе нужен файл reports/*-plan.md (конвенция имени пре-регистрации)",
        "escape": "[no-prereg]",
    },
    {
        "name": "агрегат",
        "subject": re.compile(r"агрегат", re.IGNORECASE),
        "path": re.compile(r"^morphogenesis/experiments/E09_pond/.+\.json$"),
        "hint": "в диффе нужен *.json агрегата в morphogenesis/experiments/E09_pond/",
        "escape": "[no-agg]",
    },
]


def git(*args: str) -> str:
    # ВАЖНО: encoding="utf-8" — иначе на Windows кириллица в subject декодируется как cp1251
    # и регулярное выражение не находит «пре-регистрация» (проверено на f1d870c).
    out = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True,
                         encoding="utf-8", errors="replace")
    return out.stdout.strip()


def commits_in(rng: str | None) -> list[str]:
    if rng:
        raw = git("rev-list", rng)
    else:
        raw = git("rev-list", "-1", "HEAD")
    return [c for c in raw.splitlines() if c]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--range", dest="rng", default=None)
    ap.add_argument("--warn", action="store_true")
    args = ap.parse_args(argv)

    problems: list[str] = []
    checked = 0
    for sha in commits_in(args.rng):
        subject = git("log", "-1", "--format=%s", sha)
        body = git("log", "-1", "--format=%B", sha)
        if not subject:
            continue
        # merge-коммиты не проверяем: их дифф — объединение веток
        parents = git("rev-list", "--parents", "-n", "1", sha).split()
        if len(parents) > 2:
            continue
        files = [f for f in git("show", "--pretty=format:", "--name-only", sha).splitlines() if f]
        checked += 1
        for rule in RULES:
            if not rule["subject"].search(subject):
                continue
            # ссылка на понятие без утверждения «записано» не требует файла: явный токен-исключение
            if rule.get("escape") and rule["escape"] in body:
                continue
            if not any(rule["path"].match(f) for f in files):
                problems.append(f"{sha[:7]}: в сообщении «{rule['name']}», но {rule['hint']} — нет")

    if problems:
        head = "ПРЕДУПРЕЖДЕНИЕ" if args.warn else "ОШИБКА"
        print(f"[commit-claims] {head}: {len(problems)} расхождений (проверено коммитов: {checked})")
        for p in problems:
            print("   ", p)
        return 0 if args.warn else 1
    print(f"[commit-claims] OK — сообщения соответствуют диффам (коммитов: {checked})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
