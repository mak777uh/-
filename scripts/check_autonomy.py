"""check_autonomy.py — the autonomy policy has to be machine-readable, and its protected paths have to be enforced.

Why. The laboratory already had standing permissions, but they lived in chat and in prose (`AGENTS.md`), so every cycle
re-litigated them and a risky action could slip through because nobody remembered the rule at the moment of the commit.
`lab/autonomy-rules.json` turns them into data: what may be done without asking, what needs the owner, what is forbidden, and
which paths are protected because they are publication or the physics of the world.

Two modes.

* `--check` (default, runs in `make verify`): the file parses, carries the three lists and the budgets, and every protected
  path exists. Structure only — a gate that inspects history would fail on every old commit.
* `--range A..B`: every commit in the range that touches a protected path must also touch `docs/decision-log.md`. This is the
  enforcing half; it is meant for a pre-commit hook (`--staged`) or for a periodic audit, not for every CI run.

Run:
    python scripts/check_autonomy.py
    python scripts/check_autonomy.py --staged
    python scripts/check_autonomy.py --range origin/main..HEAD
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULES = ROOT / "lab" / "autonomy-rules.json"
DECISION_LOG = "docs/decision-log.md"


def load() -> dict:
    return json.loads(RULES.read_text(encoding="utf-8"))


def check_structure() -> list[str]:
    problems: list[str] = []
    if not RULES.is_file():
        return [f"нет {RULES.relative_to(ROOT)}"]
    try:
        rules = load()
    except json.JSONDecodeError as exc:
        return [f"autonomy-rules.json не разбирается: {exc}"]
    for key in ("allowed_without_asking", "requires_owner", "forbidden", "protected_paths", "budgets", "principle"):
        if key not in rules:
            problems.append(f"нет поля {key}")
    for key in ("allowed_without_asking", "requires_owner", "forbidden"):
        if key in rules and len(rules[key]) < 3:
            problems.append(f"{key}: меньше трёх пунктов — политика из одного правила не политика")
    budgets = rules.get("budgets") or {}
    for key in ("gpu_hours_without_asking", "wall_hours_without_asking"):
        if key not in budgets:
            problems.append(f"budgets: нет {key}")
    for path in rules.get("protected_paths") or []:
        if not (ROOT / path).exists():
            problems.append(f"protected_paths: {path} не существует")
    overlap = set(rules.get("allowed_without_asking") or []) & set(rules.get("forbidden") or [])
    if overlap:
        problems.append(f"пункт одновременно разрешён и запрещён: {sorted(overlap)}")
    return problems


def git(*args: str) -> str:
    out = subprocess.run(["git", *args], cwd=str(ROOT), capture_output=True, text=True,
                         encoding="utf-8", errors="replace")
    return out.stdout


def protected(path: str, patterns: list[str]) -> bool:
    return any(path == p or path.startswith(p.rstrip("/") + "/") or path.startswith(p) for p in patterns)


def check_range(rev_range: str) -> list[str]:
    rules = load()
    patterns = rules.get("protected_paths") or []
    commits = [c for c in git("rev-list", "--reverse", rev_range).splitlines() if c.strip()]
    if not commits:
        return []
    problems: list[str] = []
    for commit in commits:
        files = [f for f in git("show", "--name-only", "--pretty=format:", commit).splitlines() if f.strip()]
        touched = [f for f in files if protected(f, patterns)]
        if touched and DECISION_LOG not in files:
            subject = git("log", "-1", "--pretty=%s", commit).strip()
            problems.append(f"{commit[:8]} «{subject[:60]}» трогает защищённый путь "
                            f"({', '.join(touched[:3])}) без записи в {DECISION_LOG}")
    return problems


def check_staged() -> list[str]:
    rules = load()
    patterns = rules.get("protected_paths") or []
    files = [f for f in git("diff", "--cached", "--name-only").splitlines() if f.strip()]
    touched = [f for f in files if protected(f, patterns)]
    if touched and DECISION_LOG not in files:
        return [f"в индексе защищённый путь ({', '.join(touched[:3])}) без записи в {DECISION_LOG}: "
                f"это публикация или физика мира, нужно решение владельца"]
    return []


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="autonomy policy check")
    ap.add_argument("--range", help="диапазон коммитов, например origin/main..HEAD")
    ap.add_argument("--staged", action="store_true", help="проверить индекс (для pre-commit)")
    args = ap.parse_args(argv)

    problems = check_structure()
    if args.staged:
        problems += check_staged()
    if args.range:
        problems += check_range(args.range)

    if problems:
        for line in problems:
            print(f"  ПРОВАЛ: {line}")
        print(f"[autonomy] проблем: {len(problems)}")
        return 1
    rules = load()
    print(f"[autonomy] ok: разрешено {len(rules['allowed_without_asking'])}, "
          f"требует владельца {len(rules['requires_owner'])}, запрещено {len(rules['forbidden'])}, "
          f"защищённых путей {len(rules['protected_paths'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
