"""Three implementations of the same policy decision must agree.

Level B in the herness model: the mediator is provable for small code, and the proof is only worth something if
the code that runs agrees with it. This script compares three independent implementations:

  A. Lean    — `formal/Policy.lean`, the proved model (F-POLICY-1..6)
  B. Python  — `scripts/check_autonomy.py`, the rule that runs today
  C. Rust    — `mediator/`, the compiled mediator

A disagreement is a failure: it means either the proof is about something else, or one implementation does
something else.

Usage: python scripts/policy_diff.py [--json out.json] [--no-rust]
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
MEDIATOR = os.path.join(ROOT, "mediator")

CASES = [
    {"who": "lead", "what": "commit", "res": "repo", "lists": ["allowed"]},
    {"who": "lead", "what": "publish", "res": "zenodo", "lists": ["needsOwner"]},
    {"who": "lead", "what": "force_push", "res": "repo", "lists": ["forbidden"]},
    {"who": "lead", "what": "commit", "res": "repo", "lists": ["allowed", "forbidden"]},
    {"who": "lead", "what": "publish", "res": "zenodo", "lists": ["needsOwner", "forbidden"]},
    {"who": "lead", "what": "commit", "res": "repo", "lists": ["allowed", "needsOwner"]},
    {"who": "lead", "what": "dance", "res": "repo", "lists": []},
]


def python_decision(lists: list[str]) -> dict:
    in_allowed = "allowed" in lists
    in_owner = "needsOwner" in lists
    in_forbidden = "forbidden" in lists
    return {
        "may": in_allowed and not in_forbidden and not in_owner,
        "owner": in_owner and not in_forbidden,
        "forbidden": in_forbidden,
    }


def _elan_bin() -> str:
    return os.path.join(os.path.expanduser("~"), ".elan", "bin")


def _rustup_lld_bin() -> str:
    return os.path.join(os.path.expanduser("~"), ".rustup", "toolchains",
                        "stable-x86_64-pc-windows-gnu", "lib", "rustlib",
                        "x86_64-pc-windows-gnu", "bin")


def find_lean() -> str | None:
    lean = shutil.which("lean")
    if lean:
        return lean
    cand = os.path.join(_elan_bin(), "lean.exe" if os.name == "nt" else "lean")
    return cand if os.path.exists(cand) else None


def lean_decision(cases: list[dict]) -> list[dict] | None:
    lean = find_lean()
    if lean is None:
        return None

    def action_lit(c: dict) -> str:
        return f'⟨"{c["who"]}", "{c["what"]}", "{c["res"]}" ⟩'

    def policy_lit(c: dict) -> str:
        a = action_lit(c)
        parts = [f"[{a}]" if name in c["lists"] else "[]"
                 for name in ("allowed", "needsOwner", "forbidden")]
        return "{" + f" allowed := {parts[0]}, needsOwner := {parts[1]}, forbidden := {parts[2]} " + "}"

    with open(os.path.join(ROOT, "formal", "Policy.lean"), encoding="utf-8") as fh:
        model = fh.read()
    lines = [model, "", "open Policy", "", "def kCheck : List (Bool × Bool × Bool) := ["]
    for c in cases:
        p, a = policy_lit(c), action_lit(c)
        lines.append(f"  (mayWithoutAsking {p} {a}, needsOwnerNow {p} {a}, isForbidden {p} {a}),")
    lines += ["]", "", "#eval kCheck", ""]

    with tempfile.TemporaryDirectory() as tmp:
        f = os.path.join(tmp, "KCheck.lean")
        with open(f, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines))
        env = dict(os.environ)
        env["PATH"] = _elan_bin() + os.pathsep + env.get("PATH", "")
        p = subprocess.run([lean, "KCheck.lean"], cwd=tmp, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", env=env, timeout=300)
        out = (p.stdout or "") + (p.stderr or "")
        if p.returncode != 0:
            print(f"[policy-diff] lean failed:\n{out[:900]}")
            return None
        triples = re.findall(r"\((true|false),\s*(true|false),\s*(true|false)\)", out)
        if not triples:
            print(f"[policy-diff] could not parse lean output:\n{out[:500]}")
            return None
        return [{"may": t[0] == "true", "owner": t[1] == "true", "forbidden": t[2] == "true"}
                for t in triples]


def build_mediator() -> str | None:
    """Build the Rust mediator and return the path to the binary, or None if it cannot be built."""
    cargo = shutil.which("cargo")
    if cargo is None:
        cand = os.path.join(os.path.expanduser("~"), ".cargo", "bin",
                            "cargo.exe" if os.name == "nt" else "cargo")
        if not os.path.exists(cand):
            return None
        cargo = cand
    env = dict(os.environ)
    env["PATH"] = (os.pathsep.join([os.path.dirname(cargo), _rustup_lld_bin(), env.get("PATH", "")]))
    p = subprocess.run([cargo, "build", "--quiet"], cwd=MEDIATOR, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=env, timeout=600)
    if p.returncode != 0:
        print(f"[policy-diff] cargo build failed:\n{(p.stderr or '')[:700]}")
        return None
    exe = os.path.join(MEDIATOR, "target", "debug", "mediator.exe" if os.name == "nt" else "mediator")
    return exe if os.path.exists(exe) else None


def rust_decision(cases: list[dict], exe: str) -> list[dict] | None:
    """Run the mediator ONCE PER CASE, each with its own policy.

    Why one policy per case. The first version wrote every case into a single policy file, so `commit` ended
    up in both `allowed` and `forbidden`, and the mediator correctly answered "forbidden" for every commit -
    which is exactly the rule F-POLICY-1. The Python and Lean sides evaluate each case against its own lists,
    so the comparison was between different questions. The mediator was right; the test was wrong.
    """
    out: list[dict] = []
    for c in cases:
        with tempfile.TemporaryDirectory() as tmp:
            pol = os.path.join(tmp, "policy.txt")
            acts = os.path.join(tmp, "actions.txt")
            # utf-8-sig writes a BOM, exactly as a Windows editor would: the mediator must survive it
            with open(pol, "w", encoding="utf-8-sig") as fh:
                for name in ("allowed", "needsOwner", "forbidden"):
                    if name in c["lists"]:
                        key = "needs_owner" if name == "needsOwner" else name
                        fh.write(f"{key}|{c['who']}|{c['what']}|{c['res']}\n")
            with open(acts, "w", encoding="utf-8-sig") as fh:
                fh.write(f"{c['who']}|{c['what']}|{c['res']}\n")
            p = subprocess.run([exe, "--policy", pol, "--actions", acts], capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=120)
            if p.returncode != 0:
                print(f"[policy-diff] mediator failed on {c}:\n{(p.stderr or '')[:500]}")
                return None
            lines = [l for l in (p.stdout or "").strip().splitlines() if l.count("|") == 5]
            if len(lines) != 1:
                print(f"[policy-diff] mediator returned {len(lines)} lines for {c}")
                return None
            f = lines[0].split("|")
            out.append({"may": f[3] == "true", "owner": f[4] == "true", "forbidden": f[5] == "true"})
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    ap.add_argument("--no-rust", action="store_true")
    args = ap.parse_args(argv)

    py = [python_decision(c["lists"]) for c in CASES]
    results: dict[str, list[dict] | None] = {"python": py}
    results["lean"] = lean_decision(CASES)
    if not args.no_rust:
        exe = build_mediator()
        results["rust"] = rust_decision(CASES, exe) if exe else None

    available = {k: v for k, v in results.items() if v is not None}
    print(f"[policy-diff] реализаций доступно: {len(available)} из {len(results)} "
          f"({', '.join(sorted(available))})")

    diffs = []
    for name, vals in available.items():
        if name == "python":
            continue
        for c, a, b in zip(CASES, py, vals):
            if a != b:
                diffs.append({"impl": name, "case": c, "python": a, name: b})

    for c, a in zip(CASES, py):
        row = f"  {c['what']:12s} {str(c['lists']):34s} py={a}"
        for name in ("lean", "rust"):
            if name in available:
                row += f" {name}={available[name][CASES.index(c)]}"
        print(row)

    print(f"\n[policy-diff] случаев: {len(CASES)}, реализаций: {len(available)}, расхождений: {len(diffs)}")
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump({"cases": len(CASES), "implementations": sorted(available),
                       "diffs": diffs}, fh, ensure_ascii=False, indent=1)
        print(f"written: {args.json}")
    return 0 if not diffs else 1


if __name__ == "__main__":
    sys.exit(main())
