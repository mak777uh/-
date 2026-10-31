"""literature_harvest.py — собрать настоящие работы по теме, с аннотациями и ссылками на полные тексты.

Зачем. 31.10 пришёл каталог из 19 «случаев», составленный языковой моделью: шесть ссылок не существовало, две
существующие говорили о другом. Проверять чужие списки по одной ссылке — медленно; правильнее **собрать корпус
самому** из регистров, где работа точно есть, и сразу с открытыми версиями, чтобы читать, а не верить.

Источник — OpenAlex: он отдаёт название, год, журнал, число цитирований, **аннотацию** (в инвертированном виде) и
`best_oa_location` — ссылку на бесплатный полный текст, если он есть. Никакого ключа не нужно.

Запуск:
    python scripts/literature_harvest.py --queries queries.txt --out docs/lit-artifacts.json
    python scripts/literature_harvest.py --query "simulation artifact evolution" --rows 5
"""
from __future__ import annotations

import argparse
import json
import urllib.parse
import time
import urllib.request
from pathlib import Path

API = "https://api.openalex.org/works"
UA = "morphogenesis-lab/1.0 (literature harvest; mailto:noreply@example.org)"
SELECT = ("id,doi,title,publication_year,cited_by_count,type,"
          "primary_location,best_oa_location,abstract_inverted_index,authorships")


def _get(url: str, timeout: int = 45) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def abstract(inv: dict | None) -> str:
    if not inv:
        return ""
    pos: dict[int, str] = {}
    for word, idxs in inv.items():
        for i in idxs:
            pos[i] = word
    return " ".join(pos[i] for i in sorted(pos))


def harvest(query: str, rows: int = 10, attempts: int = 3) -> list[dict]:
    url = (f"{API}?search={urllib.parse.quote(query)}&per-page={rows}"
           f"&select={SELECT}&sort=relevance_score:desc")
    data = None
    for attempt in range(attempts):
        try:
            data = _get(url)
            break
        except Exception as e:
            if attempt == attempts - 1:
                print(f"[harvest] запрос {query!r}: ошибка {e} — пропущен")
                return []
            time.sleep(2.0 * (attempt + 1))
    if data is None:
        return []
    out = []
    for w in data.get("results") or []:
        best = w.get("best_oa_location") or {}
        prim = w.get("primary_location") or {}
        src = (prim.get("source") or {}).get("display_name")
        out.append({
            "query": query,
            "doi": (w.get("doi") or "").replace("https://doi.org/", ""),
            "title": w.get("title"),
            "year": w.get("publication_year"),
            "venue": src,
            "type": w.get("type"),
            "cited_by": w.get("cited_by_count"),
            "oa_url": best.get("pdf_url") or best.get("landing_page_url"),
            "landing": prim.get("landing_page_url"),
            "authors": ", ".join(
                (a.get("author") or {}).get("display_name", "")
                for a in (w.get("authorships") or [])[:4]
            ),
            "abstract": abstract(w.get("abstract_inverted_index")),
        })
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="сбор настоящих работ с полными текстами")
    ap.add_argument("--query", help="один запрос")
    ap.add_argument("--queries", help="файл: по одному запросу в строке")
    ap.add_argument("--rows", type=int, default=10)
    ap.add_argument("--out", help="куда записать JSON")
    args = ap.parse_args(argv)

    queries: list[str] = []
    if args.queries:
        queries = [ln.strip() for ln in Path(args.queries).read_text(encoding="utf-8").split("\n")
                   if ln.strip() and not ln.startswith("#")]
    elif args.query:
        queries = [args.query]
    else:
        ap.print_help()
        return 2

    seen: dict[str, dict] = {}
    for i, q in enumerate(queries):
        if i:
            time.sleep(0.6)
        got = harvest(q, args.rows)
        new = 0
        for item in got:
            key = item["doi"] or (item["title"] or "").lower()
            if key not in seen:
                seen[key] = item
                new += 1
        print(f"[harvest] {q!r}: найдено {len(got)}, новых {new}")

    items = sorted(seen.values(), key=lambda x: -(x["cited_by"] or 0))
    with_oa = sum(1 for x in items if x["oa_url"])
    print(f"[harvest] всего уникальных: {len(items)} | с открытым полным текстом: {with_oa}")

    if args.out:
        Path(args.out).write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n",
                                  encoding="utf-8", newline="\n")
        print(f"[harvest] записано: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
