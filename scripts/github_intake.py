"""github_intake.py — GitHub issues as a task source, with an author allowlist.

The pattern is taken from DeepSeek's dsh-superagent prototype: the agent does not need a task typed into a chat, it watches
an authorised channel and turns an incoming item into a queue item with a session of its own. Here the channel is the
repository's issue tracker: an open issue carrying the `lab:task` label and written by an author listed in
`lab/autonomy-rules.json → authorized_task_sources.github_issues` becomes a queue item.

Read-only by design: the script never posts to GitHub, because the repository pushes over a deploy key and has no API token
for writing. The answer goes into the report and the queue item's `note`; commenting back in the issue is a manual step (or a
later task, if a token is ever provided).

    python scripts/github_intake.py               # show what would be added
    python scripts/github_intake.py --write       # append the items to lab/queue.json

Idempotency: an item whose `note` contains `issue#<number>` is not added twice.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "lab" / "queue.json"
RULES = ROOT / "lab" / "autonomy-rules.json"
API = "https://api.github.com/repos/{repo}/issues?state=open&labels={label}&per_page=50"


def load(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def fetch(repo: str, label: str) -> list[dict]:
    url = API.format(repo=repo, label=label)
    req = urllib.request.Request(url, headers={"User-Agent": "dsh-lab-intake", "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="GitHub issue intake")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    rules = load(RULES, {})
    src = ((rules.get("authorized_task_sources") or {}).get("github_issues") or {})
    repo, label = src.get("repo"), src.get("label")
    allowed = {a.lower() for a in (src.get("authors") or [])}
    if not repo or not label:
        print("[intake] в lab/autonomy-rules.json не задан источник github_issues — нечего делать")
        return 0

    try:
        issues = fetch(repo, label)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
        print(f"[intake] GitHub недоступен ({exc}) — повторим в следующем цикле, тихо")
        return 0

    queue = load(QUEUE, {"items": []})
    items = queue.get("items") or []
    known = {it.get("id") for it in items}
    taken_issues = set()
    for it in items:
        m = re.search(r"issue#(\d+)", str(it.get("note") or ""))
        if m:
            taken_issues.add(int(m.group(1)))

    added = []
    for issue in issues:
        if "pull_request" in issue:
            continue
        number = int(issue["number"])
        author = ((issue.get("user") or {}).get("login") or "").lower()
        if author not in allowed:
            print(f"[intake] issue#{number}: автор {author!r} не в списке разрешённых — пропуск")
            continue
        if number in taken_issues:
            continue
        title = str(issue.get("title") or "").strip() or f"issue {number}"
        item_id = f"gh{number}_{re.sub(r'[^a-z0-9]+', '_', title.lower())[:40].strip('_')}"
        if item_id in known:
            continue
        added.append({
            "id": item_id,
            "title": title[:120],
            "status": "planned",
            "owner": "lead",
            "kind": "task",
            "cost_gpu_h": 0,
            "created_at": str(issue.get("created_at") or "")[:10] + "T00:00:00+03:00",
            "note": f"issue#{number} from {author}: {str(issue.get('body') or '')[:200]}".strip(),
            "source_url": issue.get("html_url"),
        })

    for it in added:
        print(f"[intake] + {it['id']} — {it['title']}")
    print(f"[intake] новых: {len(added)} из {len(issues)} открытых с меткой «{label}»")
    if not args.write or not added:
        return 0
    items.extend(added)
    queue["items"] = items
    QUEUE.write_text(json.dumps(queue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"[intake] записано в {QUEUE.name}: {len(added)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
