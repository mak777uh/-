"""Поиск свежих публикаций по открытым вопросам библиотеки.

Зачем: обзор не должен зависеть от настроения и напоминаний. Одна команда — кандидаты из
Crossref с фильтрами, дальше библиотекарь отбирает 1–2 и заводит запись.

    python scripts/lit_search.py "negative frequency-dependent selection" --from 2023-01-01
    python scripts/lit_search.py "differentiable cellular automata" --from 2024-01-01 --rows 10
    python scripts/lit_search.py "priority effects" --from 2024-01-01 --only-abstract

Правила отбора (чтобы не тащить мусор):
* только `type:journal-article`, начиная с `--from` (по умолчанию 2023-01-01);
* выкидываются peer-review отчёты («Review for …», DOI с `/review`);
* с `--only-abstract` остаются только записи, у которых есть аннотация;
* вывод — год, DOI, журнал, заголовок; с `--abstract` — первые ~300 символов аннотации.

Ничего не пишет в репозиторий: только печатает кандидатов. Запись в библиотеку — вручную,
после проверки метаданных.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.parse
import urllib.request

API = "https://api.crossref.org/works"
UA = "morphogenesis-lit-search/1.0 (mailto:lab@example.org)"


def clean(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", text).strip()


def search(query: str, since: str, rows: int, only_abstract: bool, want_abstract: bool) -> list[dict]:
    params = {
        "query.bibliographic": query,
        "filter": f"from-pub-date:{since},type:journal-article",
        "rows": str(rows),
        "select": "DOI,title,issued,container-title,abstract,author",
        "mailto": "lab@example.org",
    }
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=45) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    out = []
    for item in data.get("message", {}).get("items", []):
        title = clean(" ".join(item.get("title") or []))
        doi = item.get("DOI", "")
        if not title or title.lower().startswith("review for") or "/review" in doi:
            continue
        abstract = clean(item.get("abstract", ""))
        if only_abstract and not abstract:
            continue
        year = (item.get("issued", {}).get("date-parts") or [[None]])[0][0]
        out.append(
            {
                "doi": doi,
                "year": year,
                "title": title,
                "journal": clean(" ".join(item.get("container-title") or [])),
                "authors": [a.get("family", "") for a in (item.get("author") or [])],
                "abstract": abstract if want_abstract else "",
            }
        )
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Поиск свежих публикаций (Crossref)")
    ap.add_argument("query")
    ap.add_argument("--from", dest="since", default="2023-01-01")
    ap.add_argument("--rows", type=int, default=8)
    ap.add_argument("--only-abstract", action="store_true")
    ap.add_argument("--abstract", action="store_true", help="печатать первые ~300 символов аннотации")
    args = ap.parse_args(argv)

    items = search(args.query, args.since, args.rows, args.only_abstract, args.abstract)
    if not items:
        print("кандидатов нет")
        return 0
    for it in items:
        authors = ", ".join(it["authors"][:3]) + (" et al." if len(it["authors"]) > 3 else "")
        print(f"{it['year']} | {it['doi']} | {it['journal']} | {it['title']}")
        if authors:
            print(f"     авторы: {authors}")
        if it["abstract"]:
            print(f"     ABS: {it['abstract'][:300]}…")
    print(f"\nвсего кандидатов: {len(items)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
