#!/usr/bin/env python
"""Валидатор машиночитаемых артефактов прогонов (схемы v1.1.0).

Зачем: снаружи (депозит, заявки, рецензент) спрашивают не отчёты, а артефакты.
Контракт такой:

- `lab/runs/<run_id>.json` — манифест раннера (слой A). Не переписывается никогда.
- `lab/science/<run_id>.json` — научная карточка (слой B): класс, метрики,
  пре-регистрация. Новый файл, поэтому история не страдает.
- `lab/runs.index.json` — индекс (слой C): собирается скриптом из A+B.

Валидатор проверяет B и C по схемам из `lab/schema/` и падает на битом JSON.
JSON-Schema реализован минимальным подмножеством (type/required/properties/
additionalProperties/enum/pattern/items/anyOf/minimum/minLength) — этого хватает
нашим схемам и не тянет внешнюю зависимость в CI.

Запуск (из корня репозитория):

    python scripts/validate_runs.py            # проверить всё, что есть
    python scripts/validate_runs.py --strict    # требовать непустой набор карточек

Код возврата: 0 — всё валидно, 1 — есть ошибки.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCHEMA_DIR = REPO / "lab" / "schema"
SCIENCE_DIR = REPO / "lab" / "science"
RUNS_DIR = REPO / "lab" / "runs"
INDEX = REPO / "lab" / "runs.index.json"


def load_json(path: Path) -> tuple[object, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except OSError as exc:
        return None, f"не читается: {exc}"
    except ValueError as exc:
        return None, f"битый JSON: {exc}"


def _type_ok(value: object, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    return True


def validate(value: object, schema: dict, path: str = "$") -> list[str]:
    """Мини-валидация по JSON Schema (подмножество, нужное нашим схемам)."""
    errors: list[str] = []

    expected = schema.get("type")
    if expected is not None:
        types = expected if isinstance(expected, list) else [expected]
        if not any(_type_ok(value, t) for t in types):
            return [f"{path}: ожидался тип {types}, получено {type(value).__name__}"]

    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: {value!r} не входит в enum {schema['enum']}")

    if isinstance(value, str):
        pattern = schema.get("pattern")
        if pattern and not re.search(pattern, value):
            errors.append(f"{path}: {value!r} не соответствует шаблону {pattern}")
        min_len = schema.get("minLength")
        if min_len is not None and len(value) < min_len:
            errors.append(f"{path}: короче {min_len} символов")

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        minimum = schema.get("minimum")
        if minimum is not None and value < minimum:
            errors.append(f"{path}: {value} меньше минимума {minimum}")

    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{path}: отсутствует обязательное поле {key!r}")
        props = schema.get("properties", {})
        additional = schema.get("additionalProperties", True)
        for key, item in value.items():
            if key in props:
                errors.extend(validate(item, props[key], f"{path}.{key}"))
            elif additional is False:
                errors.append(f"{path}: лишнее поле {key!r}")
            elif isinstance(additional, dict):
                errors.extend(validate(item, additional, f"{path}.{key}"))

    if isinstance(value, list) and isinstance(schema.get("items"), dict):
        for i, item in enumerate(value):
            errors.extend(validate(item, schema["items"], f"{path}[{i}]"))

    return errors


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--strict", action="store_true", help="ошибка, если карточек нет вовсе")
    args = ap.parse_args(argv)

    problems: list[str] = []
    checked_cards = 0
    checked_index = 0

    card_schema, err = load_json(SCHEMA_DIR / "run.schema.json")
    if err:
        print(f"[schema] run.schema.json: {err}")
        return 1
    index_schema, err = load_json(SCHEMA_DIR / "runs_index.schema.json")
    if err:
        print(f"[schema] runs_index.schema.json: {err}")
        return 1

    cards = sorted(SCIENCE_DIR.glob("*.json")) if SCIENCE_DIR.is_dir() else []
    if args.strict and not cards:
        problems.append("каталог lab/science/ пуст — научных карточек нет")

    manifests = {p.stem for p in RUNS_DIR.glob("*.json")} if RUNS_DIR.is_dir() else set()
    for path in cards:
        data, err = load_json(path)
        if err:
            problems.append(f"lab/science/{path.name}: {err}")
            continue
        checked_cards += 1
        for msg in validate(data, card_schema, f"lab/science/{path.name}"):
            problems.append(msg)
        run_id = data.get("run_id")
        if run_id and run_id != path.stem:
            problems.append(
                f"lab/science/{path.name}: run_id {run_id!r} не совпадает с именем файла"
            )
        if run_id and manifests and run_id not in manifests:
            problems.append(
                f"lab/science/{path.name}: нет манифеста lab/runs/{run_id}.json"
            )

    if INDEX.exists():
        data, err = load_json(INDEX)
        if err:
            problems.append(f"lab/runs.index.json: {err}")
        else:
            checked_index = len(data.get("records", [])) if isinstance(data, dict) else 0
            for msg in validate(data, index_schema, "lab/runs.index.json"):
                problems.append(msg)

    print(
        f"карточек: {checked_cards}, записей в индексе: {checked_index}, "
        f"манифестов: {len(manifests)}, ошибок: {len(problems)}"
    )
    for msg in problems[:40]:
        print(f"  ОШИБКА {msg}")
    if len(problems) > 40:
        print(f"  … ещё {len(problems) - 40}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
