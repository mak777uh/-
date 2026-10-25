#!/usr/bin/env python
"""check_readme_fresh.py — витрина не должна отставать от результатов.

Зачем: 25.10 к вечеру в README всё ещё стояло «E09_pond: learning does not pay off…»,
хотя за день закрылись W2-bud v1–v4, режим гибели и перечитывание инвазионной линии.
Числа при этом жили в рукописи, а витрина — нет. Решение: правило в контракте (§6a),
гейт ниже и ежедневное напоминание в утренней сводке.

Как проверяет: сравнивает **дату** последнего изменения README с датой последней записи
в `manuscript/CHANGELOG.md`. Если в CHANGELOG есть результат новее README — витрина
устарела. Сравниваются даты, а не коммиты: если всё сделано в один день, гейт зелёный
(иначе он падал бы на каждом коммите, где README обновляют вместе с рукописью).

Запуск:
    python scripts/check_readme_fresh.py           # проверка (CI, make verify)
    python scripts/check_readme_fresh.py --stamp   # поставить «Обновлено: сегодня»
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
CHANGELOG = ROOT / "manuscript" / "CHANGELOG.md"
# Отметка просмотра живёт ОТДЕЛЬНЫМ файлом: `lab/state.json` — генерируемый снимок
# (`lab.py state` его перезаписывает), и положенная туда отметка исчезает.
REVIEW = ROOT / "lab" / "readme-review.json"
DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")


def last_commit_date(path: Path) -> dt.date | None:
    proc = subprocess.run(["git", "log", "-1", "--format=%cs", "--", str(path.relative_to(ROOT))],
                          cwd=str(ROOT), capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    raw = proc.stdout.strip()
    try:
        return dt.date.fromisoformat(raw)
    except ValueError:
        return None


def review_stamp() -> tuple[dt.date | None, int]:
    """Отметка «витрину смотрели»: дата и допустимый интервал в днях."""
    try:
        data = json.loads(REVIEW.read_text(encoding="utf-8"))
    except Exception:
        return None, 2
    block = data.get("readme") or data   # старый формат держал поля в state.json, новый — в своём файле
    cadence = int(block.get("cadence_days") or 2)
    try:
        return dt.date.fromisoformat(str(block.get("reviewed_at"))), cadence
    except ValueError:
        return None, cadence


def newest_changelog_date() -> dt.date | None:
    if not CHANGELOG.exists():
        return None
    dates = [dt.date.fromisoformat(m) for m in DATE_RE.findall(CHANGELOG.read_text(encoding="utf-8"))]
    return max(dates) if dates else None


def stamp(today: dt.date) -> int:
    text = README.read_text(encoding="utf-8")
    line = f"Обновлено: {today.isoformat()}"
    if re.search(r"^Обновлено: \d{4}-\d{2}-\d{2}", text, re.M):
        text = re.sub(r"^Обновлено: \d{4}-\d{2}-\d{2}", line, text, count=1, flags=re.M)
    else:
        # вставить после первого заголовка
        lines = text.splitlines()
        for i, ln in enumerate(lines):
            if ln.startswith("#"):
                lines.insert(i + 1, "")
                lines.insert(i + 2, line)
                break
        text = "\n".join(lines) + "\n"
    README.write_text(text, encoding="utf-8", newline="\n")
    print(f"[readme] {line}")
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="витрина не отстаёт от результатов")
    ap.add_argument("--stamp", action="store_true", help="обновить строку «Обновлено»")
    ap.add_argument("--reviewed", action="store_true", help="отметить, что витрина просмотрена")
    args = ap.parse_args(argv)

    today = dt.date.today()
    if args.stamp:
        return stamp(today)
    if args.reviewed:
        try:
            data = json.loads(REVIEW.read_text(encoding="utf-8"))
        except Exception:
            data = {}
        data["reviewed_at"] = today.isoformat()
        data["reviewed_by"] = data.get("reviewed_by") or "lead"
        data.setdefault("cadence_days", 2)
        data["note"] = ("витрина просматривается не реже раза в 2 дня; проверка — по этой отметке, "
                        "а не по mtime файла (mtime можно тронуть, не посмотрев)")
        REVIEW.parent.mkdir(parents=True, exist_ok=True)
        REVIEW.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                          encoding="utf-8", newline="\n")
        print(f"[readme] отмечено как просмотренное: {today.isoformat()}")
        return 0

    readme_date = last_commit_date(README)
    result_date = newest_changelog_date()
    if readme_date is None or result_date is None:
        print("[readme] не смог определить даты — пропускаю (проверьте git-историю)")
        return 0
    reviewed, cadence = review_stamp()
    age = (today - reviewed).days if reviewed else None
    print(f"[readme] последнее изменение README: {readme_date}; новейший результат в CHANGELOG: {result_date}; "
          f"просмотрено: {reviewed} ({age} дн. назад, интервал {cadence} дн.)")
    if reviewed is None:
        print("[readme] ОШИБКА: нет отметки просмотра — задайте `--reviewed` после реального просмотра")
        return 1
    if age is not None and age > cadence:
        print(f"[readme] ОШИБКА: витрину не смотрели {age} дн. (> {cadence}) — обновите строку журнала и вердикт, "
              f"затем `--reviewed`")
        return 1
    if result_date > readme_date:
        print("[readme] ОШИБКА: витрина устарела — в рукописи есть результат новее, чем README")
        print("        обновите строку журнала и вердикт; затем `python scripts/check_readme_fresh.py --stamp`")
        return 1
    print("[readme] OK — витрина не отстаёт от рукописи")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
