"""Number gate for article 036: every number in the text is produced by a command that must succeed.

The first version of this gate had three defects a reviewer named, and all three are fixed here:

  1. it did not check exit codes - a command could fail and the gate would still parse its output;
  2. it checked fewer numbers than the article states;
  3. it parsed Russian output with hand-written regexes inside the script, so the list of claims lived in code.

Now the claims live in `lab/article-036-claims.json`, each with the command, the exit code it must return and
the value parsed from its output. The script reads that file, runs each command, and fails if:

  - the command exits non-zero (a failing command is not evidence, whatever it printed);
  - the parsed value differs from the expected one;
  - the article does not state the phrase.

Negative self-test: `--self-test` mutates one claim to a wrong value and checks that the gate fails, so the gate
is shown to be able to fail rather than assumed to be able to pass.

Usage:
  python scripts/check_article_036_numbers.py
  python scripts/check_article_036_numbers.py --self-test
"""
from __future__ import annotations
import argparse
import glob
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTICLE = os.path.join(ROOT, "articles", "036-a-research-bench-where-the-instrument-reports-on-itself.md")
CLAIMS = os.path.join(ROOT, "lab", "article-036-claims.json")


def _env() -> dict:
    env = dict(os.environ)
    elan = os.path.join(os.path.expanduser("~"), ".elan", "bin")
    cargo = os.path.join(os.path.expanduser("~"), ".cargo", "bin")
    env["PATH"] = os.pathsep.join([elan, cargo, env.get("PATH", "")])
    env["PYTHONIOENCODING"] = "utf-8"
    return env


_CACHE: dict[tuple[str, ...], tuple[int, str]] = {}


def run(cmd: list[str]) -> tuple[int, str]:
    """Run a command once per gate run.

    Several claims read different numbers out of the same command (closure_probe prints scenarios, caught,
    recovered and holes; policy_diff prints cases, implementations and disagreements). Without the cache each
    claim re-ran the command, and closure_probe alone copies the laboratory five times per call.
    """
    if cmd and cmd[0] == "python":
        cmd = [sys.executable] + cmd[1:]
    key = tuple(cmd)
    if key in _CACHE:
        return _CACHE[key]
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", env=_env(), timeout=1800)
    out = (p.returncode, (p.stdout or "") + (p.stderr or ""))
    _CACHE[key] = out
    return out


def evaluate(claim: dict) -> tuple[bool, str]:
    """Run one claim. Returns (ok, detail)."""
    if claim["how"] == "count":
        n = len(glob.glob(os.path.join(ROOT, claim["glob"])))
        return n == claim["expected"], f"найдено {n}, ожидалось {claim['expected']}"
    if claim["how"] == "count_gates":
        # verify.py declares its gates as a local list `steps` inside main(), and runs ONE more check outside
        # that list: check_no_sorry(). Counting only the list gives 28 and looks like a discrepancy; the real
        # number is 29. Both parts are counted here.
        with open(os.path.join(ROOT, "scripts", "verify.py"), encoding="utf-8") as fh:
            src = fh.read()
        m = re.search(r"steps:\s*list\[tuple\[.*?\]\]\s*=\s*\[(.*?)\n\s*\]", src, re.S)
        if not m:
            return False, "не найден список steps в scripts/verify.py"
        n = len(re.findall(r'^\s*\("', m.group(1), re.M))
        if re.search(r"check_no_sorry\(\)", src):
            n += 1
        return n == claim["expected"], f"найдено {n}, ожидалось {claim['expected']}"
    if claim["how"] == "sum_audit":
        rc, out = run([sys.executable, "scripts/audit_corpus.py"])
        if rc != 0:
            return False, f"audit_corpus вернул {rc}"
        nums = re.findall(r":\s*(\d+)\s*$", out, re.M)
        if len(nums) < 3:
            return False, f"не разобраны три категории аудита: {out.strip()[-160:]}"
        n = sum(int(x) for x in nums[:3])
        return n == claim["expected"], f"сумма категорий {n}, ожидалось {claim['expected']}"
    rc, out = run(list(claim["command"]))
    if rc != claim.get("expect_rc", 0):
        return False, f"команда вернула {rc}, ожидался {claim.get('expect_rc', 0)}"
    m = re.search(claim["parse"], out)
    if not m:
        return False, f"вывод не разобран по «{claim['parse']}»: {out.strip()[-160:]}"
    value = next((g for g in m.groups() if g is not None), None)
    if value is None:
        return False, "regexp matched but produced no group"
    n = int(value)
    return n == claim["expected"], f"найдено {n}, ожидалось {claim['expected']}"


def check_all(claims: list[dict], text: str) -> tuple[int, int]:
    ok_n = 0
    fail_n = 0
    for c in claims:
        ok, detail = evaluate(c)
        stated = c["phrase"] in text
        if ok and stated:
            ok_n += 1
            print(f"OK   {c['id']:24s} {c['phrase']}")
        else:
            fail_n += 1
            why = [] if ok else [detail]
            if not stated:
                why.append(f"статья не содержит «{c['phrase']}»")
            print(f"FAIL {c['id']:24s} {c['phrase']} — {'; '.join(why)}")
    return ok_n, fail_n


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)

    with open(CLAIMS, encoding="utf-8") as fh:
        data = json.load(fh)
    claims = data["claims"]
    with open(ARTICLE, encoding="utf-8") as fh:
        text = fh.read()

    if args.self_test:
        # mutate one claim to a value that cannot be right, and require the gate to fail on it
        bad = json.loads(json.dumps(claims))
        bad[0]["expected"] = bad[0]["expected"] + 1
        ok_n, fail_n = check_all(bad, text)
        print(f"\n[self-test] при подложенном неверном числе провалов: {fail_n} (должно быть >= 1)")
        return 0 if fail_n >= 1 else 1

    ok_n, fail_n = check_all(claims, text)
    print(f"\n[article-036] утверждений: {len(claims)}, прошло: {ok_n}, провалов: {fail_n}")
    return 0 if fail_n == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
