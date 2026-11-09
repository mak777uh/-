"""Prove the arm gate can fail, and that it passes on the real series.

A gate that cannot fail is decoration. This plants a wrong expectation and requires the gate to report it.
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GATE = os.path.join(ROOT, "scripts", "check_arm_matches.py")
E19 = os.path.join(ROOT, "morphogenesis", "experiments", "E19")

fails = 0


def check(name, ok, detail=""):
    global fails
    print(f"{'OK  ' if ok else 'FAIL'} {name}{(' — ' + detail) if detail and not ok else ''}")
    if not ok:
        fails += 1


def run(*args):
    p = subprocess.run([sys.executable, GATE, *args], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout or "") + (p.stderr or "")


if not os.path.isdir(E19):
    print("[arm-selftest] E19 artifacts not found; nothing to check")
    sys.exit(0)

# 1. the real series passes
rc, out = run("--dir", E19, "--field", "plastic_gate", "--expect", "random", "--arm", "record_random")
check("the real random arm passes", rc == 0, out[-200:])

rc, out = run("--dir", E19, "--field", "plastic_gate", "--expect", "pred", "--arm", "record_pred")
check("the real pred arm passes", rc == 0, out[-200:])

# 2. a planted mismatch must fail
rc, out = run("--dir", E19, "--field", "plastic_gate", "--expect", "random", "--arm", "record_pred")
check("a planted mismatch is caught", rc != 0, out[-200:])
check("the failure names the field", "plastic_gate" in out, out[-200:])

# 3. a missing directory must fail
rc, out = run("--dir", os.path.join(ROOT, "no_such_dir"), "--field", "plastic_gate", "--expect", "x")
check("a missing directory is caught", rc != 0, out[-200:])

print(f"\n[arm-selftest] провалов: {fails} из 4")
sys.exit(0 if fails == 0 else 1)
