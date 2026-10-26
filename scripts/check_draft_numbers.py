#!/usr/bin/env python
"""check_draft_numbers.py — числа в тексте статьи обязаны совпадать с агрегатами.

Зачем: 26.10 в arXiv-черновике дожили до абстракта числа из **старой** серии
(«0.862 против 0.841, 1 сид из 3»), хотя данные уже были пересчитаны на 10 сидах.
Поймал это рецензент глазами. Текст — такой же артефакт, как агрегат: если число
в нём нельзя пересчитать из сырья, оно не должно там стоять.

Скрипт делает три вещи:
  1. достаёт из текста пары «ключевая фраза → ожидаемое значение» и сверяет их
     с агрегатами (источник истины — JSON в morphogenesis/experiments/E09_pond);
  2. ищет числа, которых нет ни в одном агрегате и ни в одном инварианте;
  3. ищет запрещённые формулировки («disappears», «proved», «always») рядом с
     числами, у которых нет вердикта.

Запуск:
    python scripts/check_draft_numbers.py ../_hourly/grants/arxiv-draft-EN.md
    python scripts/check_draft_numbers.py <файл> --strict
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POND = ROOT / "morphogenesis" / "experiments"  # весь каталог: R1 и другие миры тоже
E09 = POND / "E09_pond"
# 26.10: агрегаты бывают и в других каталогах экспериментов (R1 — мир без тела),
# поэтому сканируем весь morphogenesis/experiments, а не только линию пруда.
EXPERIMENTS = ROOT / "morphogenesis" / "experiments"

# что именно обязано совпадать: (человеческое имя, значение, поля-кандидаты в агрегатах)
CHECKS = [
    ("I_obs медиана (клеточное почкование)", 0.5614, ["I_obs_median"]),
    ("I_null (95 %) медиана", 0.0621, ["I_null_95_median"]),
    ("медиана отношений (база)", 12.16, ["I_ratio_median"]),
    ("репликация uniform: отношение медиан", 14.23, ["I_ratio_median"]),
    ("репликация patches: отношение медиан", 9.47, ["I_ratio_median"]),
    ("цена one-bud: медиана rho_partial", -0.478, ["rho_partial_energy_median"]),
    ("цена d2: медиана rho_partial", -0.219, ["rho_partial_energy_median"]),
    ("линий при one-bud (медиана)", 7.5, ["lineages_median"]),
    ("линий при d2 на сидах 1-10", 6.5, ["lineages_median"]),
]

# формулировки, которые нельзя ставить рядом с «пограничными» числами
FORBIDDEN = [
    (r"remainder\s+disappears|the\s+remainder\s+vanished", "остаток объявлен исчезнувшим"),
    (r"\bproves?\b|\bproved\b", "утверждение объявлено доказанным"),
    (r"always\s+(exceeds|above|negative)", "утверждение объявлено всегдашним"),
]


def load_numbers() -> dict[str, set[float]]:
    """Все числа из агрегатов: имя поля → множество значений."""
    out: dict[str, set[float]] = {}
    for path in EXPERIMENTS.rglob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        rows = data.get("rows")
        if isinstance(rows, list):
            for row in rows:
                if not isinstance(row, dict):
                    continue
                for key, value in row.items():
                    if isinstance(value, (int, float)) and not isinstance(value, bool):
                        out.setdefault(key, set()).add(round(float(value), 4))
        def walk(obj, depth=0):
            if depth > 4:
                return
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if isinstance(value, (int, float)) and not isinstance(value, bool):
                        out.setdefault(key, set()).add(round(float(value), 4))
                    else:
                        walk(value, depth + 1)
            elif isinstance(obj, list):
                for item in obj:
                    walk(item, depth + 1)

        walk(data)
        for block in ("by_arm", "criteria", "invariants"):
            for item in data.get(block) or []:
                if isinstance(item, dict):
                    for key, value in item.items():
                        if isinstance(value, (int, float)) and not isinstance(value, bool):
                            out.setdefault(key, set()).add(round(float(value), 4))
    return out


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="числа статьи против агрегатов")
    ap.add_argument("draft", help="путь к тексту статьи (markdown)")
    ap.add_argument("--strict", action="store_true", help="код 1 при любом расхождении")
    args = ap.parse_args(argv)

    draft = Path(args.draft)
    if not draft.is_absolute():
        draft = Path.cwd() / draft
    if not draft.exists():
        print(f"[draft-numbers] нет файла: {draft}")
        return 2
    text = draft.read_text(encoding="utf-8")
    numbers = load_numbers()

    problems: list[str] = []

    # 1. числа, которые обязаны быть в тексте и должны совпадать с агрегатами
    for label, expected, fields in CHECKS:
        present = any(str(abs(expected)) in text or str(expected) in text for _ in [0])
        found = any(f in numbers for f in fields)
        if not present:
            problems.append(f"нет в тексте: {label} = {expected}")
            continue
        if not found:
            problems.append(f"нет в агрегатах (поле {fields}): {label}")
            continue
        ok = any(abs(v - expected) < 1e-3 for f in fields if f in numbers for v in numbers[f])
        if not ok:
            observed = sorted({v for f in fields if f in numbers for v in numbers[f]})[:6]
            problems.append(f"расхождение: {label} — в тексте {expected}, в агрегатах {observed}")

    # 1б. знаменатели: если у плеча в агрегате invalid_by_data или valid_n == 0,
    # «N/10» в тексте без явного valid_n читается как результат, а это неверно (AGENTS §3c).
    invalid_arms: list[str] = []
    for path in EXPERIMENTS.rglob("*_matrix.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not (data.get("criteria") or {}).get("invalid_by_data"):
            continue
        for arm in data.get("by_arm") or []:
            name = str(arm.get("arm"))
            if name in {"cell", "pair", "colony"} and (arm.get("valid_n") or 0) == 0:
                invalid_arms.append(f"{path.name}:{name}")
    if invalid_arms:
        ratio_mentions = len(re.findall(r"\b\d{1,2}\s*/\s*10\b", text))
        has_valid = "valid_n" in text or "valid runs" in text
        if not has_valid:
            problems.append(
                f"в агрегатах есть плечи без валидных прогонов ({len(invalid_arms)} шт.), "
                f"в тексте {ratio_mentions} долей вида N/10, но нет ни одного 'valid_n'/'valid runs' — "
                f"знаменатель не указан")
        print(f"[draft-numbers] знаменатели: плеч с valid_n = 0 — {len(set(invalid_arms))}")

    # 2. запрещённые формулировки
    NEGATIONS = ("not ", "no ", "cannot", "neither", "never", "does not", "do not")
    for pattern, why in FORBIDDEN:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            # «we write agrees with, not proved» и «we do not claim ... always exceeds» —
            # это как раз правильные формулировки; проверяем предложение на отрицание.
            sentence_start = max(text.rfind(". ", 0, match.start()), text.rfind("\n", 0, match.start()))
            sentence = text[sentence_start + 1: match.end() + 120].lower()
            if any(neg in sentence for neg in NEGATIONS):
                continue
            line = text[: match.start()].count("\n") + 1
            problems.append(f"строка {line}: {why} («{match.group(0)}»)")

    # 3. числа в тексте, которых нет ни в одном агрегате (эвристика, только предупреждение)
    leftovers = []
    for match in re.finditer(r"(?<![A-Za-z0-9])-?\d\.\d{2,4}(?![\d])", text):
        value = round(float(match.group(0)), 4)
        near = text[max(0, match.start() - 24): match.end() + 24]
        if "doi" in near.lower() or "10." in near or "http" in near.lower() or "annurev" in near.lower():
            continue  # номер DOI/URL — не метрика
        if "–" in near or " p = " in near or "p =" in near or "GB" in near:
            continue  # диапазон, p-значение или размер файла — не метрика
        if any(abs(value - v) < 5e-4 for values in numbers.values() for v in values):
            continue
        leftovers.append(f"строк {text[: match.start()].count(chr(10)) + 1}: {match.group(0)}")

    print(f"[draft-numbers] файл: {draft.name}, полей в агрегатах: {len(numbers)}")
    if problems:
        for p in problems:
            print(f"[draft-numbers] ОШИБКА: {p}")
    if leftovers:
        print(f"[draft-numbers] предупреждение: {len(leftovers)} чисел не найдено в агрегатах "
              f"(первые {min(5, len(leftovers))}):")
        for item in leftovers[:5]:
            print(f"   {item}")
    if not problems:
        print("[draft-numbers] OK — обязательные числа совпадают с агрегатами, "
              "запрещённых формулировок нет")
        return 0
    return 1 if args.strict else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
