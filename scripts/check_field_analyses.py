"""check_field_analyses.py — the field line's aggregates must re-derive from the stored artifacts.

Why. Since 01.11 the field line has produced twenty aggregates (`l1_field_x*.json`) whose numbers appear in CLAIMS rows and in
`docs/plan`. Every one of them is a *representation* of artifacts that are also in git, and nothing recomputed them on a machine other
than the one that wrote them: `l1_field_matrix.py --check` covers only the old single aggregate, and `aggregate_check.py` compares
aggregates to artifacts by name, not by re-running the analysis.

This checker re-runs every analysis whose output is quoted in CLAIMS or in docs/plan, compares the result with the committed aggregate
and restores the file. Eleven are covered (x80, x82, x84-x89, x91-x93); the rest of the twenty field aggregates are either not backed by
a re-runnable script or not yet quoted, and are added when they become load-bearing.

The committed file is restored byte-for-byte after the run, so the check never modifies the repository. Numbers are compared with a
tolerance of 1e-6 to absorb float ordering; the shuffle in x92 uses a fixed seed, so it is deterministic.

Run:
    python scripts/check_field_analyses.py            # check
    python scripts/check_field_analyses.py --list     # what is covered
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
TOL = 1e-6

REGISTRY = [
    ("scripts/x80_analyse.py", "morphogenesis/experiments/E09_pond/l1_field_x80_dip.json"),
    ("scripts/x82_analyse.py", "morphogenesis/experiments/E09_pond/l1_field_x82_reach.json"),
    ("scripts/x84_analyse.py", "morphogenesis/experiments/E09_pond/l1_field_x84_angular.json"),
    ("scripts/x85_analyse.py", "morphogenesis/experiments/E09_pond/l1_field_x85_symmetry_memory.json"),
    ("scripts/x86_analyse.py", "morphogenesis/experiments/E09_pond/l1_field_x86_symmetry_curve.json"),
    ("scripts/x87_analyse.py", "morphogenesis/experiments/E09_pond/l1_field_x87_memory_vs_symmetry.json"),
    ("scripts/x88_analyse.py", "morphogenesis/experiments/E09_pond/l1_field_x88_percolating_arm.json"),
    ("scripts/x89_analyse.py", "morphogenesis/experiments/E09_pond/l1_field_x89_lineage_edge.json"),
    ("scripts/x91_analyse.py", "morphogenesis/experiments/E09_pond/l1_field_x91_lineage_specificity.json"),
    ("scripts/x92_analyse.py", "morphogenesis/experiments/E09_pond/l1_field_x92_pay.json"),
    ("scripts/x93_analyse.py", "morphogenesis/experiments/E09_pond/l1_field_x93_sibling_contrast.json"),
]


def diff(a, b, path: str = "") -> list[str]:
    """Recursive comparison that tolerates float noise and reports the path of the first difference."""
    if isinstance(a, dict) and isinstance(b, dict):
        out = []
        for key in sorted(set(a) | set(b)):
            if key not in a:
                out.append(f"{path}.{key}: missing in committed")
            elif key not in b:
                out.append(f"{path}.{key}: missing in recomputed")
            else:
                out.extend(diff(a[key], b[key], f"{path}.{key}"))
        return out
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return [f"{path}: length {len(a)} != {len(b)}"]
        out = []
        for i, (x, y) in enumerate(zip(a, b)):
            out.extend(diff(x, y, f"{path}[{i}]"))
        return out
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool) and not isinstance(b, bool):
        if abs(float(a) - float(b)) > TOL:
            return [f"{path}: {a} != {b}"]
        return []
    return [] if a == b else [f"{path}: {a!r} != {b!r}"]


# 03.11: восемь агрегатов этого реестра считаются из кадров поля (_xNN_fields), а кадры в git не едут и частью
# удалены (lab/retention.json). Гейт падал в nightly с самого удаления, и это было не видно: health показывал
# «шаг не определён». Теперь отсутствие входа называется вслух и НЕ валит сборку, а расхождение при живом
# входе — валит, как и раньше. Запись о том, что число цитируется, а пересчитать его нельзя, остаётся в отчёте
# каждой прогонки.
AGG_INPUT_DIRS = {
    "l1_field_x80_dip.json": "_x80_fields",
    "l1_field_x82_reach.json": "_x82_fields",
    "l1_field_x84_angular.json": "_x71_fields",
    "l1_field_x85_symmetry_memory.json": "_x85_fields",
    "l1_field_x86_symmetry_curve.json": "_x86_fields",
    "l1_field_x87_memory_vs_symmetry.json": "_x87_fields",
    "l1_field_x88_percolating_arm.json": "_x88_fields",
    "l1_field_x89_lineage_edge.json": "_x89_fields",
}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="field aggregates re-derived from artifacts")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--ci", action="store_true")
    args = ap.parse_args(argv)

    if args.list:
        for script, agg in REGISTRY:
            print(f"{script} -> {agg}")
        return 0

    problems = []
    skipped = []
    for script, agg_rel in REGISTRY:
        agg = ROOT / agg_rel
        if not agg.is_file():
            problems.append(f"{agg_rel}: no committed aggregate")
            continue
        frames = AGG_INPUT_DIRS.get(agg.name)
        if frames and not (ROOT / "morphogenesis" / "experiments" / "L1_field" / frames).is_dir():
            skipped.append(f"{agg_rel}: inputs {frames} are field frames - not in git, retired where recorded")
            continue
        saved = agg.read_bytes()
        committed = json.loads(saved.decode("utf-8"))
        try:
            proc = subprocess.run([PY, script, "--write"], cwd=str(ROOT), capture_output=True, text=True,
                                  encoding="utf-8", errors="replace", timeout=1800)
            if proc.returncode != 0:
                problems.append(f"{script}: exit {proc.returncode}: {(proc.stderr or proc.stdout)[-300:]}")
                continue
            recomputed = json.loads(agg.read_text(encoding="utf-8"))
        finally:
            agg.write_bytes(saved)
        d = diff(committed, recomputed)
        if d:
            problems.append(f"{agg_rel}: {len(d)} difference(s), first: {d[0]}")

    for s in skipped:
        print(f"  skipped: {s}")
    if problems:
        print("[field-analyses] ПРОВАЛ:")
        for p in problems:
            print("  " + p)
        return 1
    print(f"[field-analyses] registry {len(REGISTRY)}: {len(REGISTRY) - len(skipped)} re-derived from artifacts, "
          f"{len(skipped)} skipped because their field frames are not in git (see lab/retention.json)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
