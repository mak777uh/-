"""Tell me where a NEW artifact has to be registered.

Three times on 07.11 a new result file made a gate go red because it had not been registered:
  - `library/result-map.json` (the literature auto-comment map) - a new series is silently uncovered;
  - `scripts/aggregate_check.py -> SELF_CONTAINED` - a row without an `artifact` field needs an entry;
  - `reports/README.md` - a new report needs a line in the index.

FIX 07.11: the first version checked whether the ROWS carry an `artifact` field, which is the opposite of
what SELF_CONTAINED means - an entry there says "this kind is the primary record, it does NOT need the
field". It therefore reported every registered artifact as unregistered. This version parses SELF_CONTAINED
itself and asks the real question: is this KIND listed?

Read-only.
"""
from __future__ import annotations
import ast
import fnmatch
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
POND = ROOT / "morphogenesis" / "experiments" / "E09_pond"
MAP = ROOT / "library" / "result-map.json"
AGG = ROOT / "scripts" / "aggregate_check.py"


def self_contained_kinds() -> set[str]:
    """Parse the SELF_CONTAINED dict out of aggregate_check.py without importing it."""
    src = AGG.read_text(encoding="utf-8")
    start = src.find("SELF_CONTAINED = {")
    if start < 0:
        return set()
    depth, i = 0, src.find("{", start)
    end = i
    while i < len(src):
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
        i += 1
    try:
        node = ast.literal_eval(src[src.find("{", start):end])
        return set(node.keys())
    except Exception:
        return set()


def main(argv=None) -> int:
    limit = int(argv[0]) if argv else 12
    kinds_registered = self_contained_kinds()
    try:
        globs = []
        for c in json.loads(MAP.read_text(encoding="utf-8")).get("claims", []):
            globs.extend(c.get("globs") or [])
    except Exception:
        globs = []

    files = sorted(POND.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]
    print(f"[register] SELF_CONTAINED kinds: {len(kinds_registered)}")
    print(f"[register] checking the {len(files)} newest artifacts\n")
    todo = 0
    for p in files:
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        kind = data.get("kind")
        rel = p.relative_to(ROOT).as_posix()
        rows = data.get("rows") or []
        has_artifact_field = bool(rows) and isinstance(rows[0], dict) and "artifact" in rows[0]
        notes = []
        if kind and not has_artifact_field and kind not in kinds_registered:
            notes.append(f"rows have no `artifact` field AND the kind is not in SELF_CONTAINED "
                         f"-> add \"{kind}\" to scripts/aggregate_check.py")
        covered = any(fnmatch.fnmatch(rel, g) for g in globs)
        if not covered:
            notes.append(f"library/result-map.json: no claim glob covers {p.name}")
        if notes:
            todo += 1
            print(f"{p.name}  (kind={kind})")
            for n in notes:
                print(f"    - {n}")
    print(f"\n[register] {todo} artifact(s) need attention")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
