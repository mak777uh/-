#!/usr/bin/env python
"""Провенанс серии: все артефакты получены одним кодом и на чистом дереве?

R15: артефакт несёт `git_commit` и `dirty`; серия валидна, только если коммит один и дерево
чистое. Скрипт группирует артефакты по коммиту и печатает расхождения.

Запуск: python library/tools/series_provenance.py --src morphogenesis/experiments/E09_pond --glob "colinv4_*.json"
Выход 1, если коммитов больше одного или есть dirty/отсутствие поля.
"""
from __future__ import annotations

import argparse
import glob
import json
from collections import defaultdict
from pathlib import Path


def provenance(data: dict) -> tuple[str | None, bool | None, str]:
    for holder_name in ("config", "summary", "meta", ""):
        holder = data.get(holder_name) if holder_name else data
        if not isinstance(holder, dict):
            continue
        commit = holder.get("git_commit") or holder.get("code_commit")
        dirty = holder.get("dirty") if "dirty" in holder else holder.get("git_dirty")
        if commit:
            return str(commit), (bool(dirty) if dirty is not None else None), holder_name or "root"
    return None, None, "—"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--src", default="morphogenesis/experiments/E09_pond")
    ap.add_argument("--glob", default="*.json")
    ap.add_argument("--json", default=None)
    args = ap.parse_args(argv)

    files = sorted(glob.glob(str(Path(args.src) / args.glob)))
    by_commit: dict[str, list[str]] = defaultdict(list)
    missing, dirty = [], []
    for name in files:
        data = json.loads(Path(name).read_text(encoding="utf-8"))
        commit, is_dirty, where = provenance(data)
        if not commit:
            missing.append(Path(name).name)
            continue
        by_commit[commit[:12]].append(Path(name).name)
        if is_dirty:
            dirty.append(Path(name).name)

    print(f"артефактов: {len(files)} | коммитов: {len(by_commit)} | без провенанса: {len(missing)} "
          f"| грязных: {len(dirty)}")
    for commit, names in sorted(by_commit.items(), key=lambda kv: -len(kv[1])):
        print(f"  {commit}: {len(names)} шт, например {names[0]}")
    ok = len(by_commit) <= 1 and not dirty
    if missing:
        print(f"  БЕЗ ПРОВЕНАНСА (нарушение R15): {missing[:3]}{'…' if len(missing) > 3 else ''}")
    if dirty:
        print(f"  ГРЯЗНОЕ ДЕРЕВО: {dirty[:3]}{'…' if len(dirty) > 3 else ''}")
    if not ok:
        print("  ВЕРДИКТ: серия невалидна как единый прогон кода")
    if args.json:
        Path(args.json).write_text(json.dumps({
            "files": len(files), "commits": dict(by_commit),
            "missing": missing, "dirty": dirty, "ok": ok}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
