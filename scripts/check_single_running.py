"""Gate: at most one queue item may be marked running.

Why. The queue is the GPU lane. Two items marked `running` means two series believe they own the same lane,
and the lock in `lab/locks/` protects only the experiment, not the lane. This is the level-C question in its
most concrete form: does anything pass around the lane rule?

Usage:
  python scripts/check_single_running.py [root]
"""
from __future__ import annotations
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    root = argv[0] if argv else ROOT
    qp = os.path.join(root, "lab", "queue.json")
    if not os.path.exists(qp):
        print("[single-running] нет lab/queue.json")
        return 0
    with open(qp, encoding="utf-8") as fh:
        q = json.load(fh)
    items = q.get("items") or []
    running = [it.get("id") for it in items if it.get("status") == "running"]

    if len(running) > 1:
        print(f"  ПРОВАЛ: {len(running)} пунктов в статусе running: {running}")
        print(f"[single-running] проблем: 1")
        return 1
    print(f"[single-running] ok: running пунктов {len(running)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
