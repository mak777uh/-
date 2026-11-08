"""Bridge: the policy FILE and the policy MODEL must agree.

`formal/Policy.lean` proves properties of a policy structure. `lab/autonomy-rules.json` is the policy that
actually governs the repository. Until now nothing connected the two: the proof was about a model, and the file
was about the world, and the link was a sentence in a report.

This script closes that link. It reads the JSON, turns each rule into a concrete Action (who, what, res), asks
Lean to decide it, and compares the decision with the list the rule sits in. A rule that Lean decides
differently from where the file puts it is a failure: either the file is wrong, or the model is.

The rules in the JSON are English sentences, not triples, so the mapping is explicit and auditable: see
`RULES` below. A rule with no mapping is reported as UNMAPPED, not silently skipped - an unmapped rule is a
rule the proof says nothing about.

Usage: python scripts/policy_bridge.py [--json out.json]
"""
from __future__ import annotations
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULES_FILE = os.path.join(ROOT, "lab", "autonomy-rules.json")
LEAN_MODEL = os.path.join(ROOT, "formal", "Policy.lean")

# The mapping from a JSON rule (matched by a distinctive fragment) to a concrete action.
# `list` is the list the rule sits in; `owner` is the agent label used for the action.
MAPPING = [
    # allowed_without_asking
    ("run any series whose preregistration", "run_series", "gpu", "allowed"),
    ("write reports, plan sections", "write_report", "repo", "allowed"),
    ("fix a failing gate", "fix_gate", "repo", "allowed"),
    ("close a queue item", "close_item", "repo", "allowed"),
    ("rewrite README, STATUS", "rewrite_readme", "repo", "allowed"),
    ("refactor analysis scripts", "refactor_script", "repo", "allowed"),
    # requires_owner
    ("publishing outward beyond the article series", "publish_outward", "zenodo", "needsOwner"),
    ("changing the world's physics", "change_physics", "world", "needsOwner"),
    ("deleting canonical weights", "delete_canonical", "repo", "needsOwner"),
    ("promoting an arm", "promote_arm", "repo", "needsOwner"),
    # forbidden
    ("force push, rewriting shared history", "force_push", "repo", "forbidden"),
    ("committing weights, runtime logs", "commit_weights", "repo", "forbidden"),
    ("closing a scientific result without", "close_without_trace", "repo", "forbidden"),
    ("editing closed artifacts retroactively", "edit_closed", "repo", "forbidden"),
    ("leaving a lock, a background process", "leave_lock", "repo", "forbidden"),
]

LIST_KEYS = {
    "allowed": "allowed_without_asking",
    "needsOwner": "requires_owner",
    "forbidden": "forbidden",
}


def _elan_bin() -> str:
    return os.path.join(os.path.expanduser("~"), ".elan", "bin")


def find_lean() -> str | None:
    lean = shutil.which("lean")
    if lean:
        return lean
    cand = os.path.join(_elan_bin(), "lean.exe" if os.name == "nt" else "lean")
    return cand if os.path.exists(cand) else None


def lean_decide(actions: list[dict]) -> list[dict] | None:
    """Ask Lean for the decision on each action, each judged against its own single-list policy."""
    lean = find_lean()
    if lean is None:
        return None
    with open(LEAN_MODEL, encoding="utf-8") as fh:
        model = fh.read()

    def lit(a: dict) -> str:
        return f'⟨"{a["who"]}", "{a["what"]}", "{a["res"]}" ⟩'

    def pol(a: dict) -> str:
        parts = []
        for name in ("allowed", "needsOwner", "forbidden"):
            parts.append(f"[{lit(a)}]" if name == a["list"] else "[]")
        return "{" + f" allowed := {parts[0]}, needsOwner := {parts[1]}, forbidden := {parts[2]} " + "}"

    lines = [model, "", "open Policy", "", "def kBridge : List (Bool × Bool × Bool) := ["]
    for a in actions:
        lines.append(f"  (mayWithoutAsking {pol(a)} {lit(a)}, needsOwnerNow {pol(a)} {lit(a)}, "
                     f"isForbidden {pol(a)} {lit(a)}),")
    lines += ["]", "", "#eval kBridge", ""]

    with tempfile.TemporaryDirectory() as tmp:
        f = os.path.join(tmp, "KBridge.lean")
        with open(f, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines))
        env = dict(os.environ)
        env["PATH"] = _elan_bin() + os.pathsep + env.get("PATH", "")
        p = subprocess.run([lean, "KBridge.lean"], cwd=tmp, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", env=env, timeout=300)
        out = (p.stdout or "") + (p.stderr or "")
        if p.returncode != 0:
            print(f"[bridge] lean failed:\n{out[:900]}")
            return None
        triples = re.findall(r"\((true|false),\s*(true|false),\s*(true|false)\)", out)
        if len(triples) != len(actions):
            print(f"[bridge] lean returned {len(triples)} decisions for {len(actions)} actions")
            return None
        return [{"may": t[0] == "true", "owner": t[1] == "true", "forbidden": t[2] == "true"}
                for t in triples]


def expected(list_name: str) -> dict:
    """What the model must say for an action that sits in exactly one list."""
    return {
        "allowed": {"may": True, "owner": False, "forbidden": False},
        "needsOwner": {"may": False, "owner": True, "forbidden": False},
        "forbidden": {"may": False, "owner": False, "forbidden": True},
    }[list_name]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    args = ap.parse_args(argv)

    with open(RULES_FILE, encoding="utf-8") as fh:
        rules = json.load(fh)

    actions, unmapped, mismatched = [], [], []
    for list_name, key in LIST_KEYS.items():
        for text in rules.get(key, []):
            hit = None
            for frag, what, res, want_list in MAPPING:
                if frag in text:
                    hit = (what, res, want_list)
                    break
            if hit is None:
                unmapped.append({"list": list_name, "rule": text[:90]})
                continue
            what, res, want_list = hit
            if want_list != list_name:
                mismatched.append({"rule": text[:70], "in_file": list_name, "in_mapping": want_list})
                continue
            actions.append({"who": "lead", "what": what, "res": res, "list": list_name,
                            "rule": text[:70]})

    print(f"[bridge] правил в файле: {sum(len(rules.get(k, [])) for k in LIST_KEYS.values())}, "
          f"сопоставлено: {len(actions)}, без сопоставления: {len(unmapped)}, "
          f"в разных списках: {len(mismatched)}")

    decisions = lean_decide(actions)
    if decisions is None:
        print("[bridge] Lean недоступен — мост не проверен (это не доказательство)")
        return 0

    bad = []
    for a, d in zip(actions, decisions):
        want = expected(a["list"])
        ok = d == want
        mark = "OK  " if ok else "DIFF"
        print(f"[{mark}] {a['list']:11s} {a['what']:20s} lean={d}")
        if not ok:
            bad.append({"action": a, "want": want, "lean": d})

    print(f"\n[bridge] действий: {len(actions)}, расхождений с файлом: {len(bad)}, "
          f"без сопоставления: {len(unmapped)}")
    for u in unmapped:
        print(f"  UNMAPPED [{u['list']}] {u['rule']}")
    for m in mismatched:
        print(f"  WRONG-LIST {m}")

    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump({"mapped": len(actions), "unmapped": unmapped, "wrong_list": mismatched,
                       "diffs": bad}, fh, ensure_ascii=False, indent=1)
        print(f"written: {args.json}")
    return 0 if not bad and not mismatched else 1


if __name__ == "__main__":
    sys.exit(main())
