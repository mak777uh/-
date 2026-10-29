#!/usr/bin/env python
"""Литература ПОД ТЕМУ: что проходим сейчас и что будем проходить завтра.

Отличие от `lit_pressure.py`: тот отвечает «есть ли долг», этот — «что почитать по текущей и
следующей теме и что это меняет в нашей работе». Темы ведутся руками в `library/topics.json`
(что проходим, ссылки, английские запросы, шаблон «к чему обязывает»).

Алгоритм:
1. берём темы со статусом `current` (сегодня) и `next` (завтра);
2. по каждой — запросы в Crossref (метаданные) и OpenAlex (абстракты);
3. отбрасываем то, что уже есть в библиотеке (скан DOI по `library/**.md`);
4. фильтр: год >= `min_year`, есть абстракт;
5. пишем `library/topic-digest-<date>.md`: на тему 0–2 работы + черновик комментария главному.

Комментарий — черновик: проверка и формулировка остаются за библиотекарем.
Запуск:
  python library/tools/topic_lit.py                 # current + next
  python library/tools/topic_lit.py --status next   # только завтра
  python library/tools/topic_lit.py --dry
"""
from __future__ import annotations

import argparse
import json
import re
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LIB = REPO / "library"
TOPICS = LIB / "topics.json"
STATE = LIB / ".topic-digest-state.json"


def http_json(url: str, timeout: int = 45):
    try:
        return json.load(urllib.request.urlopen(url, timeout=timeout))
    except Exception:
        return None


def library_text() -> str:
    parts: list[str] = []
    skip = ("topic-digest-", "science-review-")
    for path in LIB.rglob("*.md"):
        if path.name.startswith(skip):
            continue  # собственные сводки не считаются «источниками в библиотеке»
        try:
            parts.append(path.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            continue
    return re.sub(r"\s+", " ", " ".join(parts)).lower()


def norm_title(t: str) -> str:
    return re.sub(r"[^a-z0-9 ]+", " ", (t or "").lower()).strip()


def known_dois() -> set[str]:
    dois: set[str] = set()
    skip = ("topic-digest-", "science-review-")
    for path in LIB.rglob("*.md"):
        if path.name.startswith(skip):
            continue  # сводки не источники
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for m in re.finditer(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+", text):
            dois.add(m.group(0).lower().rstrip(".,;)"))
    return dois


BAD_DOI = ("review", "table-", "/v1/review", "/v2/review")
BAD_TITLE = ("reviewer", "review for", "peer review", "review report", "recommendation:",
             "elife assessment", "author response", "decision letter", "response to review")


def looks_like_artifact(doi: str, title: str = "") -> bool:
    d = doi.lower()
    if any(b in d for b in BAD_DOI):
        return True
    if re.search(r"\.sa\d", d):  # peer-review artifacts в eLife
        return True
    t = (title or "").strip().lower()
    return any(t.startswith(b) or b in t[:40] for b in BAD_TITLE)


def crossref(query: str, rows: int = 6) -> list[dict]:
    url = "https://api.crossref.org/works?" + urllib.parse.urlencode(
        {"query.bibliographic": query, "rows": rows})
    data = http_json(url)
    if not data:
        return []
    out = []
    for m in data.get("message", {}).get("items", []):
        doi = (m.get("DOI") or "").lower()
        year = (m.get("issued", {}).get("date-parts") or [[None]])[0][0]
        authors = ", ".join(a.get("family", "") for a in (m.get("author") or [])[:3])
        out.append({
            "doi": doi,
            "year": year,
            "authors": authors,
            "journal": (m.get("container-title") or [""])[0],
            "title": (m.get("title") or [""])[0],
        })
    return out


def passes_must(topic: dict, cand: dict, abs_text: str) -> bool:
    """Доменный фильтр: хотя бы один обязательный термин в заголовке или абстракте."""
    must = [m.lower() for m in topic.get("must", [])]
    if not must:
        return True
    blob = ((cand.get("title") or "") + " " + (abs_text or "")).lower()
    return any(m in blob for m in must)


def relevance(topic: dict, cand: dict, abs_text: str) -> int:
    """Счёт: термин в заголовке весит 2, в абстракте — 1. Порог задаётся в теме (terms)."""
    terms = [t.lower() for t in topic.get("terms", [])]
    title = (cand.get("title") or "").lower()
    body = (abs_text or "").lower()
    score = 0
    for term in terms:
        if term in title:
            score += 2
        elif term in body:
            score += 1
    return score


def abstract(doi: str) -> str | None:
    data = http_json("https://api.openalex.org/works/https://doi.org/" + doi)
    if not data:
        return None
    inv = data.get("abstract_inverted_index")
    if not inv:
        return None
    pos: dict[int, str] = {}
    for word, idx in inv.items():
        for i in idx:
            pos[i] = word
    return " ".join(pos[i] for i in sorted(pos))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Литература под текущую и следующую тему")
    ap.add_argument("--status", choices=["current", "next", "current+next"], default="current+next")
    ap.add_argument("--per-topic", type=int, default=2)
    ap.add_argument("--date", default=date.today().isoformat())
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args(argv)

    cfg = json.loads(TOPICS.read_text(encoding="utf-8"))
    min_year = int(cfg.get("min_year", 2015))
    wanted = {"current", "next"} if args.status == "current+next" else {args.status}
    topics = [t for t in cfg["topics"] if t.get("status") in wanted]
    have = known_dois()
    state = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {"seen": []}
    seen = set(state.get("seen", []))

    blob = library_text()
    lines = [f"# Литература под тему — {args.date}", "",
             "Темы: " + ", ".join(f"{t['ru']} ({t['status']})" for t in topics), ""]
    written = 0
    picked_all: list[dict] = []
    for topic in topics:
        lines.append(f"## {topic['ru']}  `{topic['id']}` ({topic['status']})")
        if topic.get("links"):
            lines.append("где у нас: " + ", ".join(f"`{l}`" for l in topic["links"]))
        picked: list[dict] = []
        for q in topic.get("queries", []):
            for cand in crossref(q):
                if not cand["doi"] or cand["doi"] in have or cand["doi"] in seen:
                    continue
                if looks_like_artifact(cand["doi"], cand.get("title", "")):
                    continue
                topic_min = int(topic.get("min_year", min_year))
                if cand["year"] and int(cand["year"]) < topic_min:
                    continue
                if any(cand["doi"] == p["doi"] for p in picked):
                    continue
                abs_ = abstract(cand["doi"])
                if not abs_ and not topic.get("allow_no_abstract"):
                    continue
                abs_ = abs_ or "(абстракт недоступен — проверить по Crossref/полю, не цитировать вслепую)"
                title_norm = norm_title(cand.get("title", ""))
                if len(title_norm) >= 40 and title_norm[:60] in blob:
                    continue  # эта работа уже в библиотеке (по названию)
                if not passes_must(topic, cand, abs_):
                    continue
                base = relevance(topic, cand, abs_)
                penalty = 0
                if cand["doi"].startswith("10.1101/") or cand["doi"].startswith("10.20944/"):
                    penalty += 1
                    cand["preprint"] = True
                head = ((abs_ or "")[:220] + " " + (cand.get("title") or "")).lower()
                if re.search(r"correspondence|comment on|reply to|response to|erratum", head):
                    continue  # не исследовательская работа — как источник не годится
                score = base - penalty
                if score < int(topic.get("min_score", 3)):
                    continue
                cand["abstract"] = abs_[:600]
                cand["score"] = score
                picked.append(cand)
                picked_all.append(cand)
                if len(picked) >= args.per_topic:
                    break
            if len(picked) >= args.per_topic:
                break
        if not picked:
            lines.append("- не нашлось работ выше порога: отброшены артефакты, препринты дублей, "
                         "нет абстракта, не прошёл доменный фильтр или релевантность < порога")
        for c in picked:
            lines.append(f"- **{c['authors']} {c['year']}**, {c['journal']} — «{c['title'][:100]}»  ")
            kind = "препринт" if c.get("preprint") else "статья"
            lines.append(f"  DOI `{c['doi']}`; {kind}; релевантность {c.get('score', '?')}; "
                         f"абстракт: {c['abstract'][:300]}…")
            have.add(c["doi"])
            written += 1
        lines.append(f"**К чему обязывает:** {topic.get('implication', '—')}")
        lines.append("")
    lines.append("## Комментарий главному (черновик)")
    lines.append("Сформулировать: (1) что из найденного меняет наш следующий шаг, (2) что подтверждает, "
                 "но менять не надо, (3) какая оговорка обязательна в тексте. Проверка DOI и отбор — "
                 "за библиотекарем.")
    text = "\n".join(lines) + "\n"
    if args.dry:
        print(text)
        return 0
    out = LIB / f"topic-digest-{args.date}.md"
    out.write_text(text, encoding="utf-8", newline="\n")
    # храним только УЖЕ ПРЕДЛОЖЕННЫЕ работы; библиотечные DOI восстанавливаются сканом,
    # иначе state навсегда блокирует поиск (замечание себе: дедуп ≠ «всё видел»)
    proposed = {c["doi"] for c in picked_all}
    state["seen"] = sorted(seen | proposed)[-400:]
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"темы: {len(topics)} | новых работ: {written} -> {out.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
