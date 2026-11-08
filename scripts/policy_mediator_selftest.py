"""Self-test for the live mediator: does the cross-check actually happen, and does it actually refuse?

A cross-check that never fires is decoration. This script plants a disagreement and checks that `decide`
raises. It also checks that a normal decision reports `source = python+rust` and `agree = True`, so we know the
Rust side really ran rather than being silently skipped.

Usage: python scripts/policy_mediator_selftest.py
"""
from __future__ import annotations
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import policy_mediator as pm  # noqa: E402

FAILS = 0


def check(name: str, cond: bool, detail: str = "") -> None:
    global FAILS
    print(f"{'OK  ' if cond else 'FAIL'} {name}{(' — ' + detail) if detail and not cond else ''}")
    if not cond:
        FAILS += 1


def main() -> int:
    action = {"who": "lead", "what": "commit", "res": "repo"}
    policy = {"allowed": [action], "needsOwner": [], "forbidden": []}

    d = pm.decide(action, policy)
    check("a normal decision is allowed", d["may"] is True, str(d))
    check("the Rust side ran", d["source"] == "python+rust", f"source={d['source']}")
    check("the two agree", d["agree"] is True, str(d))

    # plant a disagreement: make the Python rule say the opposite of the Rust rule for the same input by
    # monkeypatching the Python side only
    original = pm.python_decide

    def lying(action, policy):
        r = original(action, policy)
        r["may"] = not r["may"]
        return r

    pm.python_decide = lying
    raised = False
    try:
        pm.decide(action, policy)
    except RuntimeError as exc:
        raised = "disagreement" in str(exc).lower()
    finally:
        pm.python_decide = original
    check("a planted disagreement is refused", raised)

    # forbid beats allow, live
    both = {"allowed": [action], "needsOwner": [], "forbidden": [action]}
    d2 = pm.decide(action, both)
    check("forbid beats allow, live", d2["may"] is False and d2["forbidden"] is True, str(d2))

    # cross-check off reports python only
    d3 = pm.decide(action, policy, cross_check=False)
    check("cross-check off says so", d3["source"] == "python" and d3["agree"] is None, str(d3))

    print(f"\n[mediator-selftest] провалов: {FAILS} из 5")
    return 0 if FAILS == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
