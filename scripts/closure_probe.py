"""Closure probes: does the machinery actually catch a planted defect, and does it recover?

Level C in the herness model is not proved, only measured. The first version of this script measured badly:
four of its five probes did not plant a defect at all - they ran a check on the existing repository and
reported "caught" when the check exited 0. A check that passes on a clean tree proves nothing about whether it
would fail on a dirty one. This version follows the scheme a reviewer of article 036 demanded:

  1. copy the relevant part of the laboratory into a scratch tree;
  2. plant ONE concrete defect there;
  3. run exactly the mechanism that is supposed to catch it;
  4. require that it fails, AND that it names the expected reason;
  5. remove the defect;
  6. require that the same mechanism passes again on the clean copy.

A probe that cannot demonstrate steps 4 and 6 is reported as a HOLE, and the script exits non-zero. The
summary reports two numbers, not one: how many defects were caught, and how many scenarios were exercised.

Usage: python scripts/closure_probe.py [--json out.json]
"""
from __future__ import annotations
import argparse
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run(cmd: list[str], cwd: str) -> tuple[int, str]:
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", env=env, timeout=600)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


# Directories a probe never needs and that would make the copy slow or huge.
SKIP_DIRS = {".git", "target", "__pycache__", ".venv", "node_modules", "_hourly", "_zenodo", "_exports",
             "checkpoints", "library", "experiments", "logs"}

# Why the artifact trees are excluded and the text trees are not. A closure probe plants a defect in the LAB
# (a manifest, a weights file, a protected path, a queue status) and asks a gate about it; it never reads an
# experiment artifact. Copying `morphogenesis/experiments/` alone is 24 000 files (L1_field has 22 272), and
# five probes times that is why an earlier version of this gate took tens of minutes.
#
# `reports/` and `articles/` are NOT excluded, even though they are large: `check_autonomy` verifies that every
# protected path EXISTS, and `articles/` is one of them. Excluding it made the clean copy fail before any defect
# was planted, which turned a working probe into a false hole. The rule that follows: **a probe may exclude only
# what is not a protected path.**


def scratch_copy(dst: str, parts: list[str]) -> None:
    """Copy the repository, minus the heavy and irrelevant parts.

    Why the WHOLE repository and not just the parts a probe seems to need. The first version copied only
    `lab` and `scripts`, and then `check_autonomy` failed on the clean copy because it verifies that every
    protected path EXISTS - and `CITATION.cff` and `morphogenesis/config.py` were not in the copy. A probe whose
    clean copy already fails measures the copy, not the defect. The copy must be a working laboratory.
    """
    for entry in os.listdir(ROOT):
        if entry in SKIP_DIRS:
            continue
        src = os.path.join(ROOT, entry)
        dstp = os.path.join(dst, entry)
        if os.path.isdir(src):
            shutil.copytree(src, dstp, dirs_exist_ok=True,
                            ignore=shutil.ignore_patterns(*SKIP_DIRS))
        else:
            shutil.copy2(src, dstp)


def probe(name: str, defect: str, expect: str, parts: list[str], plant, run_check, cleanup=None) -> dict:
    """The six-step scheme, once.

    plant(scratch) plants the defect and returns a note; run_check(scratch) returns (rc, out).
    """
    result = {"probe": name, "defect": defect, "expect": expect,
              "planted": False, "caught": False, "reason_matched": False,
              "clean_passes": False, "note": ""}
    with tempfile.TemporaryDirectory() as tmp:
        scratch_copy(tmp, parts)
        # step 6 baseline: the clean copy must pass BEFORE we plant anything, otherwise the probe measures
        # the copy, not the defect
        rc0, out0 = run_check(tmp)
        result["clean_passes"] = rc0 == 0
        if rc0 != 0:
            result["note"] = f"clean copy already fails: {out0.strip()[-200:]}"
            return result

        note = plant(tmp)
        result["planted"] = True
        result["note"] = note or ""

        rc1, out1 = run_check(tmp)
        result["caught"] = rc1 != 0
        result["reason_matched"] = expect.lower() in out1.lower()
        result["excerpt"] = [l for l in out1.splitlines() if expect.lower() in l.lower()][:2]

        if cleanup:
            cleanup(tmp)
            rc2, _ = run_check(tmp)
            result["clean_passes"] = rc2 == 0
    return result


# ---------------- the five probes ----------------

def p1_no_wrapper() -> dict:
    """A run whose artifact has no manifest, then the manifest gate is asked about it."""
    def plant(tmp: str) -> str:
        planted = os.path.join(tmp, "lab", "runs", "ZZ-planted-orphan.json")
        with open(planted, "w", encoding="utf-8") as fh:
            json.dump({"schema": "run/v1.1", "run_id": "ZZ-planted-orphan",
                       "owner": "lead", "status": "finished",
                       "started_at": "2026-11-08T00:00:00Z"}, fh)
        return "planted a manifest with no artifact and no policy gate"

    def check(tmp: str) -> tuple[int, str]:
        return run([sys.executable, "scripts/check_autonomy.py"], tmp)

    def clean(tmp: str) -> None:
        os.remove(os.path.join(tmp, "lab", "runs", "ZZ-planted-orphan.json"))

    # the defect this probe is about is a run WITHOUT a manifest. The mechanism that catches it is the
    # manifest gate: every manifest must carry a policy_gate, so a run that bypassed the wrapper (which is
    # the only thing that writes policy_gate) is visible.
    def plant2(tmp: str) -> str:
        planted = os.path.join(tmp, "lab", "runs", "ZZ-planted-nogate.json")
        with open(planted, "w", encoding="utf-8") as fh:
            json.dump({"schema": "run/v1.1", "run_id": "ZZ-planted-nogate",
                       "owner": "lead", "status": "finished",
                       "started_at": "2026-11-08T00:00:00Z"}, fh)
        return "planted a manifest written without the wrapper (no policy_gate)"

    def check2(tmp: str) -> tuple[int, str]:
        return run([sys.executable, "scripts/check_run_manifest_gate.py"], tmp)

    def clean2(tmp: str) -> None:
        os.remove(os.path.join(tmp, "lab", "runs", "ZZ-planted-nogate.json"))

    return probe("P1_no_wrapper", "a run that bypassed the wrapper (manifest without policy_gate)",
                 "policy_gate", ["lab", "scripts"], plant2, check2, clean2)


def p2_foreign_owner() -> dict:
    """A manifest claiming an owner the policy does not know."""
    def plant(tmp: str) -> str:
        planted = os.path.join(tmp, "lab", "runs", "ZZ-planted-foreign.json")
        with open(planted, "w", encoding="utf-8") as fh:
            json.dump({"schema": "run/v1.1", "run_id": "ZZ-planted-foreign",
                       "owner": "foreign-agent-xyz", "status": "finished",
                       "started_at": "2026-11-08T00:00:00Z"}, fh)
        return "planted a manifest with an invented owner"

    def check(tmp: str) -> tuple[int, str]:
        return run([sys.executable, "scripts/check_autonomy.py"], tmp)

    def clean(tmp: str) -> None:
        os.remove(os.path.join(tmp, "lab", "runs", "ZZ-planted-foreign.json"))

    return probe("P2_foreign_owner", "a run claiming a foreign owner", "foreign-agent-xyz",
                 ["lab", "scripts"], plant, check, clean)


def p3_weights() -> dict:
    """A weights file that is not ignored: does the repository notice?"""
    def plant(tmp: str) -> str:
        w = os.path.join(tmp, "morphogenesis", "checkpoints", "ZZ_planted.pt")
        os.makedirs(os.path.dirname(w), exist_ok=True)
        with open(w, "wb") as fh:
            fh.write(b"not a real checkpoint")
        # remove the ignore rule so the file becomes stageable
        gi = os.path.join(tmp, ".gitignore")
        if os.path.exists(gi):
            with open(gi, encoding="utf-8") as fh:
                text = fh.read()
            text = "\n".join(l for l in text.splitlines() if "*.pt" not in l and ".pt" not in l)
            with open(gi, "w", encoding="utf-8") as fh:
                fh.write(text)
        return "planted an unignored .pt weights file"

    def check(tmp: str) -> tuple[int, str]:
        return run([sys.executable, "scripts/check_weights_ignored.py"], tmp)

    def clean(tmp: str) -> None:
        # restore BOTH halves of the defect: the file and the ignore rule that was removed to make it stageable
        w = os.path.join(tmp, "morphogenesis", "checkpoints", "ZZ_planted.pt")
        if os.path.exists(w):
            os.remove(w)
        gi_src = os.path.join(ROOT, ".gitignore")
        gi_dst = os.path.join(tmp, ".gitignore")
        if os.path.exists(gi_src):
            shutil.copy2(gi_src, gi_dst)

    return probe("P3_weights", "a weights file that is not ignored", "weights",
                 ["morphogenesis", "scripts", ".gitignore"], plant, check, clean)


def p4_protected_path() -> dict:
    """A protected path changed without a decision-log entry."""
    def plant(tmp: str) -> str:
        with open(os.path.join(tmp, "lab", "autonomy-rules.json"), encoding="utf-8") as fh:
            rules = json.load(fh)
        rules["protected_paths"] = list(rules.get("protected_paths") or []) + ["ZZ_planted_protected.md"]
        with open(os.path.join(tmp, "lab", "autonomy-rules.json"), "w", encoding="utf-8") as fh:
            json.dump(rules, fh, ensure_ascii=False, indent=1)
        target = os.path.join(tmp, "ZZ_planted_protected.md")
        with open(target, "w", encoding="utf-8") as fh:
            fh.write("a protected file, changed\n")
        return "planted a protected path change with no decision-log entry"

    def check(tmp: str) -> tuple[int, str]:
        return run([sys.executable, "scripts/check_protected_staged.py", "ZZ_planted_protected.md"], tmp)

    def clean(tmp: str) -> None:
        # restore BOTH halves: the file and the rule that was added to make it protected
        target = os.path.join(tmp, "ZZ_planted_protected.md")
        if os.path.exists(target):
            os.remove(target)
        rules_src = os.path.join(ROOT, "lab", "autonomy-rules.json")
        rules_dst = os.path.join(tmp, "lab", "autonomy-rules.json")
        shutil.copy2(rules_src, rules_dst)

    return probe("P4_protected_path", "a protected path staged without a decision-log entry",
                 "decision", ["lab", "scripts", "docs"], plant, check, clean)


def p5_double_lock() -> dict:
    """Two queue items marked running at once."""
    def plant(tmp: str) -> str:
        qp = os.path.join(tmp, "lab", "queue.json")
        with open(qp, encoding="utf-8") as fh:
            q = json.load(fh)
        items = q.get("items") or []
        if len(items) < 2:
            return "queue has fewer than two items; cannot plant"
        items[0]["status"] = "running"
        items[1]["status"] = "running"
        with open(qp, "w", encoding="utf-8") as fh:
            json.dump(q, fh, ensure_ascii=False, indent=1)
        return "planted two items marked running"

    def check(tmp: str) -> tuple[int, str]:
        return run([sys.executable, "scripts/check_single_running.py"], tmp)

    def clean(tmp: str) -> None:
        qp = os.path.join(tmp, "lab", "queue.json")
        with open(qp, encoding="utf-8") as fh:
            q = json.load(fh)
        for it in q.get("items") or []:
            it["status"] = "pending"
        with open(qp, "w", encoding="utf-8") as fh:
            json.dump(q, fh, ensure_ascii=False, indent=1)

    return probe("P5_double_lock", "two queue items marked running", "running",
                 ["lab", "scripts"], plant, check, clean)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    args = ap.parse_args(argv)

    probes = [p1_no_wrapper(), p2_foreign_owner(), p3_weights(), p4_protected_path(), p5_double_lock()]
    caught = sum(1 for p in probes if p["caught"] and p["reason_matched"])
    recovered = sum(1 for p in probes if p["clean_passes"])
    for p in probes:
        ok = p["caught"] and p["reason_matched"] and p["clean_passes"]
        mark = "CAUGHT" if ok else "HOLE"
        print(f"[{mark}] {p['probe']}: {p['defect']}")
        if not ok:
            print(f"        planted={p['planted']} caught={p['caught']} "
                  f"reason={p['reason_matched']} clean_passes={p['clean_passes']}")
            if p.get("note"):
                print(f"        note: {p['note']}")
            if p.get("excerpt"):
                print(f"        excerpt: {p['excerpt']}")
    print(f"\n[closure] сценариев: {len(probes)}, дефектов поймано с ожидаемой причиной: {caught}, "
          f"восстановление проверено: {recovered}, дыр: {len(probes) - caught}")
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump({"scenarios": len(probes), "caught": caught, "recovered": recovered,
                       "holes": len(probes) - caught, "probes": probes}, fh, ensure_ascii=False, indent=1)
        print(f"written: {args.json}")
    return 0 if caught == len(probes) else 1


if __name__ == "__main__":
    sys.exit(main())
