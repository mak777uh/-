"""check_design.py — пять проверок дизайна ДО серии. Гейт против нашего главного провала.

Зачем. 31.10 линия поля дала пять невалидных постановок подряд, около 110 прогонов впустую. Три из пяти были
невалидны по одной причине: **манипуляция не доходила до динамики**. Ещё одна — потому что отклик не писался.
Каждую из них можно было отбросить за минуты, а не за 40 прогонов. Здесь эти проверки выполняются машиной.

Пять проверок (шаблон — `docs/preregistration-template.md`):

1. **связность**: два прогона, отличающиеся ТОЛЬКО манипуляцией, дают разные хеши динамики;
2. **положительный контроль**: в плече, где эффект обязан быть, эффект записан числом (проверяется человеком,
   скрипт требует, чтобы поле было заполнено);
3. **отклик существует и варьирует**: поле пишется по срезам и имеет ненулевую дисперсию;
4. **арифметика чувствительности**: посчитаны sd, эффект и число сидов (поля обязательны);
5. **правило отказа**: перечислены исходы, при которых опыт объявляется нечувствительным.

Запуск:
    python scripts/check_design.py --prereg reports/2026-11-01-x99-preregistration.md --ci
    python scripts/check_design.py --pair on.json off.json --key "series[].components"
    python scripts/check_design.py --readout run.json --key "series[].components"

Коды выхода: 0 — все проверки прошли; 1 — провал (с названным пунктом).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import statistics as st
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_HEADINGS = [
    ("1. Manipulation is connected", "связность манипуляции"),
    ("2. Positive control fires", "положительный контроль"),
    ("3. Readout exists and varies", "отклик существует и варьирует"),
    ("4. Sensitivity arithmetic", "арифметика чувствительности"),
    ("5. Refusal rule", "правило отказа"),
]

# поля, которые обязаны быть заполнены в пре-регистрации (не пустые)
REQUIRED_TICKS = [
    ("connected", "связность"),
    ("positive control fires", "положительный контроль"),
    ("readout exists and varies", "отклик"),
    ("sensitivity computed", "чувствительность"),
    ("refusal rule written", "правило отказа"),
]


def dig_path(obj, path: str):
    """Достать значение по пути вида `series[].components` (список -> список значений)."""
    cur = obj
    parts = path.split(".")
    for part in parts:
        is_list = part.endswith("[]")
        key = part[:-2] if is_list else part
        if key:
            if not isinstance(cur, dict) or key not in cur:
                raise KeyError(path)
            cur = cur[key]
        if is_list:
            if not isinstance(cur, list):
                raise KeyError(path)
            # дальше — остаток пути применять к каждому элементу
            rest = ".".join(parts[parts.index(part) + 1:])
            if not rest:
                return cur
            return [dig_path(x, rest) for x in cur]
    return cur


def dynamics_hash(path: Path, key: str) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    values = dig_path(data, key)
    blob = json.dumps(values, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.md5(blob).hexdigest()[:12]


def check_pair(a: Path, b: Path, key: str) -> tuple[bool, str]:
    if not a.is_file() or not b.is_file():
        return False, f"нет файла: {a if not a.is_file() else b}"
    ha, hb = dynamics_hash(a, key), dynamics_hash(b, key)
    if ha == hb:
        return False, (f"ПРОВАЛ 1: динамика плеч идентична ({ha}) — манипуляция не доходит до мира. "
                       f"Это ровно случай X46: менялась метка, а не система")
    return True, f"связность есть: {ha} против {hb}"


def check_readout(path: Path, key: str) -> tuple[bool, str]:
    if not path.is_file():
        return False, f"нет файла: {path}"
    data = json.loads(path.read_text(encoding="utf-8"))
    try:
        values = dig_path(data, key)
    except KeyError:
        return False, f"ПРОВАЛ 3: поля `{key}` нет в артефакте — отклик не пишется"
    flat = [v for v in values if isinstance(v, (int, float)) and v is not None]
    if len(flat) < 5:
        return False, f"ПРОВАЛ 3: поля `{key}` почти нет данных ({len(flat)} значений)"
    if len(set(flat)) == 1:
        return False, f"ПРОВАЛ 3: `{key}` постоянно ({flat[0]}) — измерять нечего"
    return True, f"отклик есть: {len(flat)} значений, медиана {st.median(flat):.4g}, разброс {max(flat)-min(flat):.4g}"


def check_prereg(path: Path, structure_only: bool = False) -> tuple[bool, list[str]]:
    if not path.is_file():
        return False, [f"нет файла пре-регистрации: {path}"]
    text = path.read_text(encoding="utf-8")
    problems: list[str] = []
    notes: list[str] = []
    for heading, human in REQUIRED_HEADINGS:
        if heading not in text:
            problems.append(f"ПРОВАЛ: нет раздела «{human}» ({heading})")
    low = text.lower()
    if not structure_only:
        for phrase, human in REQUIRED_TICKS:
            if f"[x] {phrase}" not in low and f"- [x] {phrase}" not in low:
                problems.append(f"ПРОВАЛ: не отмечен пункт «{human}» (нужно `- [x] {phrase}`)")
    # незаполненные REQUIRED-поля шаблона
    leftover = [ln.strip() for ln in text.split("\n") if "…" in ln and "REQUIRED" not in ln]
    if leftover:
        notes.append(f"внимание: {len(leftover)} строк ещё с многоточием — проверьте, что это не пропуски")
    if not problems:
        notes.append("все пять разделов и отметок на месте")
    return not problems, problems + notes


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="пять проверок дизайна до серии")
    ap.add_argument("--prereg", help="файл пре-регистрации")
    ap.add_argument("--pair", nargs=2, metavar=("ON", "OFF"), help="два артефакта: с манипуляцией и без")
    ap.add_argument("--readout", help="артефакт, в котором должен быть отклик")
    ap.add_argument("--key", default="series[].components", help="путь к полю в артефакте")
    ap.add_argument("--structure", action="store_true",
                    help="только структура: разделы на месте, отметки не требуются (для make verify)")
    ap.add_argument("--ci", action="store_true", help="падение при любом провале")
    args = ap.parse_args(argv)

    ok = True
    if args.prereg:
        good, lines = check_prereg(Path(args.prereg), structure_only=args.structure)
        ok &= good
        for line in lines:
            print("  " + line)
    if args.pair:
        good, line = check_pair(Path(args.pair[0]), Path(args.pair[1]), args.key)
        ok &= good
        print("  " + line)
    if args.readout:
        good, line = check_readout(Path(args.readout), args.key)
        ok &= good
        print("  " + line)
    if not (args.prereg or args.pair or args.readout):
        ap.print_help()
        return 2
    print("[design] итог:", "пройдено" if ok else "ПРОВАЛ")
    return 0 if (ok or not args.ci) else 1


if __name__ == "__main__":
    raise SystemExit(main())
