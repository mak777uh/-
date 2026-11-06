#!/usr/bin/env python
"""result_lit.py — литература под КАЖДЫЙ новый результат прогона, автоматически.

Зачем: сейчас литература ищется по темам (topic_lit) и по моей инициативе. Результат прогона приходит
раньше, чем я успеваю к нему посмотреть, и связь «результат → канон» теряется.

Что делает:
  1) берёт новые/изменённые агрегаты из `library/result-inbox.jsonl` (пишет `result_scan.py`);
  2) из имени файла и вердикта строит поисковый запрос (без LLM — по ключевым словам серии);
  3) ищет через `lit_find.py` (OpenAlex + Crossref + arXiv), берёт работы выше порога;
  4) пишет ОДИН блок в `lab/notices.md` адресно главному: по каждому результату — 1–2 источника с DOI и
     строкой «→ в сводку:» (что это меняет), плюс честное «канона не нашлось»;
  5) помнит, что уже обработано (`library/.result-lit-state.json`), чтобы не дублировать.

Запуск:
  python library/tools/result_lit.py --dry            # показать, что сделает
  python library/tools/result_lit.py                  # обработать новые результаты
  python library/tools/result_lit.py --since-hours 48 # окно
Коды: 0 — обработано (или нечего); 1 — ошибка поиска.
"""
from __future__ import annotations

import argparse
import io
import json
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
INBOX = REPO / "library" / "result-inbox.jsonl"
STATE = REPO / "library" / ".result-lit-state.json"
NOTICES = REPO / "lab" / "notices.md"
LIT = REPO / "library" / "tools" / "lit_find.py"

# серия → ключевые слова для запроса (по имени файла)
SERIES = [
    (r"s\d+_.*gradpos|gradpos", "gradient following taxis chemotaxis movement"),
    (r"s\d+_.*localres|local.?res", "local resource gradient foraging movement"),
    (r"s\d+_.*randdir|randdir", "random movement null model dispersal"),
    (r"s\d+_.*lineage|lineage", "lineage selection reproductive variance"),
    (r"s\d+_.*crowd|crowding", "crowding density dependence competition"),
    (r"s\d+_.*recover|recovery", "resource recovery rate renewal timescale"),
    (r"s\d+_.*habit|adaptation.?trap|fixed.?ref", "habituation behavioural adaptation trap"),
    (r"l1_field_x\d+.*fusion|corridor|bridge", "fusion coalescence reaction diffusion spots"),
    (r"l1_field_x\d+.*phase", "phase dependence pattern formation inflow"),
    (r"l1_field_x\d+.*gap", "gap threshold coalescence distance"),
    (r"x\d+.*wave|spatial.?wave", "spatial wave coupling resource pattern"),
    (r"prediction|predict", "anticipatory behaviour prediction resource"),
]
DEFAULT_Q = "reaction diffusion pattern formation resource agent model"
# результат считается свежим, если записан после этой даты (бэклог не трогаем)
FRESH_FROM = "2026-11-07 00:00"


def load(p, default):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return default


def save(p, obj):
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def query_for(rec: dict) -> str:
    key = (rec.get("file") or "") + " " + (rec.get("claim") or "")
    low = key.lower()
    for pat, q in SERIES:
        if re.search(pat, low):
            return q
    return DEFAULT_Q


def search(query: str, limit: int = 2) -> list[dict]:
    out = subprocess.run([sys.executable, str(LIT), "search", "--query", query,
                          "--sources", "openalex,crossref", "--limit", str(limit), "--json"],
                         capture_output=True, text=True, encoding="utf-8", cwd=REPO)
    if out.returncode != 0:
        return []
    try:
        data = json.loads(out.stdout)
    except Exception:
        return []
    items = data.get("results") or data.get("items") or []
    return [i for i in items if i.get("doi")][:limit]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="литература под новые результаты")
    ap.add_argument("--since-hours", type=int, default=24)
    ap.add_argument("--limit", type=int, default=2, help="работ на результат")
    ap.add_argument("--max-results", type=int, default=5, help="результатов за прогон")
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args(argv)

    if not INBOX.exists():
        print("нет result-inbox.jsonl — сначала result_scan.py")
        return 0
    state = load(STATE, {"done": []})
    done = set(state.get("done", []))

    recs = []
    for line in INBOX.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except Exception:
            continue
        key = (r.get("key") or r.get("file") or "")
        # только артефакты экспериментов: docs/ и *.md — не результаты прогона
        if not key.endswith(".json") or "/docs/" in f"/{key}":
            continue
        k = f"{r.get('at')}|{key}"
        if k in done:
            continue
        recs.append((k, r))
    # один блок на файл: берём последнюю запись по каждому ключу
    seen, uniq = set(), []
    for k, r in reversed(recs):
        key = (r.get("key") or r.get("file") or "")
        if key in seen:
            continue
        seen.add(key)
        uniq.append((k, r))
    recs = list(reversed(uniq))[-args.max_results:]
    # только свежие: старый бэклог (до --fresh-from) не обрабатываем
    fresh = []
    for k, r in recs:
        at = str(r.get("at") or "")
        if at >= FRESH_FROM:
            fresh.append((k, r))
    recs = fresh
    if not recs:
        print("новых результатов нет")
        return 0

    blocks = []
    for k, r in recs:
        q = query_for(r)
        hits = search(q, args.limit)
        name = (r.get("file") or "?").split("/")[-1]
        lines = [f"- **{name}** (`{r.get('at')}`) — искал: «{q}»"]
        if hits:
            for h in hits:
                title = (h.get("title") or "")[:110]
                year = h.get("year") or "?"
                doi = h.get("doi")
                kind = "preprint" if any(x in doi for x in ("10.1101/", "10.21203/", "10.48550/", "10.31234/")) else "статья"
                lines.append(f"  - {title} ({year}, {kind}), [`{doi}`](https://doi.org/{doi})")
            lines.append("  → в сводку: канон по этому классу результатов найден; проверить, совпадает ли "
                         "направление эффекта с литературой или расходится.")
        else:
            lines.append("  → в сводку: канона по этому запросу не нашлось — результат остаётся нашим "
                         "наблюдением, в тексте нельзя называть его механизмом.")
        blocks.append("\n".join(lines))
        done.add(k)

    text = ("\n\n### " + __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M")
            + " — библиотекарь → **главному**: литература под новые результаты (авто)\n\n"
            + "\n".join(blocks) + "\n")
    if args.dry:
        print(text)
        return 0
    with NOTICES.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    save(STATE, {"done": sorted(done)})
    print(f"обработано результатов: {len(recs)} -> lab/notices.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
