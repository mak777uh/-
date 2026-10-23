"""Очередь проверок литературы: срабатывает на «нам нужен параметр/механизм X».

Зачем: когда мы в рассуждении приходим к «нужен параметр, торгующий A против B», это
сигнал, что задача, скорее всего, уже сформулирована в науке (эволюция расселения,
идеальное свободное распределение, конкуренция за участки). Проверять надо не «когда
вспомним», а автоматически — по фразе-триггеру.

Что делает:
  --scan            пройтись по нашим текстам (отчёты, docs, _hourly/log.md), найти
                    фразы-триггеры и добавить новые записи в lab/lit-queue.json
  --add "текст"     добавить вручную; запросы генерируются из текста и типа триггера
  --list            показать очередь
  --done ID --result "что нашли"   закрыть запись с итогом

Типы триггеров и шаблоны запросов — в TRIGGERS ниже.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "lab" / "lit-queue.json"

TRIGGERS = [
    {
        "kind": "needs_parameter",
        "patterns": [
            r"нужен параметр",
            r"нужен механизм",
            r"нужно добавить",
            r"не хватает (механизма|параметра|сигнала)",
            r"нужен вес",
        ],
        "query_templates": [
            "{subject} trade-off model",
            "{subject} optimal policy evolution",
            "{subject} theoretical prediction",
        ],
    },
    {
        "kind": "negative_result",
        "patterns": [
            r"проигрыв",
            r"стало хуже",
            r"не сработало",
            r"эффекта нет",
            r"нулевой результат",
            r"не побил",
        ],
        "query_templates": [
            "{subject} why does it fail",
            "{subject} known limitations",
            "{subject} negative result",
        ],
    },
    {
        "kind": "about_to_sweep",
        "patterns": [r"свип", r"перебор", r"сетк[аи] параметров", r"попробуем разные"],
        "query_templates": [
            "{subject} closed form threshold",
            "{subject} dependence on population size",
        ],
    },
    {
        "kind": "claim_needs_check",
        "patterns": [
            r"не проверяли",
            r"нужно проверить",
            r"приоритет",
            r"не переносить",
            r"чужие \d",
        ],
        "query_templates": [
            "{subject} prior work",
            "{subject} already known",
        ],
    },
]

SUBJECT_HINTS = [
    (r"ресурс.{0,20}скученност|скученност.{0,20}ресурс", "resource vs crowding trade-off site selection"),
    (r"спор|потомств|размножен", "offspring dispersal site choice"),
    (r"мутац", "mutation rate error threshold"),
    (r"пластичност", "phenotypic plasticity adaptive value"),
    (r"смерт|выжива", "survival threshold mortality"),
]


def _load() -> dict:
    if QUEUE.exists():
        return json.loads(QUEUE.read_text(encoding="utf-8"))
    return {"updated_at": None, "items": []}


def _save(data: dict) -> None:
    data["updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    QUEUE.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def classify(text: str) -> list[str]:
    kinds = []
    for trigger in TRIGGERS:
        if any(re.search(p, text, re.IGNORECASE) for p in trigger["patterns"]):
            kinds.append(trigger["kind"])
    return kinds


def subject(text: str) -> str:
    for pattern, name in SUBJECT_HINTS:
        if re.search(pattern, text, re.IGNORECASE):
            return name
    return " ".join(text.split()[:6])


def make_queries(text: str, kinds: list[str]) -> list[str]:
    queries = []
    subj = subject(text)
    for trigger in TRIGGERS:
        if trigger["kind"] in kinds:
            queries.extend(q.format(subject=subj) for q in trigger["query_templates"])
    if not queries:
        queries = [f"{subj} prior work", f"{subj} model"]
    return list(dict.fromkeys(queries))


def add_item(data: dict, text: str, source: str = "manual") -> dict | None:
    kinds = classify(text)
    if not kinds:
        return None
    fingerprint = hashlib.sha1(text.strip().encode("utf-8")).hexdigest()[:10]
    if any(i["fingerprint"] == fingerprint for i in data["items"]):
        return None
    item = {
        "id": f"L-{len(data['items']) + 1:03d}",
        "fingerprint": fingerprint,
        "text": text.strip(),
        "source": source,
        "kinds": kinds,
        "queries": make_queries(text, kinds),
        "status": "new",
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "result": None,
    }
    data["items"].append(item)
    return item


def scan(data: dict) -> list[dict]:
    """Сканируем только документы текущей линии, не всю историю отчётов."""
    files = [
        ROOT / "docs" / "plan-alive.md",
        ROOT / "docs" / "world-design.md",
        ROOT / "docs" / "prior-art-alive.md",
    ]
    log = ROOT.parent / "_hourly" / "log.md"
    if log.exists():
        files.append(log)
    files = [f for f in files if f.exists()]
    added = []
    for path in files:
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        if path.name == "log.md" and len(lines) > 400:
            offset = len(lines) - 400
            lines = lines[offset:]
        for number, line in enumerate(lines, start=1):
            if len(line.strip()) < 20:
                continue
            item = add_item(data, line, source=f"{path.relative_to(ROOT.parent)}:{number}")
            if item:
                added.append(item)
    return added


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--add", default=None)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--done", default=None)
    ap.add_argument("--result", default="")
    args = ap.parse_args(argv)

    data = _load()
    if args.scan:
        added = scan(data)
        _save(data)
        print(f"добавлено триггеров: {len(added)}")
        for item in added[:10]:
            print(f"  {item['id']} [{','.join(item['kinds'])}] {item['text'][:80]}…")
        return 0
    if args.add:
        item = add_item(data, args.add)
        _save(data)
        if item:
            print(f"{item['id']}: {item['text'][:80]}")
            for q in item["queries"]:
                print(f"   запрос: {q}")
        else:
            print("триггер не распознан или уже есть")
        return 0
    if args.done:
        for item in data["items"]:
            if item["id"] == args.done:
                item["status"] = "done"
                item["result"] = args.result or "проверено"
                _save(data)
                print(f"{args.done}: закрыт")
                return 0
        print(f"{args.done}: не найдено")
        return 1
    # по умолчанию — список
    for item in data["items"]:
        mark = "✓" if item["status"] == "done" else "•"
        print(f"{mark} {item['id']} [{','.join(item['kinds'])}] {item['text'][:70]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
