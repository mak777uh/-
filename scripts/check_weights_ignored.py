"""Gate: weights files must be ignored by git.

Why. Weights are the one artifact the repository deliberately does not carry (AGENTS.md §5a: git is thin
memory, not a weight store). If a `.pt` file is not ignored, a single `git add -A` puts a multi-megabyte binary
into history, where it cannot be removed without rewriting shared history - which the contract forbids.

The gate reads `.gitignore` and checks that every weights suffix is covered. It does not ask git, so it works in
a scratch copy without a repository.

Usage:
  python scripts/check_weights_ignored.py [root]
"""
from __future__ import annotations
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUFFIXES = (".pt", ".pth", ".ckpt")


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    root = argv[0] if argv else ROOT
    gi = os.path.join(root, ".gitignore")
    if not os.path.exists(gi):
        print("[weights] нет .gitignore — веса не игнорируются")
        return 1
    with open(gi, encoding="utf-8") as fh:
        rules = [l.strip() for l in fh if l.strip() and not l.strip().startswith("#")]

    problems: list[str] = []
    for suffix in SUFFIXES:
        covered = any(
            r == suffix or r == f"*{suffix}" or r.endswith(f"*{suffix}") or suffix in r
            for r in rules
        )
        if not covered:
            problems.append(f"суффикс {suffix} не покрыт правилом .gitignore")

    if problems:
        for p in problems:
            print(f"  ПРОВАЛ: {p}")
        print(f"[weights] проблем: {len(problems)}")
        return 1
    print(f"[weights] ok: все суффиксы весов {SUFFIXES} игнорируются")
    return 0


if __name__ == "__main__":
    sys.exit(main())
