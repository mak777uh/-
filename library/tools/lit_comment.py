#!/usr/bin/env python
"""lit_comment.py — комментарий к результату с проверкой, а не «вот две статьи».

Проблема, которую решает: автомат умеет найти похожие работы, но не умеет сказать, ЧТО ЭТО МЕНЯЕТ.
Здесь — три уровня, и каждый честно помечен:

  1. **направление** — из абстракта вытаскивается, совпадает ли он с нашим результатом или расходится
     (по маркерам «no effect / does not / fail / instead» против «consistent / increases / supports»);
  2. **тип свидетельства** — `preprint` / `статья` / `обзор` (по типу Crossref и DOI);
  3. **что это меняет** — формулируется по ПРАВИЛУ, а не по вдохновению:
       совпало + статья      → «подтверждает, менять не надо»;
       совпало + preprint    → «подтверждает, но preprint — оговорка обязательна»;
       расходится + статья   → «расходится с каноном: либо у нас особый режим, либо ошибка — проверить»;
       не нашлось            → «канона нет: наше наблюдение, механизмом не называть».

Запуск:
  python library/tools/lit_comment.py --query "..." [--our-result "текст нашего вывода"]
  python library/tools/lit_comment.py --from-result <файл.json>   # взять запрос из result_lit
Коды: 0 — комментарий построен; 1 — нечего комментировать.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
LIT = REPO / "library" / "tools" / "lit_find.py"

AGREE = re.compile(r"\b(consistent with|supports?|confirms?|in line with|we show that|increases?|"
                   r"promotes?|enhances?|facilitates?)\b", re.I)
DISAGREE = re.compile(r"\b(no effect|does not|did not|fails? to|contrary|instead|"
                      r"challenge|refute|we find no)\b", re.I)
REVIEW = re.compile(r"\b(review|overview|survey|meta-analysis)\b", re.I)
# «сильный» домен: без него работа не наша, даже если в ней есть слово «resource».
# «mobility» в одиночку не годится — это транспорт; наш термин — movement/foraging/dispersal.
DOMAIN = re.compile(r"\b(agent-based|individual-based|reaction-diffusion|cellular automat\w*|"
                    r"partial differential|pattern formation|forag\w*|taxis|dispersal|"
                    r"coexist\w*|selection|lineage|demographic stochastic\w*|"
                    r"ideal free distribution|carrying capacity|population dynamics|"
                    r"ecological model|simulation model|numerical model)\b", re.I)
OFFDOMAIN = re.compile(r"\b(bear|cheetah|bushbaby|galago|bat|bird|fish|primate|livestock|patient|"
                       r"clinical|hospital|cancer|tumou?r|electric|automotive|vehicle|traffic|"
                       r"business|market|supply chain|energy policy)\b", re.I)
MOBILITY_FALSE = re.compile(r"\b(electric|urban|smart|sustainable|green)\s+mobility\b|"
                            r"\bmobility (plan|policy|service|management|solutions?)\b", re.I)


def in_domain(item: dict) -> bool:
    text = (item.get("title") or "") + " " + (item.get("abstract") or "")
    return (bool(DOMAIN.search(text)) and not OFFDOMAIN.search(text)
            and not MOBILITY_FALSE.search(text))


def fetch(query: str, limit: int = 3) -> list[dict]:
    out = subprocess.run([sys.executable, str(LIT), "search", "--query", query,
                          "--sources", "openalex,crossref,arxiv,europepmc",
                          "--limit", str(limit), "--json"],
                         capture_output=True, text=True, encoding="utf-8", cwd=REPO)
    if out.returncode != 0:
        return []
    try:
        data = json.loads(out.stdout)
    except Exception:
        return []
    return [i for i in data.get("items", []) if i.get("doi")][:limit]


def is_peer_review_artifact(item: dict) -> bool:
    """Рецензии и decision letters — не статьи: DOI оканчивается на /reviewN или /decisionN."""
    doi = (item.get("doi") or "").lower()
    title = (item.get("title") or "").lower()
    return (bool(re.search(r"/(review|decision)\d*$", doi))
            or bool(re.search(r"\.(sa|review|decision)\d+$", doi))   # eLife: .sa2, .review1
            or title.startswith("review for")
            or title.startswith("author response")
            or title.startswith("decision letter"))


def kind_of(item: dict) -> str:
    doi = item.get("doi") or ""
    if any(x in doi for x in ("10.1101/", "10.21203/", "10.48550/", "10.31234/", "10.2139/")):
        return "preprint"
    if REVIEW.search(item.get("title") or "") or REVIEW.search(item.get("abstract") or ""):
        return "обзор"
    return "статья"


def direction(item: dict) -> str:
    text = (item.get("abstract") or "") + " " + (item.get("title") or "")
    if DISAGREE.search(text):
        return "расходится"
    if AGREE.search(text):
        return "совпадает"
    return "неясно"


def verdict(direction_: str, kind: str) -> str:
    if kind == "preprint":
        return "подтверждает, но preprint — оговорка обязательна"
    if direction_ == "совпадает":
        return "подтверждает, менять не надо"
    if direction_ == "расходится":
        return "расходится с каноном: либо у нас особый режим, либо ошибка — проверить"
    return "направление не установлено по абстракту — читать вручную"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="комментарий к результату с проверкой")
    ap.add_argument("--query")
    ap.add_argument("--our-result", default="")
    ap.add_argument("--limit", type=int, default=2)
    args = ap.parse_args(argv)
    if not args.query:
        print("нужен --query")
        return 1

    raw = fetch(args.query, args.limit * 4)
    hits = [h for h in raw if in_domain(h) and not is_peer_review_artifact(h)]
    dropped = len(raw) - len(hits)
    if dropped:
        print(f"(отброшено не по домену: {dropped})")
    if not hits:
        print(f"запрос: {args.query}\nканона не нашлось → в сводку: наше наблюдение, механизмом не называть.")
        return 0

    print(f"запрос: {args.query}")
    if args.our_result:
        print(f"наш результат: {args.our_result}")
    print()
    for h in hits[: args.limit]:
        k = kind_of(h)
        d = direction(h)
        print(f"- {(h.get('title') or '')[:100]} ({h.get('year') or '?'}, {k})")
        print(f"  DOI: {h['doi']}")
        print(f"  направление: {d}")
        print(f"  → в сводку: {verdict(d, k)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
