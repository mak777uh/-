"""Which experiment artifacts are NOT covered by any claim in library/result-map.json?

Why: the auto-literature tool only sees artifacts that match a claim's globs. When a new series
appears and nobody adds it to the map, the result silently gets no literature search — the same
"silent hole" that hid the whole pond line from the library for a day.

This check lists artifacts that (a) look like run artifacts (have a "rows" or "summary" key) and
(b) match no claim glob. Exit code 1 if any are found, so it can be used as a gate.

    python scripts/check_result_map_coverage.py
    python scripts/check_result_map_coverage.py --limit 20
"""
from __future__ import annotations
import argparse
import fnmatch
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
MAP = REPO / "library" / "result-map.json"
POND = REPO / "morphogenesis" / "experiments" / "E09_pond"
SKIP_NAMES = {"p0_cal1.json", "p0_cal2.json", "p0_cal3.json"}  # ad-hoc calibration probes


def claim_globs() -> list[str]:
    try:
        data = json.loads(MAP.read_text(encoding="utf-8"))
    except Exception:
        return []
    out = []
    for c in data.get("claims", []):
        out.extend(c.get("globs") or [])
    return out


def is_run_artifact(path: pathlib.Path) -> bool:
    if path.name.endswith("_matrix.json"):
        return True
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return False
    return isinstance(data, dict) and ("rows" in data or "summary" in data)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="artifacts not covered by any claim")
    ap.add_argument("--limit", type=int, default=15, help="сколько примеров печатать")
    args = ap.parse_args(argv)

    globs = claim_globs()
    if not globs:
        print("[coverage-map] нет заявок в result-map.json — проверять нечего")
        return 0

    uncovered = []
    total = 0
    for path in sorted(POND.glob("*.json")):
        if path.name in SKIP_NAMES or not is_run_artifact(path):
            continue
        total += 1
        rel = path.relative_to(REPO).as_posix()
        if any(fnmatch.fnmatch(rel, g) for g in globs):
            continue
        uncovered.append(rel)

    print(f"[coverage-map] артефактов прогонов: {total}; без заявки: {len(uncovered)}")
    for rel in uncovered[: args.limit]:
        print(f"  БЕЗ ЗАЯВКИ {rel}")
    if len(uncovered) > args.limit:
        print(f"  ... и ещё {len(uncovered) - args.limit}")
    return 0 if not uncovered else 1


if __name__ == "__main__":
    sys.exit(main())
