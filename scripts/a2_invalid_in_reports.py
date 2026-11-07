"""A2: did any INVALID run reach a report?

A1 found 27 runs out of 1141 whose R1 check failed (mean deaths >= 10 and mean living >= 10). Those
runs must not support any published number. This script:

  1. lists the artifacts and arms that contain R1 failures;
  2. greps the reports/ directory for the names of those artifacts;
  3. reports which reports mention an artifact that carries an invalid run.

Read-only.
"""
from __future__ import annotations
import json
import pathlib
import re
import sys
from collections import defaultdict

REPO = pathlib.Path(__file__).resolve().parents[1]
POND = REPO / "morphogenesis" / "experiments" / "E09_pond"
REPORTS = REPO / "reports"


def main(argv=None) -> int:
    bad = defaultdict(list)   # artifact -> list of (arm, seed, regime)
    for path in sorted(POND.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        for r in data.get("rows") or []:
            if isinstance(r, dict) and r.get("R1") is False:
                bad[path.name].append((r.get("arm"), r.get("seed"), r.get("regime")))

    print(f"[a2] artifacts with R1 failures: {len(bad)}")
    for name, items in sorted(bad.items()):
        print(f"   {name}: {len(items)} runs, e.g. {items[:3]}")

    # which reports mention those artifacts?
    report_text = {}
    for p in sorted(REPORTS.glob("*.md")):
        report_text[p.name] = p.read_text(encoding="utf-8", errors="ignore")

    hits = defaultdict(list)
    for name in bad:
        stem = name.replace(".json", "")
        for rname, text in report_text.items():
            if stem in text:
                hits[name].append(rname)

    print(f"\n[a2] artifacts with R1 failures that are MENTIONED in a report: {len(hits)}")
    for name, reports in sorted(hits.items()):
        print(f"   {name} -> {reports}")

    out = {
        "kind": "a2_invalid_in_reports",
        "artifacts_with_r1_failures": {k: len(v) for k, v in bad.items()},
        "mentioned_in_reports": {k: v for k, v in hits.items()},
    }
    with open(POND / "a2_invalid_in_reports.json", "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(f"\n[a2] written {POND / 'a2_invalid_in_reports.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
