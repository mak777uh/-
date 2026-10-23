"""Задание библиотекарю: собирается из текущего состояния работы, а не пишется руками.

Зачем: библиотекарь не должен угадывать, что нам нужно. Задание формируется из
1) очереди литературы `lab/lit-queue.json` (открытые вопросы),
2) текущей фазы `docs/plan-alive.md`,
3) последних чисел `docs/world-design.md` (что уже проверено — чтобы не искали
   повторно то, что у нас уже есть).

Выход: `_hourly/library-brief.md` — готовое задание с разделами «что проверяем»,
«что искать», «что НЕ искать», «формат записи», «критерий полезности».
"""
from __future__ import annotations

import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT / "repo"
OUT = ROOT.parent / "_hourly" / "library-brief.md"

# направления поиска по текущей фазе (обновляется вручную при смене фазы)
SEARCH_DIRECTIONS = [
    {
        "why": "P1: обучение в течение жизни не бьёт фиксированное правило",
        "terms": [
            "melioration vs matching law suboptimal choice",
            "evolution of learning versus innate behaviour gain function",
            "tragedy of the commons multilevel selection group benefit",
            "density-dependent dispersal evolution crowding",
        ],
    },
    {
        "why": "P2: перенос между средами, скорость изменения среды",
        "terms": [
            "evolutionary rescue plasticity two-phase",
            "environmental change rate versus adaptation time prediction",
        ],
    },
    {
        "why": "P3: порог мутаций и скорость обучения как наследуемый признак",
        "terms": [
            "error threshold population size exponential",
            "evolution of learning rate meta-learning",
        ],
    },
]

ALREADY_HAVE = [
    "Fretwell & Lucas 1970 (IFD) — есть запись P1 в library/hypotheses/pond-lineage.md",
    "Eigen 1971 / Aston 2013 (порог мутаций) — P2/P3",
    "Ashander 2016, Greenspoon & Spencer 2021 (rescue и пластичность) — P4/P5",
    "Paenke 2009, Suzuki & Arita 2007 (роль обучения) — P6/P7",
    "Clauset 2009 (power law), Bak 1987 (SOC), MSPD — P8/P9/P10",
]


def load_queue() -> list[dict]:
    path = REPO / "lab" / "lit-queue.json"
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return [i for i in data.get("items", []) if i.get("status") != "done"]


def current_numbers() -> list[str]:
    """Последние числа из docs/world-design.md — чтобы библиотекарь не искал уже проверенное."""
    path = REPO / "docs" / "world-design.md"
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    rows = re.findall(r"^\|.*\|\s*$", text, flags=re.MULTILINE)
    interesting = [r for r in rows if re.search(r"(601|594|540|532|529|509|473|429)", r)]
    return interesting[-8:]


def render() -> str:
    queue = load_queue()
    numbers = current_numbers()

    lines = [
        "# Задание библиотекарю (сформировано автоматически)",
        "",
        "Источник: очередь `lab/lit-queue.json`, план `docs/plan-alive.md`, числа из",
        "`docs/world-design.md`. Задание пересобирается скриптом `scripts/library_brief.py`.",
        "",
        "## Что мы проверяем сейчас",
        "",
        "P1: пластичность политики размещения спор. Все проверенные схемы обучения",
        "(по исходу 532, локальный вес 529, bandit 540, colony 492) проигрывают",
        "фиксированному правилу (w=0.1 → 601) и IFD (594). Гипотеза: дело в сигнале",
        "обучения и/или в конфликте личной и групповой выгоды.",
        "",
        "## Открытые вопросы очереди",
        "",
    ]
    if queue:
        for item in queue:
            kinds = ",".join(item.get("kinds", []))
            lines.append(f"- **{item['id']}** [{kinds}] {item['text'][:160]}")
            for query in item.get("queries", [])[:2]:
                lines.append(f"  - запрос: `{query}`")
    else:
        lines.append("- очередь пуста; см. направления поиска ниже")

    lines += [
        "",
        "## Что искать (направления текущей фазы)",
        "",
    ]
    for direction in SEARCH_DIRECTIONS:
        lines.append(f"**{direction['why']}**")
        for term in direction["terms"]:
            lines.append(f"- `{term}`")
        lines.append("")

    lines += [
        "## Что НЕ искать (уже есть в библиотеке)",
        "",
    ]
    lines += [f"- {item}" for item in ALREADY_HAVE]

    lines += [
        "",
        "## Последние числа (что уже проверено у нас)",
        "",
        "Не ищи повторно эти результаты; ищи то, что меняет их интерпретацию.",
        "",
    ]
    lines += numbers if numbers else ["- (нет)"]

    lines += [
        "",
        "## Формат записи",
        "",
        "Ссылка/DOI, `[К]`/`[А]` (полный текст или только аннотация), `Что даёт:` 2–4",
        "предложения своими словами, `Чего не даёт:`, `Оговорка:`, `Гипотеза (наша)`, блок",
        "**`Код и данные:`** (открыт ли код, есть ли сырые прогоны). Затем закрыть пункт",
        "очереди: `python scripts/lit_check.py --done L-XXX --result \"...\"`.",
        "",
        "## Критерий полезности",
        "",
        "Запись полезна, если из неё следует **проверяемое следствие для наших чисел**:",
        "новая функциональная форма, порог, или предсказание, которое можно сравнить с",
        "601/594 на существующих артефактах. «Интересно, но не проверяемо» — не в приоритет.",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    OUT.write_text(render(), encoding="utf-8")
    print(f"обновлено: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
