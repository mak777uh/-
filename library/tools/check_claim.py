#!/usr/bin/env python
"""Проверка находки ДО публикации: чек-лист, который ловит 45 % моих ошибок.

Мои ошибки за двое суток (реестр в self-audit): 5 из 11 — «прочитал артефакт неверно»
(не то поле, не тот файл, не тот масштаб). Этот инструмент проверяет именно это:

  --artifact PATH   файл существует и это JSON нужной серии
  --field A.B       поле реально есть (вложенность через точку)
  --expect VALUE    значение воспроизводится (число — с допуском, строка — точно)
  --series-kind K   kind агрегата совпадает (ловушка «взял uniform вместо patches»)
  --in PATH...      поле задокументировано в файле(ах) (подстрока)

Коды: 0 — проверка прошла; 1 — есть проблема; 2 — ошибка аргументов/файла.

Пример (ловушка B-082):
  python library/tools/check_claim.py --artifact morphogenesis/.../placement_matrix.json \
      --series-kind placement_runs --field by_arm.0.survived_k --expect 7 --in docs/world-design.md
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def get_field(data, dotted: str):
    """Достать поле: 'a.b.0.c' — словари и списки."""
    cur = data
    for part in dotted.split("."):
        if isinstance(cur, list):
            if not part.isdigit() or int(part) >= len(cur):
                return None, False
            cur = cur[int(part)]
        elif isinstance(cur, dict):
            if part not in cur:
                return None, False
            cur = cur[part]
        else:
            return None, False
    return cur, True


def close(a, b) -> bool:
    try:
        fa, fb = float(a), float(b)
    except (TypeError, ValueError):
        return str(a) == str(b)
    if fb == 0:
        return abs(fa) <= 1e-9
    return abs(fa - fb) / abs(fb) <= 1e-6


def homogeneity_note(artifact: Path) -> str | None:
    """Провенанс серии: помечена ли она как снятая разным кодом (lab/homogeneity.json)."""
    reg = REPO / "lab" / "homogeneity.json"
    if not reg.exists():
        return None
    try:
        data = json.loads(reg.read_text(encoding="utf-8"))
    except Exception:
        return None
    rel = str(artifact.parent.relative_to(REPO)).replace("\\", "/")
    for status, items in data.items():
        if not isinstance(items, dict) or status in ("note",):
            continue
        for path, reason in items.items():
            path = str(path).replace("\\", "/")
            if rel == path or rel.endswith("/" + path) or path in rel:
                if status in ("archived_invalid", "invalid"):
                    return f"серия {path} помечена {status}: {str(reason)[:140]}"
    return None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Проверка находки до публикации")
    ap.add_argument("--artifact", required=True)
    ap.add_argument("--field", default=None)
    ap.add_argument("--expect", default=None)
    ap.add_argument("--series-kind", default=None)
    ap.add_argument("--in", dest="docs", nargs="*", default=[])
    args = ap.parse_args(argv)

    path = REPO / args.artifact
    problems: list[str] = []
    if not path.exists():
        print(f"ПРОБЛЕМА: нет файла {args.artifact}")
        return 1
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"ПРОБЛЕМА: файл не читается как JSON ({exc})")
        return 2

    if args.series_kind:
        kind = data.get("kind") if isinstance(data, dict) else None
        if kind != args.series_kind:
            problems.append(f"kind = {kind!r}, ожидался {args.series_kind!r} — вероятно, не та серия")

    if args.field:
        value, ok = get_field(data, args.field)
        if not ok:
            problems.append(f"поля {args.field!r} нет в артефакте")
        elif args.expect is not None and not close(value, args.expect):
            problems.append(f"поле {args.field} = {value!r}, ожидалось {args.expect!r}")

    for doc in args.docs:
        p = REPO / doc
        if not p.exists():
            problems.append(f"документ {doc} отсутствует")
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        if args.field:
            leaf = args.field.split(".")[-1]
            if leaf not in text:
                problems.append(f"поле {leaf!r} не упомянуто в {doc} — определение не задокументировано")
        if args.artifact and Path(args.artifact).name not in text:
            problems.append(f"артефакт {Path(args.artifact).name} не упомянут в {doc}")

    note = homogeneity_note(path)
    if note:
        problems.append(note + " — числа этой серии не публикуются")

    if problems:
        for pr in problems:
            print("ПРОБЛЕМА:", pr)
        return 1
    print("проверка прошла: файл, поле, значение и документация согласованы")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
