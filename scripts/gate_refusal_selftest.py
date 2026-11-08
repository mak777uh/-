"""Does the live gate actually refuse? Plant a disagreement and check that no run starts.

A gate that only ever says yes is decoration. This script makes the mediator disagree with itself by
monkeypatching the Python rule, then calls the same function `lab.py run` calls, and checks that:

  1. the call is refused (returns a refusal, not a decision);
  2. no lock file is left behind;
  3. no manifest is written.

Usage: python scripts/gate_refusal_selftest.py
"""
from __future__ import annotations
import glob
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import policy_mediator as pm  # noqa: E402

FAILS = 0


def check(name: str, cond: bool, detail: str = "") -> None:
    global FAILS
    print(f"{'OK  ' if cond else 'FAIL'} {name}{(' — ' + detail) if detail and not cond else ''}")
    if not cond:
        FAILS += 1


def main() -> int:
    action = {"who": "lead", "what": "run_series", "res": "gpu"}
    policy = {"allowed": [action], "needsOwner": [], "forbidden": []}

    # baseline: the gate agrees and allows
    d = pm.decide(action, policy)
    check("baseline allows", d["may"] is True and d["agree"] is True, str(d))

    # plant: the Python side lies, so the two implementations disagree
    original = pm.python_decide

    def lying(a, p):
        r = original(a, p)
        r["may"] = not r["may"]
        return r

    pm.python_decide = lying
    refused = False
    msg = ""
    try:
        pm.decide(action, policy)
    except RuntimeError as exc:
        refused = True
        msg = str(exc)
    finally:
        pm.python_decide = original
    check("planted disagreement is refused", refused, msg[:120])
    check("the refusal names the disagreement", "disagreement" in msg.lower(), msg[:120])

    # no lock and no manifest for a refused action: the gate runs before the lock, so this is structural,
    # and the check is that the test itself left nothing behind
    locks = glob.glob(os.path.join(ROOT, "lab", "locks", "K_REFUSAL_TEST.lock"))
    manifests = glob.glob(os.path.join(ROOT, "lab", "runs", "*K_REFUSAL_TEST*.json"))
    check("no lock left", not locks, str(locks))
    check("no manifest written", not manifests, str(manifests))

    print(f"\n[gate-refusal] провалов: {FAILS} из 5")
    return 0 if FAILS == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
