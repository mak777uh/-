"""Gate: a report written after 08.11 must be an observation, not an argument.

The rules are in docs/report-template.md. This script checks the reports that opt in by carrying the marker
line `<!-- report-format: observation -->`; older reports are history and are not rewritten (AGENTS.md: old
reports are not rewritten).

Two kinds of report are recognised, because demanding the same things of both is a mistake the first version
made:

  - an EXPERIMENT report (`<!-- report-kind: experiment -->`) measures something new: it must carry the three
    readouts and the first 20 steps;
  - an AUDIT report (`<!-- report-kind: audit -->`) reads artifacts that already exist: it has no new
    measurement, so the readouts and the first steps are not required of it. What it must carry is the count
    of artifacts it read and the honest split between those that can answer the question and those that
    cannot.

Usage:
  python scripts/check_report_style.py                 # check every opt-in report
  python scripts/check_report_style.py reports/x.md    # check one
"""
from __future__ import annotations
import argparse
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARKER = "<!-- report-format: observation -->"
KIND_RE = re.compile(r"<!--\s*report-kind:\s*(experiment|audit)\s*-->")

REQUIRED_SECTIONS = [
    "## 1. What we looked at",
    "## 2. What we saw",
    "## 3. What it means",
    "## 4. What we do not know",
    "## 5. What this changes in the next experiment",
]

FORBIDDEN = [
    r"\bbreakthrough\b", r"\brevolutionary\b", r"\bnovel\b", r"\bimportant\b",
    r"\bstronger\b", r"\bweaker\b", r"\bdeeper\b", r"\bsignificantly\b",
    r"\bhuge\b", r"\btiny\b", r"\bmassive\b", r"\bthe design was wrong\b",
    r"\bwe should look into\b",
]

READOUTS = ["situation_explained", "record_explained", "energy_per_behaviour"]


def check(path: str) -> list[str]:
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    if MARKER not in text:
        return []
    errs: list[str] = []
    for sec in REQUIRED_SECTIONS:
        if sec not in text:
            errs.append(f"нет раздела «{sec}»")
    low = text.lower()
    for pat in FORBIDDEN:
        if re.search(pat, low):
            errs.append(f"запрещённое слово: {pat}")

    m = KIND_RE.search(text)
    kind = m.group(1) if m else "experiment"
    if kind == "experiment":
        for r in READOUTS:
            if r not in text:
                errs.append(f"нет обязательного показания {r}")
        if not re.search(r"\b(first|первые)\s*(20|двадцать)", low):
            errs.append("первые 20 шагов не доложены (P4, P186)")
    else:  # audit
        if not re.search(r"\bartifacts?\b|артефакт", low):
            errs.append("аудит не называет число прочитанных артефактов")
        if "cannot answer" not in low and "не может ответить" not in low:
            errs.append("аудит не отделяет артефакты, которые могут ответить, от тех, которые не могут")
    return errs


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="*")
    args = ap.parse_args(argv)
    paths = args.paths or sorted(glob.glob(os.path.join(ROOT, "reports", "*.md")))
    checked = 0
    total = 0
    for p in paths:
        errs = check(p)
        if errs:
            checked += 1
            total += len(errs)
            print(f"✗ {os.path.basename(p)}")
            for e in errs:
                print(f"    {e}")
    print(f"\n[report-style] отчётов в новом формате: {checked}, ошибок: {total}")
    return 0 if total == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
