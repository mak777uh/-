#!/usr/bin/env python
"""Проверить пакеты доказательств в library/claims-evidence.md.

Что проверяет (без сети):
  * колонка «Артефакт»: путь/шаблон существует в репозитории (glob), иначе — пробел;
  * колонка «Якорь»: P-номер есть в library/hypotheses/*.md («| P<n> |»), иначе — пробел;
  * колонка «Пробел»: строка не должна быть пустой/«нет».

Запуск: python scripts/claim_audit.py [--json out.json]
Выход 1, если есть пробелы (удобно для CI).
"""
from __future__ import annotations

import argparse
import glob
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TABLE = REPO / "library" / "claims-evidence.md"
HYP = REPO / "library" / "hypotheses"
EMPTY = {"", "нет", "—", "-", "n/a"}


def hypotheses_text() -> str:
    return "\n".join(p.read_text(encoding="utf-8") for p in sorted(HYP.glob("*.md")))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", default=None)
    args = ap.parse_args(argv)

    if not TABLE.exists():
        print(f"нет файла: {TABLE}")
        return 1
    text = hypotheses_text()
    rows = []
    problems = 0
    for line in TABLE.read_text(encoding="utf-8").splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 8 or not re.fullmatch(r"C\d+", cells[0]):
            continue
        cid, claim, artifact, control, effect, boundary, anchor, counter, gap = cells[:9]
        row = {"claim": cid, "title": claim, "artifact": artifact, "anchor": anchor,
               "gap": gap, "artifact_ok": None, "anchor_ok": None, "gap_ok": gap.lower() not in EMPTY}
        if artifact and artifact not in EMPTY:
            row["artifact_ok"] = bool(glob.glob(str(REPO / artifact)))
        if anchor and anchor not in EMPTY:
            row["anchor_ok"] = bool(re.search(rf"\| {re.escape(anchor)} \|", text))
        missing = [k for k in ("artifact_ok", "anchor_ok") if row[k] is False]
        if not row["gap_ok"]:
            missing.append("gap")
        row["problems"] = missing
        problems += len(missing)
        rows.append(row)

    print(f"пакетов: {len(rows)} | проблем: {problems}")
    for row in rows:
        mark = "ok" if not row["problems"] else ",".join(row["problems"])
        print(f"  {row['claim']}: {mark}")

    if args.json:
        Path(args.json).write_text(json.dumps({"rows": rows, "problems": problems},
                                              ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
