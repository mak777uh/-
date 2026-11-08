"""Gate: every run manifest must carry a policy_gate record.

Why. The wrapper `lab.py run` asks the policy mediator before taking the lock and writes the decision into the
manifest as `policy_gate`. A manifest WITHOUT that field is therefore evidence that the run bypassed the
wrapper - which is exactly the closure question level C asks: does anything pass around the mediator?

This gate is the mechanism that answers it. It is small on purpose: it reads manifests and checks one field.

Usage:
  python scripts/check_run_manifest_gate.py [root]
"""
from __future__ import annotations
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# the date the wrapper began writing policy_gate into the manifest
CUTOFF = "2026-11-08"


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    root = argv[0] if argv else ROOT
    runs = os.path.join(root, "lab", "runs")
    if not os.path.isdir(runs):
        print("[run-gate] нет lab/runs")
        return 0

    problems: list[str] = []
    checked = 0
    for name in sorted(os.listdir(runs)):
        if not name.endswith(".json"):
            continue
        path = os.path.join(runs, name)
        try:
            with open(path, encoding="utf-8") as fh:
                m = json.load(fh)
        except Exception as exc:  # noqa: BLE001
            problems.append(f"{name}: не читается ({exc})")
            continue
        # grandfather: the wrapper started recording policy_gate on 2026-11-08. Every run before that date
        # predates the gate and is history (AGENTS.md: old manifests are not rewritten). The gate governs what
        # runs NEXT, which is the only thing it can govern.
        started = str(m.get("started_at") or "")
        if started < CUTOFF:
            continue
        checked += 1
        if "policy_gate" not in m:
            problems.append(f"{name}: прогон без policy_gate — запущен мимо обёртки")

    if problems:
        for p in problems:
            print(f"  ПРОВАЛ: {p}")
        print(f"[run-gate] проблем: {len(problems)} из {checked} манифестов")
        return 1
    print(f"[run-gate] ok: {checked} манифестов, у всех есть policy_gate")
    return 0


if __name__ == "__main__":
    sys.exit(main())
