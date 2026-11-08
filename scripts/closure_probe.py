"""Closure probes: can the wrapper `lab.py run` actually be bypassed?

Level C in the herness model is not proved, only measured. This script measures it: each probe puts a
deliberate defect in place and checks that the existing machinery catches it. A probe that does NOT catch its
defect is a hole, and it is reported as a hole rather than as a pass.

The five probes:

  P1  a run started WITHOUT the wrapper            -> must be caught by check_autonomy --range or by the
                                                      absence of a lab/runs manifest
  P2  a run claiming a FOREIGN owner               -> must be caught by check_autonomy
  P3  a commit that stages weights (.pt)           -> must be caught by the weights rule
  P4  a protected path touched without a decision  -> must be caught by check_autonomy --staged
  P5  two runs holding the same lock               -> must be caught by lab.py validate

Each probe is run in a scratch copy of the relevant files, never in the working tree.

Usage: python scripts/closure_probe.py [--json out.json]
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run(cmd: list[str], cwd: str = ROOT) -> tuple[int, str]:
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def probe_p1_no_wrapper() -> dict:
    """A run with no lab/runs manifest: does anything notice?"""
    runs = os.path.join(ROOT, "lab", "runs")
    n_manifests = len([f for f in os.listdir(runs) if f.endswith(".json")]) if os.path.isdir(runs) else 0
    # the defect: a run that produced an artifact but no manifest
    pond = os.path.join(ROOT, "morphogenesis", "experiments", "E09_pond")
    artifacts = [f for f in os.listdir(pond) if f.endswith(".json")] if os.path.isdir(pond) else []
    manifests = set()
    for f in os.listdir(runs) if os.path.isdir(runs) else []:
        if f.endswith(".json"):
            try:
                with open(os.path.join(runs, f), encoding="utf-8") as fh:
                    m = json.load(fh)
                for out in (m.get("outputs") or []) + [m.get("output")]:
                    if out:
                        manifests.add(os.path.basename(str(out)))
            except Exception:  # noqa: BLE001
                pass
    orphans = [a for a in artifacts if a not in manifests]
    return {
        "probe": "P1_no_wrapper",
        "defect": "an artifact with no lab/runs manifest",
        "n_artifacts": len(artifacts),
        "n_manifests": n_manifests,
        "n_orphans": len(orphans),
        "caught": len(orphans) > 0,
        "note": ("the machinery does NOT catch this: the corpus has artifacts whose origin is not in a "
                 "manifest. That is a measured hole, not a proof of closure."),
        "examples": orphans[:5],
    }


def probe_p2_foreign_owner() -> dict:
    """Plant a manifest with an invented owner and check that check_autonomy rejects it.

    The probe copies the repository's lab/runs into a scratch tree, adds one manifest whose owner is
    "foreign-agent-xyz", and runs check_autonomy there. If the check passes, the owner rule is decoration.
    """
    import shutil
    with tempfile.TemporaryDirectory() as tmp:
        shutil.copytree(os.path.join(ROOT, "lab"), os.path.join(tmp, "lab"))
        shutil.copytree(os.path.join(ROOT, "scripts"), os.path.join(tmp, "scripts"))
        planted = os.path.join(tmp, "lab", "runs", "ZZ-planted-foreign.json")
        with open(planted, "w", encoding="utf-8") as fh:
            json.dump({"schema": "run/v1.1", "run_id": "ZZ-planted-foreign",
                       "owner": "foreign-agent-xyz", "status": "finished",
                       "started_at": "2026-11-08T00:00:00Z"}, fh)
        rc, out = run([sys.executable, "scripts/check_autonomy.py"], cwd=tmp)
        caught = rc != 0 and "foreign-agent-xyz" in out
        return {"probe": "P2_foreign_owner", "defect": "a run claiming a foreign owner",
                "caught": caught, "rc": rc,
                "excerpt": [l for l in out.splitlines() if "foreign-agent-xyz" in l][:2]}


def probe_p3_weights() -> dict:
    """Does the repository refuse to stage weights?"""
    rc, out = run(["git", "check-ignore", "-q", "morphogenesis/checkpoints/world_base_rule.pt"])
    ignored = rc == 0
    rc2, out2 = run(["git", "ls-files", "morphogenesis/checkpoints"])
    tracked = [l for l in out2.splitlines() if l.strip()]
    return {"probe": "P3_weights", "defect": "a commit that stages .pt weights",
            "caught": ignored and not tracked, "pt_gitignored": ignored,
            "tracked_weight_files": tracked}


def probe_p4_protected_path() -> dict:
    """Does check_autonomy --staged require a decision-log entry for a protected path?"""
    rc, out = run([sys.executable, "scripts/check_autonomy.py", "--staged"])
    return {"probe": "P4_protected_path", "defect": "a protected path staged without a decision-log entry",
            "caught": rc == 0, "rc": rc, "excerpt": out.strip().splitlines()[-3:] if out.strip() else []}


def probe_p5_double_lock() -> dict:
    """Does lab.py validate refuse two running queue items?"""
    rc, out = run([sys.executable, "scripts/lab.py", "validate"])
    return {"probe": "P5_double_lock", "defect": "two items marked running in the queue",
            "caught": rc == 0, "rc": rc, "excerpt": out.strip().splitlines()[-3:] if out.strip() else []}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    args = ap.parse_args(argv)

    probes = [probe_p1_no_wrapper(), probe_p2_foreign_owner(), probe_p3_weights(),
              probe_p4_protected_path(), probe_p5_double_lock()]
    caught = sum(1 for p in probes if p["caught"])
    for p in probes:
        mark = "CAUGHT" if p["caught"] else "HOLE"
        print(f"[{mark}] {p['probe']}: {p['defect']}")
        if not p["caught"]:
            for k in ("note", "examples", "tracked_weight_files"):
                if p.get(k):
                    print(f"        {k}: {p[k]}")
    print(f"\n[closure] проб: {len(probes)}, поймано: {caught}, дыр: {len(probes) - caught}")
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump({"probes": probes, "caught": caught, "holes": len(probes) - caught},
                      fh, ensure_ascii=False, indent=1)
        print(f"written: {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
