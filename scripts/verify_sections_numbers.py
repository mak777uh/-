#!/usr/bin/env python
"""verify_sections_numbers.py — числа в рукописи обязаны воспроизводиться из агрегатов.

Зачем: 25.10 три пересчёта одного результата (W2-bud) дали три числа, потому что
определения не были задокументированы, а агрегатор считал критерий по подмножеству
(см. `lab/notices.md`, прецедент 2026-10-25). Этот скрипт ловит такой класс расхождений
машинно: для каждой пары «раздел рукописи → агрегат + ключи» он пересчитывает значение из
агрегата и падает, если отформатированная строка не встречается в тексте раздела.

Как задаётся проверка (таблица `CHECKS` ниже):

    {
      "section": "4i",                     # подстрока заголовка раздела в paper.md
      "aggregate": "morphogenesis/...json", # путь от корня репозитория
      "values": {"k": "<pointer>", "n": "<pointer>"},
      "template": "{k}/{n}",               # что именно должно стоять в тексте
      "note": "…",                         # для человека, если упадёт
    }

Указатель (`pointer`) — путь по JSON: `a.b`, `a[0]`, `a{arm=cell}` (элемент списка по полю).
Форматирование: числа приводятся к строке; для float пробуются варианты `str(v)`,
`f"{v:.1f}"`, `f"{v:.2f}"` — в тексте должна найтись хотя бы одна форма.

Запуск (из корня):

    python scripts/verify_sections_numbers.py           # проверка
    python scripts/verify_sections_numbers.py --list    # показать таблицу проверок
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "manuscript" / "paper.md"
POND = "morphogenesis/experiments/E09_pond"

CHECKS: list[dict] = [
    # --- §4i: W2-bud (клеточное почкование) --------------------------------------------
    {
        "section": "4i",
        "aggregate": f"{POND}/w2bud_matrix.json",
        "values": {"k": "by_arm{arm=cell}.crow_I_positive_k_all",
                   "n": "by_arm{arm=cell}.runs"},
        "template": "{k}/{n}",
        "note": "I > 0 в W2-bud — по ВСЕМ сидам (знаменатель = runs, не valid_n)",
    },
    {
        "section": "4i",
        "aggregate": f"{POND}/w2bud_matrix.json",
        "values": {"v": "by_arm{arm=cell}.tags_ge2_median"},
        "template": "{v}",
        "note": "медиана меток с >=2 живыми клетками (type_counts, не lineage_fitness)",
    },
    {
        "section": "4i",
        "aggregate": f"{POND}/w2bud_matrix.json",
        "values": {"v": "by_arm{arm=cell}.lineages_median"},
        "template": "{v}",
        "note": "медиана линий с данными (>=5 живых клеток и >=1 спора)",
    },
    {
        "section": "4i",
        "aggregate": f"{POND}/w2bud_matrix.json",
        "values": {"v": "by_arm{arm=colony}.crow_I_median_all"},
        "template": "I = {v}",
        "note": "контроль W1: I = 0 во всех сидах",
    },
    {
        "section": "4i",
        "aggregate": f"{POND}/w2bud2_matrix.json",
        "values": {"v": "by_arm{arm=cell}.I_obs_median"},
        "template": "{v}",
        "note": "I_obs в W2-bud (медиана по 10 сидам) — критерий через нуль-модель",
    },
    {
        "section": "4i",
        "aggregate": f"{POND}/w2bud2_matrix.json",
        "values": {"v": "by_arm{arm=cell}.I_null_95_median"},
        "template": "{v}",
        "note": "I_null(95 %) — нуль-модель случайных потомков при наблюдаемых размерах линий",
    },
    {
        "section": "4i",
        "aggregate": f"{POND}/w2bud2_matrix.json",
        "values": {"v": "by_arm{arm=cell}.I_ratio_median"},
        "template": "{v}",
        "note": "запас I_obs / I_null(95 %)",
    },
    {
        "section": "4i",
        "aggregate": f"{POND}/w2bud3_matrix.json",
        "values": {"v": "by_arm{arm=cell}.rho_trait_cell_steps_median"},
        "template": "{v}",
        "note": "цена признака: rho(tag_trait, lineage_cell_steps) по линиям с данными "
                "(отрицательный = высокий признак даёт меньше клетко-шагов)",
        "pending": "агрегат появится, когда закроется серия W2-bud v3",
    },
    {
        "section": "4i",
        "aggregate": f"{POND}/w2bud4s_matrix.json",
        "values": {"v": "by_arm{arm=cell}.rho_partial_energy_median"},
        "template": "{v}",
        "note": "частная корреляция rho(признак, cell_steps | energy_per_cell_time); "
                "df = n_линий - 3 (при 5-6 линиях df = 2-3)",
    },
    # --- §4h: размещение и слияние (V8) ------------------------------------------------
    {
        "section": "4h",
        "aggregate": f"{POND}/v8_matrix.json",
        "values": {"k": "by_arm{arm=into_resident_majority}.survived_k",
                   "n": "by_arm{arm=into_resident_majority}.valid_n"},
        "template": "{k}/{n}",
        "note": "V8: выживание инвайдера при случайной подсадке",
    },
    {
        "section": "4h",
        "aggregate": f"{POND}/v8_matrix.json",
        "values": {"k": "by_arm{arm=into_gap_majority}.separate_k",
                   "n": "by_arm{arm=into_gap_majority}.valid_n"},
        "template": "{k}/{n}",
        "note": "V8: доля прогонов с отдельной компонентой при подсадке в gap",
    },
    {
        "section": "4h",
        "aggregate": f"{POND}/placement_patches_matrix.json",
        "values": {"k": "by_arm{arm=keep}.survived_k", "n": "by_arm{arm=keep}.runs"},
        "template": "{k}/{n}",
        "note": "patches: выживание при сохранении типа на фоне полной подсадки",
    },
    {
        "section": "4h",
        "aggregate": f"{POND}/placement_matrix.json",
        "values": {"k": "by_arm{arm=keep}.survived_k", "n": "by_arm{arm=keep}.runs"},
        "template": "{k}/{n}",
        "note": "uniform: выживание при сохранении типа на фоне полной подсадки",
    },
    {
        "section": "4h",
        "aggregate": f"{POND}/merge_keep_matrix.json",
        "values": {"k": "by_arm{arm=keep}.survived_k",
                   "n": "by_arm{arm=keep}.valid_n"},
        "template": "{k}/{n}",
        "note": "merge=keep: выживание при запрете переписывания типа",
    },
    {
        "section": "4h",
        "aggregate": f"{POND}/merge_keep_matrix.json",
        "values": {"k": "by_arm{arm=majority}.survived_k",
                   "n": "by_arm{arm=majority}.valid_n"},
        "template": "{k}/{n}",
        "note": "merge=keep: контроль majority",
    },
]

SEGMENT = re.compile(r"\{(\w+)=([^}]+)\}")


def resolve(agg, pointer: str):
    """Пройти по JSON по указателю `a.b`, `a[0]`, `a{arm=cell}`."""
    node = agg
    for part in pointer.split("."):
        m = SEGMENT.search(part)
        if m:
            field, want = m.group(1), m.group(2)
            name = part[: m.start()]
            seq = node[name] if name else node
            node = next((item for item in seq if str(item.get(field)) == want), None)
            if node is None:
                raise KeyError(f"в {name} нет элемента {field}={want}")
        elif "[" in part:
            name, idx = part[:-1].split("[")
            node = node[name][int(idx)]
        else:
            node = node[part]
    return node


def variants(value) -> list[str]:
    """Строковые формы значения, любая из которых считается «число есть в тексте»."""
    if isinstance(value, bool):
        return [str(value).lower(), str(value)]
    if isinstance(value, int):
        return [str(value)]
    if isinstance(value, float):
        # ВАЖНО: никаких "{:.0f}" — «0» встречается в любом тексте и даёт ложный проход
        # (поймано 25.10: гейт «проходил» на 0.4284, потому что в разделе была цифра 0).
        out = [str(value)]
        for fmt in ("{:.1f}", "{:.2f}", "{:.3f}"):
            out.append(fmt.format(value))
        if float(value) == int(value):
            out.append(str(int(value)))      # «I = 0» вместо «I = 0.0»
        return list(dict.fromkeys(out))
    return [str(value)]


def section_text(section: str) -> str | None:
    """Текст раздела рукописи: от заголовка с номером до следующего заголовка того же уровня."""
    if not PAPER.exists():
        return None
    text = PAPER.read_text(encoding="utf-8")
    pattern = re.compile(rf"^(#+\s*{re.escape(section)}[\.\s].*)$", re.MULTILINE)
    m = pattern.search(text)
    if not m:
        return None
    level = len(m.group(1)) - len(m.group(1).lstrip("#"))
    rest = text[m.end():]
    stop = re.search(rf"^#{{1,{level}}}\s", rest, re.MULTILINE)
    return rest[: stop.start()] if stop else rest


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--list", action="store_true", help="показать таблицу проверок")
    args = ap.parse_args(argv)

    if args.list:
        for c in CHECKS:
            print(f"§{c['section']} <- {c['aggregate']} :: {c['template']}  ({c['note']})")
        return 0

    if not PAPER.exists():
        print(f"[sections] нет {PAPER}")
        return 1

    cache: dict[str, dict] = {}
    problems: list[str] = []
    checked = 0
    skipped: list[str] = []
    for check in CHECKS:
        agg_path = ROOT / check["aggregate"]
        if not agg_path.exists():
            # Отложенная проверка: агрегата ещё нет, но он объявлен и появится сам
            # (например, серия идёт прямо сейчас). Так гейт не краснеет на HEAD,
            # а молчание не подменяет проверку: SKIP печатается в лог CI, и как
            # только файл появится, проверка включится без правок.
            if check.get("pending"):
                skipped.append(f"§{check['section']}: {check['aggregate']} — {check['pending']}")
                continue
            problems.append(f"§{check['section']}: нет агрегата {check['aggregate']}")
            continue
        if check["aggregate"] not in cache:
            cache[check["aggregate"]] = json.loads(agg_path.read_text(encoding="utf-8"))
        agg = cache[check["aggregate"]]
        try:
            values = {k: resolve(agg, ptr) for k, ptr in check["values"].items()}
        except (KeyError, IndexError, TypeError) as exc:
            problems.append(f"§{check['section']}: указатель не разрешён ({exc})")
            continue
        expected = check["template"].format(**values)
        body = section_text(check["section"])
        if body is None:
            problems.append(f"§{check['section']}: раздел не найден в {PAPER.name}")
            continue
        checked += 1
        forms = [expected]
        if isinstance(values.get("v"), float):
            forms = [check["template"].format(**{**values, "v": f})
                     for f in variants(values["v"])]

        def _norm(text: str) -> str:
            """Типографские минусы и пробелы -> ASCII: рукопись пишет «−0.700» (U+2212),
            а агрегат — «-0.7» (дефис). Без нормализации гейт ложно краснеет."""
            return (text.replace("\u2212", "-").replace("\u2013", "-")
                        .replace("\u2014", "-").replace("\u00a0", " "))

        def _present(form: str) -> bool:
            """Число должно стоять отдельно: не быть частью другого числа."""
            return re.search(rf"(?<![\d.,]){re.escape(_norm(form))}(?![\d])",
                             _norm(body)) is not None

        if not any(_present(f) for f in forms):
            problems.append(
                f"§{check['section']}: в тексте нет «{expected}» (из {check['aggregate']}, "
                f"ключи {check['values']}) — {check['note']}"
            )

    print(f"[sections] проверок: {len(CHECKS)}, выполнено: {checked}, отложено: {len(skipped)}")
    for s in skipped:
        print(f"[sections] SKIP (отложено): {s}")
    if problems:
        for p in problems:
            print(f"[sections] ОШИБКА: {p}")
        print(f"[sections] проблем: {len(problems)}")
        return 1
    print("[sections] OK — числа разделов воспроизводятся из агрегатов")
    return 0


if __name__ == "__main__":
    sys.exit(main())
