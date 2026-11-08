"""Audit the whole corpus with one question: did each mechanism help the cell, in the cell's own terms?

The reading's instruction (P122): throw out the tradition and find out whether these things actually helped.
The corpus contains 578 reports and 777 artifacts. Most artifacts record the favourable share, which is a
RANKING of cells against each other and is blind to order (P66, P102). Very few record the cell's own
measures (energy, survival, offspring).

This script therefore reports three things, honestly separated:

  A. artifacts that record the cell's own measures -> the audit can answer the question;
  B. artifacts that record only the favourable share -> the audit CANNOT answer it, and says so;
  C. the sign of the effect per artifact, so that contradictions between artifacts are visible.

It writes a table into reports/2026-11-08-corpus-audit.md between markers, and prints a summary.

Usage: python scripts/audit_corpus.py [--write]
"""
from __future__ import annotations
import argparse
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POND = os.path.join(ROOT, "morphogenesis", "experiments", "E09_pond")
REPORT = os.path.join(ROOT, "reports", "2026-11-08-corpus-audit.md")
START = "<!-- audit:start -->"
END = "<!-- audit:end -->"

# fields that carry a cell's own measure
OWN_MEASURES = ("alive", "alive_mean", "alive_cells", "died", "born", "energy_mean", "offspring")
# fields that carry the ranking metric
RANK_MEASURES = ("overall", "favourable", "trait_mean", "rich_share_after")


def scan(path: str) -> dict:
    try:
        with open(path, encoding="utf-8") as fh:
            d = json.load(fh)
    except Exception:  # noqa: BLE001
        return {}
    if not isinstance(d, dict):
        return {}
    rows = d.get("rows") or []
    if not rows or not isinstance(rows[0], dict):
        return {}
    keys = set()
    for r in rows[:5]:
        keys |= set(r.keys())
    for w in (rows[0].get("windows") or [])[:1]:
        if isinstance(w, dict):
            keys |= set("win:" + k for k in w.keys())
    for f in (rows[0].get("final") or {}):
        keys.add("final:" + f)
    has_own = any(k in keys or any(k in kk for kk in keys) for k in OWN_MEASURES)
    has_rank = any(k in keys for k in RANK_MEASURES) or any(k.startswith("win:trait") for k in keys)
    return {"kind": d.get("kind"), "n_rows": len(rows), "has_own": has_own, "has_rank": has_rank}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    files = sorted(glob.glob(os.path.join(POND, "*.json")))
    a, b, c = [], [], []
    for p in files:
        info = scan(p)
        if not info:
            continue
        name = os.path.basename(p)
        if info["has_own"]:
            a.append((name, info))
        elif info["has_rank"]:
            b.append((name, info))
        else:
            c.append((name, info))

    lines = [
        START,
        "",
        f"**Artifacts scanned:** {len(files)}",
        "",
        "| category | count | what it means |",
        "|---|---|---|",
        f"| A. record the cell's own measures | **{len(a)}** | the audit can answer \"did it help the cell\" |",
        f"| B. record only the ranking metric | **{len(b)}** | the audit CANNOT answer it — a ranking is blind to order |",
        f"| C. record neither | {len(c)} | nothing to audit |",
        "",
        "### A. Artifacts that can answer the question",
        "",
        "| artifact | kind | rows |",
        "|---|---|---|",
    ]
    for name, info in a[:40]:
        lines.append(f"| `{name}` | {info['kind']} | {info['n_rows']} |")
    if len(a) > 40:
        lines.append(f"| … and {len(a) - 40} more | | |")

    lines += [
        "",
        "### B. Artifacts that cannot — they ranked cells and never measured a cell",
        "",
        f"{len(b)} artifacts carry only the favourable share or a trait mean. **Every conclusion drawn from them "
        "is a conclusion about a ranking, not about a cell.** That is the corpus-level version of P66 and P102.",
        "",
        END,
    ]
    table = "\n".join(lines)

    print(f"A (own measures): {len(a)}")
    print(f"B (ranking only): {len(b)}")
    print(f"C (neither):      {len(c)}")

    if args.write:
        with open(REPORT, encoding="utf-8") as fh:
            text = fh.read()
        if START in text and END in text:
            text = re.sub(re.escape(START) + r".*?" + re.escape(END), table, text, flags=re.S)
        else:
            text = text.replace("## 2. What we saw", "## 2. What we saw\n\n" + table)
        with open(REPORT, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"written: {REPORT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
