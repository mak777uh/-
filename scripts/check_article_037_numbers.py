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

    # the seven errors: the FIRST numbered table must have seven rows numbered 1..7.
    # A later table in the same document also numbers rows 1,2,3,6 (the "does it fit the shape" check), so
    # counting every "| N |" row across the file gives 11 and is not what the claim is about.
    first_table: list[str] = []
    started = False
    for line in text.splitlines():
        m = re.match(r"^\| (\d) \| ", line)
        if m:
            started = True
            first_table.append(m.group(1))
        elif started:
            break
    check("the error table has 7 rows", len(first_table) == 7, f"found {first_table}")
    check("the errors are numbered 1..7",
          first_table == [str(i) for i in range(1, 8)], str(first_table))

    # the four principles
    ps = re.findall(r"^### P(\d)\. ", text, re.M)
    check("four principles", ps == ["1", "2", "3", "4"], str(ps))

    # Each of P1-P3 must state what would falsify it. P4 is no longer a principle but a theorem (Adams et al.
    # 2017, Poincare recurrence), and a theorem is not falsified by an experiment - what can be checked is
    # whether its ASSUMPTIONS apply. Demanding a falsifier of P4 was the first version's mistake, and the gate
    # must not repeat it.
    n_falsify = text.count("**What would falsify it.**")
    check("P1-P3 each state a falsification", n_falsify == 3, f"found {n_falsify}")
    check("P4 states what would violate its assumptions",
          "**What would violate its assumptions**" in text, "phrase missing")
    check("P4 is labelled a theorem, not a principle",
          "this is a theorem, not a principle" in text.lower(), "phrase missing")

    # the manifesto must state what it does not claim
    check("has a 'does not claim' section", "## 6. What this document does not claim" in text)

    # the three stopping conditions must each be present with a metric, a threshold and a seed count, or they
    # cannot fire - which was the referee's objection to the first version
    for tag in ("S1", "S2", "S3"):
        check(f"stopping condition {tag} is present", f"| {tag} |" in text)
    check("stopping conditions carry numeric thresholds",
          "0.02" in text and "0.9" in text, "thresholds missing")
    check("the weakest condition is named as such", "weakest of the three" in text)

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
