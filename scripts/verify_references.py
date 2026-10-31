"""verify_references.py — проверить ссылку по названию, не доверяя памяти и не имея веб-поиска.

Зачем. 31.10 пришёл каталог из 19 «задокументированных случаев», составленный языковой моделью. Вставлять такие
ссылки в статью нельзя, пока они не проверены, а плагин веб-поиска в тот момент отвечал ошибкой авторизации.
Сеть у машины при этом есть: работают Crossref API и Zenodo API. Этот скрипт задаёт вопрос издательским
регистрам напрямую и печатает, что там есть:

* **Crossref** (`api.crossref.org`) — журналы и конференции с DOI;
* **DataCite** (`api.datacite.org`) — Zenodo, Dryad и прочие репозитории (у них DOI другого регистра).

Проверка не доказывает, что работа говорит то, что ей приписывают, — она доказывает, что работа **существует** и
называется так. Содержание всё равно читает человек.

Запуск:
    python scripts/verify_references.py --query "Surprising Creativity of Digital Evolution"
    python scripts/verify_references.py --file references.json      # [{id, query, claimed}, ...]
    python scripts/verify_references.py --file references.json --write out.json
"""
from __future__ import annotations

import argparse
import json
import urllib.parse
import urllib.request
from pathlib import Path

REGISTERS = {
    "crossref": "https://api.crossref.org/works?rows={rows}&select=DOI,title,container-title,issued,author"
                "&query.bibliographic={q}",
    "datacite": "https://api.datacite.org/dois?page[size]={rows}&query={q}",
}
UA = "morphogenesis-lab/1.0 (reference verification; mailto:noreply@example.org)"


def _get(url: str, timeout: int = 40) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def crossref(query: str, rows: int = 3) -> list[dict]:
    url = REGISTERS["crossref"].format(rows=rows, q=urllib.parse.quote(query))
    data = _get(url)
    out = []
    for it in (data.get("message", {}).get("items") or []):
        out.append({
            "register": "crossref",
            "doi": it.get("DOI"),
            "title": " ".join(it.get("title") or []),
            "venue": " ".join(it.get("container-title") or []),
            "year": (it.get("issued", {}).get("date-parts") or [[None]])[0][0],
            "authors": ", ".join(
                f"{a.get('family', '')} {a.get('given', '')}".strip()
                for a in (it.get("author") or [])[:4]
            ),
        })
    return out


def datacite(query: str, rows: int = 3) -> list[dict]:
    url = REGISTERS["datacite"].format(rows=rows, q=urllib.parse.quote(query))
    try:
        data = _get(url)
    except Exception:
        return []
    out = []
    for it in (data.get("data") or []):
        attr = it.get("attributes") or {}
        titles = attr.get("titles") or [{}]
        out.append({
            "register": "datacite",
            "doi": attr.get("doi"),
            "title": titles[0].get("title") if titles else "",
            "venue": (attr.get("publisher") or ""),
            "year": attr.get("publicationYear"),
            "authors": ", ".join((c.get("name") or "") for c in (attr.get("creators") or [])[:4]),
        })
    return out


def verify(query: str, rows: int = 3) -> dict:
    found = crossref(query, rows)
    if not found:
        found = datacite(query, rows)
    else:
        found += datacite(query, 1)
    return {"query": query, "found": found}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="проверка ссылок по названию через Crossref/DataCite")
    ap.add_argument("--query", help="одна строка поиска")
    ap.add_argument("--file", help="JSON: [{id, query, claimed}, ...]")
    ap.add_argument("--rows", type=int, default=3)
    ap.add_argument("--write", help="куда записать результат (JSON)")
    args = ap.parse_args(argv)

    items = []
    if args.file:
        items = json.loads(Path(args.file).read_text(encoding="utf-8"))
    elif args.query:
        items = [{"id": "query", "query": args.query, "claimed": None}]
    else:
        ap.print_help()
        return 2

    results = []
    for it in items:
        res = verify(it["query"], args.rows)
        res["id"] = it.get("id")
        res["claimed"] = it.get("claimed")
        results.append(res)
        print(f"\n[{it.get('id')}] {it['query']}")
        if it.get("claimed"):
            print(f"   заявлено: {it['claimed']}")
        if not res["found"]:
            print("   НЕ НАЙДЕНО ни в Crossref, ни в DataCite")
        for f in res["found"]:
            print(f"   → {f['doi']} | {f['year']} | {f['title'][:80]} | {f['venue'][:40]}")

    if args.write:
        Path(args.write).write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n",
                                    encoding="utf-8", newline="\n")
        print(f"\n[refs] записано: {args.write}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
