"""Gate: a protected path may not change without a decision-log entry.

Why. `lab/autonomy-rules.json` lists paths that are either publication or the physics of the world. Changing one
is allowed, but not silently: the contract requires an entry in `docs/decision-log.md` in the same change.

This gate answers one question about one file: is this path protected, and if so, does the decision log mention
it? It is called by the closure probe with a planted protected path, and by `check_autonomy --staged` for the
real index.

Usage:
  python scripts/check_protected_staged.py <path> [root]
"""
from __future__ import annotations
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if not argv:
        print("usage: check_protected_staged.py <path> [root]")
        return 2
    path = argv[0]
    root = argv[1] if len(argv) > 1 else ROOT

    rules_path = os.path.join(root, "lab", "autonomy-rules.json")
    if not os.path.exists(rules_path):
        print("[protected] нет lab/autonomy-rules.json")
        return 0
    with open(rules_path, encoding="utf-8") as fh:
        rules = json.load(fh)
    protected = rules.get("protected_paths") or []

    norm = path.replace("\\", "/")
    hit = [p for p in protected if norm == p or norm.startswith(p.rstrip("/") + "/")]
    if not hit:
        print(f"[protected] ok: {path} не защищён")
        return 0

    log_path = os.path.join(root, "docs", "decision-log.md")
    mentioned = False
    if os.path.exists(log_path):
        with open(log_path, encoding="utf-8") as fh:
            mentioned = any(h in fh.read() for h in hit)

    if not mentioned:
        print(f"  ПРОВАЛ: {path} защищён ({hit[0]}), но в docs/decision-log.md нет записи")
        print(f"[protected] проблем: 1")
        return 1
    print(f"[protected] ok: {path} защищён и есть запись в decision-log")
    return 0


if __name__ == "__main__":
    sys.exit(main())
