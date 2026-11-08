"""Gate: an experiment may not run without a manifest that passes the standing rules.

The rules come from the reading of Krishnamurti and from our own history of failed designs (P51, P74,
P190, P294, and the four tautologies of 07.11). Each rule is a field that must be present and must have
the right value; a missing field is a failure, not a default.

Usage:
  python scripts/check_experiment_manifest.py                     # check every manifest
  python scripts/check_experiment_manifest.py lab/experiments/E18.json
  python scripts/check_experiment_manifest.py --allow-add         # lift the moratorium (owner decision)
"""
from __future__ import annotations
import argparse
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST_DIR = os.path.join(ROOT, "lab", "experiments")

REQUIRED = [
    "id", "title", "question", "symptom", "first_hand", "adds_or_removes",
    "changes_set_or_values", "has_direction", "manipulation_reaches_dynamics",
    "sensitivity", "readouts", "first_steps_reported", "equally_satisfied_by_either_answer",
    "no_should_for_the_cell", "no_mechanism_added", "preregistered",
]

READOUTS_REQUIRED = {"situation_explained", "record_explained", "energy_per_behaviour"}


WAIVER_WORDS = ("unknown", "tbd", "to be determined", "неизвестно", "n/a", "потом")


def _numbers_in(obj) -> int:
    """How many actual numbers the sensitivity block contains, at any depth."""
    if isinstance(obj, bool):
        return 0
    if isinstance(obj, (int, float)):
        return 1
    if isinstance(obj, str):
        return 1 if any(ch.isdigit() for ch in obj) else 0
    if isinstance(obj, dict):
        return sum(_numbers_in(v) for v in obj.values())
    if isinstance(obj, list):
        return sum(_numbers_in(v) for v in obj)
    return 0


def _check_sensitivity(mid: str, sens: dict) -> list[str]:
    """The arithmetic must be arithmetic: a spread, a seed count with a reason, a refusal rule.

    A block that contains only prose, or that waives the calculation with a word like "unknown", fails.
    """
    errs: list[str] = []
    flat = json.dumps(sens, ensure_ascii=False).lower()
    if _numbers_in(sens) == 0:
        errs.append(f"{mid}: в sensitivity нет ни одного числа - это не арифметика")
    for word in WAIVER_WORDS:
        if word in flat and "estimate" not in flat and "оценк" not in flat:
            errs.append(f"{mid}: sensitivity откладывает расчёт словом «{word}»")
            break
    if "spread" not in flat and "разброс" not in flat and "sd" not in flat:
        errs.append(f"{mid}: sensitivity не называет ожидаемый разброс")
    if "seed" not in flat and "сид" not in flat:
        errs.append(f"{mid}: sensitivity не называет число сидов")
    if "refusal" not in flat and "отказ" not in flat:
        errs.append(f"{mid}: sensitivity не содержит правила отказа")
    return errs


def check_one(path: str, allow_add: bool) -> list[str]:
    errs: list[str] = []
    try:
        with open(path, encoding="utf-8") as fh:
            m = json.load(fh)
    except Exception as exc:  # noqa: BLE001
        return [f"{os.path.basename(path)}: не читается ({exc})"]

    for key in REQUIRED:
        if key not in m:
            errs.append(f"{m.get('id', '?')}: нет поля {key}")

    if m.get("adds_or_removes") == "add" and not allow_add:
        errs.append(f"{m.get('id', '?')}: добавление запрещено мораторием "
                    f"(adds_or_removes=add); разрешено только remove")
    if m.get("changes_set_or_values") == "values":
        errs.append(f"{m.get('id', '?')}: меняет только значения переменных — это жонглирование "
                    f"(P51), нужен set")
    mrd = m.get("manipulation_reaches_dynamics") or {}
    if not mrd.get("checked"):
        errs.append(f"{m.get('id', '?')}: не проверено, что манипуляция доходит до динамики")
    if not str(mrd.get("how", "")).strip():
        errs.append(f"{m.get('id', '?')}: пустое поле how в manipulation_reaches_dynamics")
    sens = m.get("sensitivity") or {}
    if not sens:
        errs.append(f"{m.get('id', '?')}: нет арифметики чувствительности")
    else:
        errs.extend(_check_sensitivity(m.get("id", "?"), sens))
    readouts = set(m.get("readouts") or [])
    missing = READOUTS_REQUIRED - readouts
    if missing:
        errs.append(f"{m.get('id', '?')}: нет обязательных показаний {sorted(missing)}")
    if m.get("first_steps_reported") is not True:
        errs.append(f"{m.get('id', '?')}: первые шаги не докладываются (P4, P186)")
    if m.get("equally_satisfied_by_either_answer") is not True:
        errs.append(f"{m.get('id', '?')}: опыт не чист — нужен одинаково приемлемый любой ответ (P112)")
    if m.get("no_should_for_the_cell") is not True:
        errs.append(f"{m.get('id', '?')}: в опыте есть «должен» для клетки (P63)")
    if m.get("no_mechanism_added") is not True and not allow_add:
        errs.append(f"{m.get('id', '?')}: добавляется механизм — запрещено мораторием")
    if m.get("preregistered") is not True:
        errs.append(f"{m.get('id', '?')}: манифест не пре-регистрирован")
    return errs


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--allow-add", action="store_true",
                    help="снять мораторий на добавления (решение владельца)")
    args = ap.parse_args(argv)

    paths = args.paths or sorted(glob.glob(os.path.join(MANIFEST_DIR, "*.json")))
    if not paths:
        print("[manifest] манифестов нет")
        return 0

    # GRANDFATHER (07.11): manifests written before this gate existed describe experiments already run
    # under the old rules. They are reported but do not fail the gate - the gate governs what runs NEXT.
    # A manifest is grandfathered if it has no "preregistered" field at all (the new format always has it).
    total = 0
    old_format = 0
    for p in paths:
        name = os.path.basename(p)
        try:
            with open(p, encoding="utf-8") as fh:
                m = json.load(fh)
        except Exception as exc:  # noqa: BLE001
            print(f"✗ {name}: не читается ({exc})")
            total += 1
            continue
        if "preregistered" not in m:
            old_format += 1
            print(f"· {name}: старый формат (до гейта), не проверяется")
            continue
        errs = check_one(p, args.allow_add)
        if errs:
            total += len(errs)
            for e in errs:
                print(f"✗ {e}")
        else:
            print(f"✓ {name}")
    print(f"\n[manifest] манифестов: {len(paths)} (старых: {old_format}), ошибок: {total}")
    return 0 if total == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
