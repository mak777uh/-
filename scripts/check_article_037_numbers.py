"""Number gate for article 037: every count in the manifesto is produced by a command.

The manifesto makes claims about our own record. A claim about a record is only worth what the record says, so
the counts are checked here the same way article 036 checks its own.

Usage: python scripts/check_article_037_numbers.py [--self-test]
"""
from __future__ import annotations
import argparse
import glob
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTICLE = os.path.join(ROOT, "articles", "037-what-our-errors-say-about-the-limits-of-the-method.md")

CHECKS: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    CHECKS.append((name, ok, detail))
    print(f"{'OK  ' if ok else 'FAIL'} {name}{(' — ' + detail) if detail and not ok else ''}")


def count(pattern: str) -> int:
    return len(glob.glob(os.path.join(ROOT, pattern)))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)

    with open(ARTICLE, encoding="utf-8") as fh:
        text = fh.read()

    reports = count("reports/*.md")
    articles = count("articles/*.md")

    check("583 reports", reports == 583, f"found {reports}")
    check("43 articles stated in the text", "43 articles" in text, "phrase missing")
    # the article is itself the 44th once committed; the text says 43 because it describes the record BEFORE it
    check("article count is consistent with the record it describes",
          articles in (43, 44), f"found {articles}")

    elim = os.path.join(ROOT, "docs", "eliminations.md")
    if os.path.exists(elim):
        with open(elim, encoding="utf-8") as fh:
            rows = [l for l in fh if l.strip().startswith("|") and not set(l.strip()) <= set("|-: ")]
        n = len(rows)
        check("45 eliminated directions", n == 45, f"found {n}")
        check("45 stated in the text", "45 entries" in text, "phrase missing")
    else:
        check("eliminations register exists", False, "missing docs/eliminations.md")

    # the seven errors: the table must have seven numbered rows
    rows = re.findall(r"^\| (\d) \| ", text, re.M)
    check("the error table has 7 rows", len(rows) == 7, f"found {rows}")
    check("the errors are numbered 1..7", rows == [str(i) for i in range(1, 8)], str(rows))

    # the four principles
    ps = re.findall(r"^### P(\d)\. ", text, re.M)
    check("four principles", ps == ["1", "2", "3", "4"], str(ps))

    # each principle must state what would falsify it
    check("every principle has a falsification", text.count("**What would falsify it.**") == 4,
          f"found {text.count('**What would falsify it.**')}")

    # the manifesto must state what it does not claim
    check("has a 'does not claim' section", "## 6. What this document does not claim" in text)

    # the evidence appendix must point at files that exist
    for path in ("docs/eliminations.md", "scripts/check_experiment_manifest.py",
                 "scripts/check_design.py", "scripts/k_readouts.py",
                 "lab/experiments/E18.json", "reports/2026-11-08-corpus-audit.md"):
        check(f"evidence exists: {path}", os.path.exists(os.path.join(ROOT, path)))

    fails = sum(1 for _, ok, _ in CHECKS if not ok)
    print(f"\n[article-037] проверок: {len(CHECKS)}, провалов: {fails}")
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
