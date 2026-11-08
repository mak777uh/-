"""Number gate for article 036: every number in the text must be produced by a command.

The article makes ten checkable claims. This script runs the commands and compares their output with the
numbers the article states. A mismatch is a failure: the article would then describe a repository that does
not exist.

Usage: python scripts/check_article_036_numbers.py
"""
from __future__ import annotations
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTICLE = os.path.join(ROOT, "articles", "036-a-research-bench-where-the-instrument-reports-on-itself.md")

CHECKS: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    CHECKS.append((name, ok, detail))
    print(f"{'OK  ' if ok else 'FAIL'} {name}{(' — ' + detail) if detail and not ok else ''}")


def run(args: list[str], cwd: str = ROOT) -> tuple[int, str]:
    env = dict(os.environ)
    elan = os.path.join(os.path.expanduser("~"), ".elan", "bin")
    cargo = os.path.join(os.path.expanduser("~"), ".cargo", "bin")
    env["PATH"] = os.pathsep.join([elan, cargo, env.get("PATH", "")])
    p = subprocess.run(args, cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", env=env, timeout=900)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def count_files(pattern: str) -> int:
    import glob
    return len(glob.glob(os.path.join(ROOT, pattern)))


def main() -> int:
    with open(ARTICLE, encoding="utf-8") as fh:
        text = fh.read()

    # 1. repository counts
    check("583 reports", count_files("reports/*.md") == 583, f"found {count_files('reports/*.md')}")
    check("43 articles", count_files("articles/*.md") == 43, f"found {count_files('articles/*.md')}")
    check("791 raw artifacts",
          count_files("morphogenesis/experiments/E09_pond/*.json") == 791,
          f"found {count_files('morphogenesis/experiments/E09_pond/*.json')}")
    check("486 scripts", count_files("scripts/*.py") == 486, f"found {count_files('scripts/*.py')}")
    check("8 Lean files", count_files("formal/*.lean") == 8, f"found {count_files('formal/*.lean')}")
    check("84 tests",
          count_files("morphogenesis/tests/*.py") == 84,
          f"found {count_files('morphogenesis/tests/*.py')}")

    rc, out = run(["git", "rev-list", "--count", "HEAD"])
    commits = int(out.strip()) if rc == 0 and out.strip().isdigit() else -1
    check("2141 commits", commits == 2141, f"found {commits}")

    # 2. the gates
    rc, out = run([sys.executable, "scripts/lean_check.py"])
    m = re.search(r"гипотез:\s*(\d+),\s*теорем:\s*(\d+)", out)
    theorems = int(m.group(2)) if m else -1
    check("40 theorems", theorems == 40, f"found {theorems}")

    rc, out = run([sys.executable, "scripts/policy_bridge.py"])
    m = re.search(r"действий:\s*(\d+),\s*расхождений с файлом:\s*(\d+),\s*без сопоставления:\s*(\d+)", out)
    if m:
        check("15 rules bridged", int(m.group(1)) == 15, f"found {m.group(1)}")
        check("0 bridge disagreements", int(m.group(2)) == 0, f"found {m.group(2)}")
        check("0 unmapped rules", int(m.group(3)) == 0, f"found {m.group(3)}")
    else:
        check("bridge output parsed", False, out[-200:])

    rc, out = run([sys.executable, "scripts/policy_diff.py"])
    m = re.search(r"случаев:\s*(\d+),\s*реализаций:\s*(\d+),\s*расхождений:\s*(\d+)", out)
    if m:
        check("7 cases", int(m.group(1)) == 7, f"found {m.group(1)}")
        check("3 implementations", int(m.group(2)) == 3, f"found {m.group(2)}")
        check("0 implementation disagreements", int(m.group(3)) == 0, f"found {m.group(3)}")
    else:
        check("policy_diff output parsed", False, out[-200:])

    rc, out = run([sys.executable, "scripts/closure_probe.py"])
    m = re.search(r"проб:\s*(\d+),\s*поймано:\s*(\d+),\s*дыр:\s*(\d+)", out)
    if m:
        check("5 probes", int(m.group(1)) == 5, f"found {m.group(1)}")
        check("5 caught", int(m.group(2)) == 5, f"found {m.group(2)}")
        check("0 holes", int(m.group(3)) == 0, f"found {m.group(3)}")
    else:
        check("closure output parsed", False, out[-200:])

    # 3. the article states these numbers
    for phrase in ("583 reports", "43 articles", "791 raw artifacts", "486 scripts",
                   "8 Lean files", "84 tests", "2 141 commits", "40 theorems",
                   "15 rules", "7 cases", "3 implementations", "5 probes"):
        check(f"article states «{phrase}»", phrase in text, "not found in the article")

    # 4. the article must not claim what is not proved
    check("article says closure is measured, not proved",
          "only measured" in text or "measured, not proved" in text or "only measured" in text.lower())
    check("article admits the readouts are unused",
          "have not been used in a completed experiment" in text)

    fails = sum(1 for _, ok, _ in CHECKS if not ok)
    print(f"\n[article-036] проверок: {len(CHECKS)}, провалов: {fails}")
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
