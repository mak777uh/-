"""check_article_numbers.py — числа статьи 028 обязаны воспроизводиться из агрегатов.

Зачем. Перед публикацией нужно машинное доказательство, что ни одно число в статье не разошлось с артефактами.
`verify_sections_numbers.py` покрывает рукопись (`paper.md`), а статья 028 живёт отдельным файлом и не
проверялась — именно поэтому библиотекарь нашёл два числа без артефакта (аудит 31.10).

Как устроено. Таблица `CHECKS`: для каждой записи берётся агрегат, из него — значение, оно форматируется и
ищется в тексте статьи **дословно**. Если строка не найдена — расхождение (артефакт прав, статья нет).

Запуск:
    python scripts/check_article_numbers.py            # отчёт
    python scripts/check_article_numbers.py --ci       # падение при расхождении
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTICLES = [
    ROOT / "articles" / "028-pole-bez-zadannyh-obektov.md",          # ru, v1.4 (опубликована)
    ROOT / "articles" / "028-field-without-stipulated-objects.md",   # en, v1.5
]
L1 = ROOT / "morphogenesis" / "experiments" / "L1_field"
POND = ROOT / "morphogenesis" / "experiments" / "E09_pond"

# (что ищем в статье, файл агрегата, путь в JSON, как форматировать)
CHECKS: list[dict] = [
    # --- §4.9: времена жизни (X23, сиды 171..180)
    {"agg": L1 / "lifetimes_matrix.json", "path": "by_arm.static.median_life_steps", "fmt": "{:d}", "what": "медиана жизни, неоднородный"},
    {"agg": L1 / "lifetimes_matrix.json", "path": "by_arm.homog.median_life_steps", "fmt": "{:d}", "what": "медиана жизни, однородный"},
    {"agg": L1 / "lifetimes_matrix.json", "path": "by_arm.static.durable_per_run", "fmt": "{:.1f}", "what": "долгоживущих, неоднородный"},
    {"agg": L1 / "lifetimes_matrix.json", "path": "by_arm.homog.durable_per_run", "fmt": "{:.1f}", "what": "долгоживущих, однородный"},
    {"agg": L1 / "lifetimes_matrix.json", "path": "by_arm.static.median_peak_size", "fmt": "{:d}", "what": "пик площади, неоднородный"},
    {"agg": L1 / "lifetimes_matrix.json", "path": "by_arm.homog.median_peak_size", "fmt": "{:d}", "what": "пик площади, однородный"},
    {"agg": L1 / "lifetimes_matrix.json", "path": "by_arm.static.share_durable", "fmt": "{:.0f} %", "what": "доля долгоживущих"},
    {"agg": L1 / "lifetimes_matrix.json", "path": "by_arm.homog.share_short", "fmt": "{:.0f} %", "what": "доля короткоживущих"},
    # --- §4a: обитаемость (X43)
    {"agg": POND / "habitable_matrix.json", "path": "summary.survived", "fmt": "{:d}", "what": "выживших прогонов"},
    {"agg": POND / "habitable_matrix.json", "path": "summary.median_alive_last", "fmt": "{:g}", "what": "медиана клеток"},
    {"agg": POND / "habitable_matrix.json", "path": "summary.min", "fmt": "{:d}", "what": "минимум клеток"},
    {"agg": POND / "habitable_matrix.json", "path": "summary.max", "fmt": "{:d}", "what": "максимум клеток"},
    # --- §4b: адекватность (X44, мера с командой)
    {"agg": POND / "adequacy_mi.json", "path": "by_arm.cost.under.median_excess", "fmt": "{:.4f}", "what": "адекватность, цена высокая"},
    {"agg": POND / "adequacy_mi.json", "path": "by_arm.cheap.under.median_excess", "fmt": "{:.4f}", "what": "адекватность, цена низкая"},
    {"agg": POND / "adequacy_mi.json", "path": "by_arm.free.under.median_excess", "fmt": "{:.4f}", "what": "адекватность, цена нулевая"},
]


def dig(obj, path: str):
    cur = obj
    for part in path.split("."):
        if isinstance(cur, dict):
            cur = cur[part]
        elif isinstance(cur, list):
            cur = cur[int(part)]
        else:
            raise KeyError(path)
    return cur


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="сверка чисел статьи 028 с агрегатами")
    ap.add_argument("--ci", action="store_true")
    args = ap.parse_args(argv)

    texts = {}
    for art in ARTICLES:
        if art.exists():
            texts[art.name] = art.read_text(encoding="utf-8")
    if not texts:
        print("[article] статей нет")
        return 1
    bad = 0
    for c in CHECKS:
        agg = Path(c["agg"])
        if not agg.exists():
            print(f"[article] ОТСУТСТВУЕТ агрегат {agg.relative_to(ROOT)} — {c['what']}")
            bad += 1
            continue
        try:
            value = dig(json.loads(agg.read_text(encoding="utf-8")), c["path"])
        except (KeyError, IndexError, TypeError):
            print(f"[article] нет пути {c['path']} в {agg.name} — {c['what']}")
            bad += 1
            continue
        if c["fmt"].endswith(" %"):
            needle = c["fmt"].format(value * 100)
        else:
            needle = c["fmt"].format(value)
        for name, text in texts.items():
            if needle not in text:
                print(f"[article] РАСХОЖДЕНИЕ: {c['what']} = {needle} (из {agg.name}), нет в {name}")
                bad += 1

    total = len(CHECKS) * len(texts)
    if bad:
        print(f"[article] расхождений: {bad} из {total}")
        return 1 if args.ci else 0
    print(f"[article] все {total} чисел статьи совпадают с агрегатами")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
