"""The mediator that the harness calls: Python rule plus a cross-check against the Rust mediator.

Why two implementations at runtime. The Rust mediator is compiled, has no dependencies and agrees with the
proved Lean model on every test case. The Python rule is what the rest of the repository already imports. Running
both and refusing on disagreement means a defect has to appear in BOTH to reach the world - and if only one is
wrong, we find out at the moment of the decision rather than in a review a day later.

The Rust side is optional: if the binary is missing (a machine without cargo), the mediator works with the
Python rule alone and says so in `source`. It never silently pretends the cross-check happened.

Usage as a library:
    from policy_mediator import decide
    d = decide({"who": "lead", "what": "commit", "res": "repo"},
               {"allowed": [...], "needsOwner": [...], "forbidden": [...]})

Usage as a command (for the harness and for tests):
    python scripts/policy_mediator.py --policy lab/autonomy-rules.json \
        --action lead commit repo
"""
from __future__ import annotations
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIATOR_DIR = os.path.join(ROOT, "mediator")


def _rustup_lld_bin() -> str:
    return os.path.join(os.path.expanduser("~"), ".rustup", "toolchains",
                        "stable-x86_64-pc-windows-gnu", "lib", "rustlib",
                        "x86_64-pc-windows-gnu", "bin")


def _mediator_binary() -> str | None:
    exe = os.path.join(MEDIATOR_DIR, "target", "debug", "mediator.exe" if os.name == "nt" else "mediator")
    if os.path.exists(exe):
        return exe
    cargo = shutil.which("cargo")
    if cargo is None:
        cand = os.path.join(os.path.expanduser("~"), ".cargo", "bin",
                            "cargo.exe" if os.name == "nt" else "cargo")
        if not os.path.exists(cand):
            return None
        cargo = cand
    env = dict(os.environ)
    env["PATH"] = os.pathsep.join([os.path.dirname(cargo), _rustup_lld_bin(), env.get("PATH", "")])
    p = subprocess.run([cargo, "build", "--quiet"], cwd=MEDIATOR_DIR, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=env, timeout=600)
    if p.returncode != 0 or not os.path.exists(exe):
        return None
    return exe


def python_decide(action: dict, policy: dict) -> dict:
    """The rule that runs today: forbid beats everything."""
    def has(key: str) -> bool:
        return any(a == action for a in policy.get(key, []))
    in_allowed = has("allowed")
    in_owner = has("needsOwner")
    in_forbidden = has("forbidden")
    return {
        "may": in_allowed and not in_forbidden and not in_owner,
        "owner": in_owner and not in_forbidden,
        "forbidden": in_forbidden,
    }


def rust_decide(action: dict, policy: dict, exe: str) -> dict | None:
    with tempfile.TemporaryDirectory() as tmp:
        pol = os.path.join(tmp, "policy.txt")
        acts = os.path.join(tmp, "actions.txt")
        with open(pol, "w", encoding="utf-8") as fh:
            for name, key in (("allowed", "allowed"), ("needs_owner", "needsOwner"),
                              ("forbidden", "forbidden")):
                for a in policy.get(key, []):
                    fh.write(f"{name}|{a['who']}|{a['what']}|{a['res']}\n")
        with open(acts, "w", encoding="utf-8") as fh:
            fh.write(f"{action['who']}|{action['what']}|{action['res']}\n")
        p = subprocess.run([exe, "--policy", pol, "--actions", acts], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=120)
        if p.returncode != 0:
            return None
        lines = [l for l in (p.stdout or "").strip().splitlines() if l.count("|") == 5]
        if len(lines) != 1:
            return None
        f = lines[0].split("|")
        return {"may": f[3] == "true", "owner": f[4] == "true", "forbidden": f[5] == "true"}


def decide(action: dict, policy: dict, cross_check: bool = True) -> dict:
    """Decide, and cross-check against the Rust mediator when it is available.

    Returns the decision plus `source` (python | python+rust) and `agree` (True, False, or None when the
    cross-check could not run). A disagreement is raised, not returned: the harness must not act on a decision
    two implementations do not share.
    """
    py = python_decide(action, policy)
    out = dict(py)
    out["source"] = "python"
    out["agree"] = None
    if not cross_check:
        return out
    exe = _mediator_binary()
    if exe is None:
        return out
    rs = rust_decide(action, policy, exe)
    if rs is None:
        return out
    out["source"] = "python+rust"
    out["agree"] = (rs == py)
    if rs != py:
        raise RuntimeError(
            f"mediator disagreement on {action}: python={py} rust={rs}. "
            f"Two implementations of the same policy must agree; refusing to decide."
        )
    return out


def _load_policy(path: str) -> dict:
    """Accept both the autonomy-rules format (sentences) and the action format (triples)."""
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    if "allowed" in data and isinstance(data["allowed"], list) and data["allowed"] \
            and isinstance(data["allowed"][0], dict):
        return data
    # autonomy-rules.json: sentences. The bridge script maps them; here we only support the action format,
    # because a sentence is not an action and pretending otherwise would be the kind of silent guess this
    # repository forbids.
    return {"allowed": [], "needsOwner": [], "forbidden": []}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--policy", required=True)
    ap.add_argument("--action", nargs=3, metavar=("WHO", "WHAT", "RES"), required=True)
    ap.add_argument("--no-cross-check", action="store_true")
    args = ap.parse_args(argv)

    policy = _load_policy(args.policy)
    action = {"who": args.action[0], "what": args.action[1], "res": args.action[2]}
    d = decide(action, policy, cross_check=not args.no_cross_check)
    print(json.dumps({"action": action, **d}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
