#!/usr/bin/env python
"""lit_find.py — поиск литературы и веб-поиск без ключей, с честным отчётом об отказах.

Зачем: `topic_lit.py` берёт один источник и молча отбрасывает всё, что не подошло; когда источник
недоступен (плагин веб-поиска, Semantic Scholar без ключа), это выглядит как «ничего нет». Здесь:
несколько источников, дедупликация по DOI/названию, и в конце — сколько отброшено и почему.

Источники (все без ключа, проверены 31.10):
  openalex    — покрытие + абстракты (inverted index)
  crossref    — библиографическая точность, тип, год, издание
  arxiv       — препринты (Atom)
  europepmc   — биомед
  datacite    — наборы данных и препринты-депозиты
  web         — DuckDuckGo HTML (общий веб; ссылки без DOI)

Запуск:
  python library/tools/lit_find.py search --query "invasion growth rate coexistence" --limit 5
  python library/tools/lit_find.py search --query "storage effect" --sources openalex,arxiv --min-year 2015
  python library/tools/lit_find.py verify --doi 10.1007/s00285-025-02283-0
Коды: 0 — есть результаты; 1 — ничего не нашлось (с причинами); 2 — все источники недоступны.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

UA = "morphogenesis-library/1.0 (mailto:lab@example.org)"
TIMEOUT = 25


def get(url: str) -> bytes | None:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return r.read()
    except Exception:
        return None


def get_json(url: str):
    raw = get(url)
    if raw is None:
        return None
    try:
        return json.loads(raw.decode("utf-8", "replace"))
    except Exception:
        return None


def abstract_from_inverted(inv: dict | None) -> str:
    if not isinstance(inv, dict) or not inv:
        return ""
    pos = {}
    for word, idx in inv.items():
        for i in idx:
            pos[i] = word
    return " ".join(pos[i] for i in sorted(pos))


def norm_title(t: str) -> str:
    return re.sub(r"[^a-z0-9а-я]+", " ", (t or "").lower()).strip()


# ---------------------------------------------------------------- источники

def src_openalex(query: str, limit: int, min_year: int | None):
    url = ("https://api.openalex.org/works?search=" + urllib.parse.quote(query)
           + f"&per-page={min(limit * 3, 50)}&sort=relevance_score:desc")
    if min_year:
        url += f"&filter=from_publication_date:{min_year}-01-01"
    d = get_json(url)
    if not d:
        return None
    out = []
    for w in d.get("results") or []:
        out.append({
            "source": "openalex",
            "title": w.get("title") or "",
            "year": w.get("publication_year"),
            "doi": (w.get("doi") or "").replace("https://doi.org/", ""),
            "venue": ((w.get("primary_location") or {}).get("source") or {}).get("display_name") or "",
            "type": w.get("type") or "",
            "abstract": abstract_from_inverted(w.get("abstract_inverted_index")),
            "url": w.get("id") or "",
        })
    return out


def src_crossref(query: str, limit: int, min_year: int | None):
    url = ("https://api.crossref.org/works?query=" + urllib.parse.quote(query)
           + f"&rows={min(limit * 3, 50)}&select=DOI,title,issued,container-title,abstract,type")
    if min_year:
        url += f"&filter=from-pub-date:{min_year}-01-01"
    d = get_json(url)
    if not d:
        return None
    out = []
    for it in (d.get("message") or {}).get("items") or []:
        year = ((it.get("issued") or {}).get("date-parts") or [[None]])[0][0]
        out.append({
            "source": "crossref",
            "title": (it.get("title") or [""])[0],
            "year": year,
            "doi": it.get("DOI") or "",
            "venue": (it.get("container-title") or [""])[0],
            "type": it.get("type") or "",
            "abstract": re.sub(r"<[^>]+>", " ", it.get("abstract") or "").strip(),
            "url": "https://doi.org/" + (it.get("DOI") or ""),
        })
    return out


def src_arxiv(query: str, limit: int, min_year: int | None):
    q = urllib.parse.quote(f'all:"{query}"')
    raw = get(f"http://export.arxiv.org/api/query?search_query={q}&max_results={min(limit*3,50)}"
              "&sortBy=relevance")
    if raw is None:
        return None
    try:
        root = ET.fromstring(raw)
    except Exception:
        return None
    ns = {"a": "http://www.w3.org/2005/Atom"}
    out = []
    for e in root.findall("a:entry", ns):
        title = " ".join((e.findtext("a:title", "", ns) or "").split())
        pub = e.findtext("a:published", "", ns) or ""
        year = int(pub[:4]) if pub[:4].isdigit() else None
        link = e.findtext("a:id", "", ns) or ""
        out.append({
            "source": "arxiv", "title": title, "year": year, "doi": "",
            "venue": "arXiv", "type": "preprint",
            "abstract": " ".join((e.findtext("a:summary", "", ns) or "").split()),
            "url": link,
        })
    return out


def src_europepmc(query: str, limit: int, min_year: int | None):
    url = ("https://www.ebi.ac.uk/europepmc/webservices/rest/search?query="
           + urllib.parse.quote(query) + f"&format=json&pageSize={min(limit*3,50)}")
    d = get_json(url)
    if not d:
        return None
    out = []
    for r in (d.get("resultList") or {}).get("result") or []:
        out.append({
            "source": "europepmc", "title": r.get("title") or "",
            "year": int(r["pubYear"]) if str(r.get("pubYear", "")).isdigit() else None,
            "doi": r.get("doi") or "", "venue": r.get("journalTitle") or "",
            "type": r.get("pubType") or "", "abstract": r.get("abstractText") or "",
            "url": "https://doi.org/" + (r.get("doi") or "") if r.get("doi") else "",
        })
    return out


def src_datacite(query: str, limit: int, min_year: int | None):
    url = ("https://api.datacite.org/dois?query=" + urllib.parse.quote(query)
           + f"&page[size]={min(limit*3,50)}")
    d = get_json(url)
    if not d:
        return None
    out = []
    for it in d.get("data") or []:
        a = it.get("attributes") or {}
        titles = a.get("titles") or [{}]
        year = a.get("publicationYear")
        out.append({
            "source": "datacite", "title": titles[0].get("title") or "",
            "year": year, "doi": a.get("doi") or "", "venue": a.get("publisher") or "",
            "type": (a.get("types") or {}).get("resourceTypeGeneral") or "",
            "abstract": "", "url": "https://doi.org/" + (a.get("doi") or ""),
        })
    return out


BROWSER_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/120 Safari/537.36")

CACHE_PATH = Path(__file__).resolve().parents[1] / ".lit-find-cache.json"
CACHE_TTL = 7 * 24 * 3600


def _cache_get(key: str):
    try:
        d = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return None
    hit = d.get(key)
    if not hit or time.time() - hit.get("ts", 0) > CACHE_TTL:
        return None
    return hit.get("items")


def _cache_put(key: str, items):
    try:
        d = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    except Exception:
        d = {}
    d[key] = {"ts": time.time(), "items": items}
    try:
        CACHE_PATH.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8", newline="\n")
    except Exception:
        pass


def _fetch(url: str):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": BROWSER_UA})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return r.read().decode("utf-8", "replace")
    except Exception:
        return None


def _parse_ddg(html: str, limit: int):
    out = []
    for m in re.finditer(r"<a\b([^>]*)>(.*?)</a>", html, re.S):
        attrs, inner = m.group(1), m.group(2)
        if "result__a" not in attrs:
            continue
        href_m = re.search(r'href="([^"]+)"', attrs)
        if not href_m:
            continue
        href = href_m.group(1)
        if "uddg=" in href:
            mm = re.search(r"uddg=([^&]+)", href)
            if mm:
                href = urllib.parse.unquote(mm.group(1))
        title = re.sub(r"<[^>]+>", "", inner).strip()
        if title:
            out.append({"source": "web", "title": title, "year": None, "doi": "",
                        "venue": "", "type": "web", "abstract": "", "url": href})
        if len(out) >= limit:
            break
    return out


def _parse_ddg_lite(html: str, limit: int):
    out = []
    for m in re.finditer(r'<a\b([^>]*class="result-link"[^>]*)>(.*?)</a>', html, re.S):
        attrs, inner = m.group(1), m.group(2)
        href_m = re.search(r'href="([^"]+)"', attrs)
        if not href_m:
            continue
        href = href_m.group(1)
        if "uddg=" in href:
            mm = re.search(r"uddg=([^&]+)", href)
            if mm:
                href = urllib.parse.unquote(mm.group(1))
        title = re.sub(r"<[^>]+>", "", inner).strip()
        if title:
            out.append({"source": "web", "title": title, "year": None, "doi": "",
                        "venue": "", "type": "web", "abstract": "", "url": href})
        if len(out) >= limit:
            break
    return out


def _wiki(query: str, limit: int):
    """Последняя ступень: энциклопедия. Явно помечается — это не научный источник."""
    url = ("https://en.wikipedia.org/w/api.php?action=query&list=search&format=json&srlimit="
           + str(limit) + "&srsearch=" + urllib.parse.quote(query))
    d = get_json(url)
    if not d:
        return []
    out = []
    for r in ((d.get("query") or {}).get("search") or []):
        out.append({"source": "wiki", "title": r.get("title") or "", "year": None, "doi": "",
                    "venue": "Wikipedia (энциклопедия, не источник)",
                    "type": "wiki", "abstract": re.sub(r"<[^>]+>", "", r.get("snippet") or ""),
                    "url": "https://en.wikipedia.org/wiki/" + urllib.parse.quote((r.get("title") or "").replace(" ", "_"))})
    return out


def src_web(query: str, limit: int, min_year: int | None):
    """Лестница: DDG html -> DDG lite -> Wikipedia. Возвращает (items, via) или None."""
    key = "web:" + query
    cached = _cache_get(key)
    if cached is not None:
        return cached
    ladder = (
        ("ddg-html", "https://duckduckgo.com/html/?q=" + urllib.parse.quote(query), _parse_ddg),
        ("ddg-lite", "https://lite.duckduckgo.com/lite/?q=" + urllib.parse.quote(query), _parse_ddg_lite),
    )
    for name, url, parser in ladder:
        html = _fetch(url)
        if not html:
            continue
        items = parser(html, limit)
        if items:
            _cache_put(key, items)
            return items
    items = _wiki(query, limit)
    if items:
        _cache_put(key, items)
        return items
    return None


SOURCES = {
    "openalex": src_openalex, "crossref": src_crossref, "arxiv": src_arxiv,
    "europepmc": src_europepmc, "datacite": src_datacite, "web": src_web, "wiki": lambda q, l, y: _wiki(q, l),
}


# ---------------------------------------------------------------- склейка

def score(item: dict, terms: list[str]) -> int:
    text = (item.get("title") or "") + " " + (item.get("abstract") or "")
    low = text.lower()
    return sum(1 for t in terms if t in low)


def search(query: str, sources: list[str], limit: int, min_year: int | None):
    terms = [w for w in re.findall(r"[a-zа-я0-9\-]{3,}", query.lower())]
    merged, per_source, failed = [], {}, []
    for name in sources:
        fn = SOURCES.get(name)
        if fn is None:
            failed.append((name, "неизвестный источник"))
            continue
        res = fn(query, limit, min_year)
        if res is None:
            failed.append((name, "недоступен"))
            continue
        per_source[name] = len(res)
        for item in res:
            item["score"] = score(item, terms)
            merged.append(item)

    # дедупликация: DOI, иначе нормализованное название
    seen_doi, seen_title, unique = set(), set(), []
    dropped_dup = 0
    for item in merged:
        doi = (item.get("doi") or "").lower()
        key_t = norm_title(item.get("title") or "")[:120]
        if (doi and doi in seen_doi) or (not doi and key_t and key_t in seen_title):
            dropped_dup += 1
            continue
        if doi:
            seen_doi.add(doi)
        if key_t:
            seen_title.add(key_t)
        unique.append(item)

    # фильтры: год, наличие идентификатора (для научных источников)
    kept, dropped_old, dropped_noid = [], 0, 0
    for item in unique:
        if min_year and item.get("year") and item["year"] < min_year:
            dropped_old += 1
            continue
        if item["source"] != "web" and not (item.get("doi") or item.get("url")):
            dropped_noid += 1
            continue
        kept.append(item)

    kept.sort(key=lambda x: (-x["score"], -(x.get("year") or 0)))
    return kept[:limit], {
        "per_source": per_source, "failed": failed, "dropped_dup": dropped_dup,
        "dropped_old": dropped_old, "dropped_noid": dropped_noid, "total_raw": len(merged),
    }


def verify(doi: str) -> int:
    ok = []
    for name, url in (("crossref", "https://api.crossref.org/works/" + urllib.parse.quote(doi)),
                      ("datacite", "https://api.datacite.org/dois/" + urllib.parse.quote(doi)),
                      ("openalex", "https://api.openalex.org/works/https://doi.org/" + urllib.parse.quote(doi))):
        d = get_json(url)
        ok.append((name, bool(d)))
    found = [n for n, v in ok if v]
    print(f"DOI {doi}: " + ("найден в " + ", ".join(found) if found else "НЕ найден ни в одном реестре"))
    for n, v in ok:
        print(f"  {n:10s} {'есть' if v else 'нет'}")
    return 0 if found else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="поиск литературы и веба без ключей")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search")
    s.add_argument("--query", required=True)
    s.add_argument("--sources", default="openalex,crossref,arxiv")
    s.add_argument("--limit", type=int, default=5)
    s.add_argument("--min-year", type=int, default=None)
    s.add_argument("--json", action="store_true")
    v = sub.add_parser("verify")
    v.add_argument("--doi", required=True)
    args = ap.parse_args(argv)

    if args.cmd == "verify":
        return verify(args.doi)

    sources = [x.strip() for x in args.sources.split(",") if x.strip()]
    items, stats = search(args.query, sources, args.limit, args.min_year)
    if args.json:
        print(json.dumps({"items": items, "stats": stats}, ensure_ascii=False, indent=2))
    else:
        print(f"запрос: {args.query}")
        print("источники: " + ", ".join(f"{k}={v}" for k, v in stats["per_source"].items())
              + (f" | недоступны: {', '.join(n for n, _ in stats['failed'])}" if stats["failed"] else ""))
        print(f"сырых: {stats['total_raw']} | дублей: {stats['dropped_dup']} | "
              f"старых: {stats['dropped_old']} | без id: {stats['dropped_noid']} | показано: {len(items)}")
        for i, it in enumerate(items, 1):
            print(f"\n{i}. [{it['source']}] {it['title']}")
            print(f"   {it.get('year') or '—'} · {it.get('venue') or '—'} · DOI {it.get('doi') or '—'} · релевантность {it['score']}")
            if it.get("abstract"):
                print("   " + it["abstract"][:280].replace("\n", " ") + ("…" if len(it["abstract"]) > 280 else ""))
        if not items:
            print("\nне нашлось выше порога; причины: " +
                  (", ".join(f"{n}: {r}" for n, r in stats["failed"]) or "все источники ответили пусто"))
    if items:
        return 0
    return 2 if stats["failed"] and not stats["per_source"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
