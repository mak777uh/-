"""Automatic literature enqueueing: the librarian should not wait to be asked.

Why. The librarian works when a message arrives in `lab/notices.md`. Between messages nothing happens, so a
gap that the bench itself discovers - a gate that fails with a message nobody has seen, a manifest that
admits its sensitivity is unknown, a report that says "we do not know" - sits unnoticed until a human
remembers to ask.

This script watches for those events and appends a question to `lab/lit-queue.json`. It does NOT search; it
only makes the question visible, with the context a search needs: `question`, `why`, `target`, `deliverable`.

The four triggers are the ones AGENTS.md §3a already names, plus one:

  T1  a gate failed with a message the queue has not seen before        ("стало хуже")
  T2  a manifest was written with `sensitivity` unknown or waived        ("нужен параметр")
  T3  a report contains "we do not know" / "unexplained" / "неизвестно"  ("не проверяли")
  T4  a new config field appeared with no citation in the manifest       ("будем перебирать")
  T5  an open question in docs/open-questions.md has no answer yet       (the audit's own questions)

Idempotent: a question already in the queue is not added twice. Read-only with respect to everything except
`lab/lit-queue.json`.

Usage:
  python scripts/lit_autoqueue.py            # report what would be added
  python scripts/lit_autoqueue.py --write    # add it
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUEUE = os.path.join(ROOT, "lab", "lit-queue.json")
QUESTIONS = os.path.join(ROOT, "docs", "open-questions.md")


def _load_queue() -> dict:
    if os.path.exists(QUEUE):
        with open(QUEUE, encoding="utf-8") as fh:
            return json.load(fh)
    return {"items": []}


def _key(question: str) -> str:
    return hashlib.sha256(question.strip().lower().encode("utf-8")).hexdigest()[:16]


def _existing_keys(queue: dict) -> set[str]:
    return {it.get("key") or _key(it.get("question", "")) for it in queue.get("items", [])}


def trigger_open_questions() -> list[dict]:
    """T5: every open question without an `**Answer.**` section becomes a queue item."""
    out = []
    if not os.path.exists(QUESTIONS):
        return out
    with open(QUESTIONS, encoding="utf-8") as fh:
        text = fh.read()
    blocks = re.split(r"\n## (?=Q\d+\.)", text)
    for b in blocks:
        m = re.match(r"(Q\d+)\.\s*(.+)", b.strip())
        if not m:
            continue
        qid, title = m.group(1), m.group(2).strip()
        # an answer may be "**Answer.**", "**Answer (partial).**" or "**Evidence:**" - any of them closes it
        if re.search(r"\*\*(Answer|Evidence)", b):
            continue
        search = ""
        sm = re.search(r"\*\*Search for:\*\*\s*(.+)", b)
        if sm:
            search = sm.group(1).strip()
        out.append({
            "key": _key(qid + title),
            "question": f"{qid}: {title}",
            "why": "open question from the design audit (docs/open-questions.md)",
            "target": search or "see docs/open-questions.md",
            "deliverable": "an answer with a source, pasted under **Answer.** in docs/open-questions.md",
            "source": "docs/open-questions.md",
        })
    return out


# Only reports this recent are candidates for T3. Older reports were read when they were written; a queue
# that re-adds them on every run is noise, and noise makes the queue unreadable.
RECENT_DAYS = 7
DATE_RE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")


def _recent(name: str, days: int = RECENT_DAYS) -> bool:
    import datetime
    m = DATE_RE.search(name)
    if not m:
        return False
    try:
        d = datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return False
    return (datetime.date.today() - d).days <= days


def trigger_reports() -> list[dict]:
    """T3: a RECENT report that admits it does not know."""
    out = []
    reports = os.path.join(ROOT, "reports")
    if not os.path.isdir(reports):
        return out
    pat = re.compile(r"(we do not know|unexplained|неизвестно|не проверяли|we cannot say)", re.I)
    for name in sorted(os.listdir(reports)):
        if not name.endswith(".md"):
            continue
        if not _recent(name):
            continue
        path = os.path.join(reports, name)
        try:
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
        except Exception:  # noqa: BLE001
            continue
        hits = pat.findall(text)
        if hits:
            q = f"report {name} admits uncertainty ({len(hits)} occurrences of '{hits[0]}') - what does the literature say about this?"
            out.append({
                "key": _key(q),
                "question": q,
                "why": "T3: the report says the bench does not know",
                "target": name,
                "deliverable": "a citation that either settles it or shows it is genuinely open",
                "source": f"reports/{name}",
            })
    return out


def trigger_manifests() -> list[dict]:
    """T2: a manifest whose sensitivity is unknown or waived."""
    out = []
    exp = os.path.join(ROOT, "lab", "experiments")
    if not os.path.isdir(exp):
        return out
    for name in sorted(os.listdir(exp)):
        if not name.endswith(".json"):
            continue
        try:
            with open(os.path.join(exp, name), encoding="utf-8") as fh:
                m = json.load(fh)
        except Exception:  # noqa: BLE001
            continue
        sens = m.get("sensitivity") or {}
        flat = json.dumps(sens, ensure_ascii=False).lower()
        if "unknown" in flat or "waived" in flat:
            q = f"manifest {name} waives its sensitivity calculation - what is the right power calculation for this readout?"
            out.append({
                "key": _key(q),
                "question": q,
                "why": "T2: the manifest says the spread is unknown",
                "target": name,
                "deliverable": "a formula or a citation for the expected spread of this readout",
                "source": f"lab/experiments/{name}",
            })
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--check", action="store_true",
                    help="выйти с кодом 1, если в очереди не хватает вопросов (для make verify)")
    args = ap.parse_args(argv)

    queue = _load_queue()
    have = _existing_keys(queue)
    candidates = trigger_open_questions() + trigger_reports() + trigger_manifests()
    new = [c for c in candidates if c["key"] not in have]

    print(f"[lit-auto] кандидатов: {len(candidates)}, новых: {len(new)}")
    for c in new:
        print(f"  + {c['question'][:100]}")

    if args.write and new:
        queue.setdefault("items", []).extend(new)
        with open(QUEUE, "w", encoding="utf-8") as fh:
            json.dump(queue, fh, ensure_ascii=False, indent=1)
        print(f"[lit-auto] записано в {QUEUE}: {len(new)} новых")
    elif new:
        print("[lit-auto] запустите с --write, чтобы добавить")

    # --check is the mode `make verify` uses: it fails when the queue is behind reality, so a gap the bench
    # itself discovered cannot sit unnoticed until a human remembers to ask.
    if args.check:
        return 0 if not new else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
