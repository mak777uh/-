"""lit_index.py — локальный поисковик по полным текстам статей.

Зачем. К 31.10 у нас 20+ проверенных работ и 5 прочитанных целиком. Читать по одной — медленно, а помнить прочитанное
ещё медленнее. Нужен инструмент, который отвечает на вопрос «где в корпусе говорится про X» за секунды и показывает
цитату с контекстом, а не пересказ модели.

Что делает:
    python scripts/lit_index.py --add _hourly/fulltexts        # проиндексировать каталог (txt/pdf)
    python scripts/lit_index.py --search "discretization step"  # искать, с контекстом
    python scripts/lit_index.py --search "non-Platonic" --doc davis
    python scripts/lit_index.py --stats                        # что в индексе

Индекс — обратный, по нормализованным словам (нижний регистр, без пунктуации, простой стемминг суффиксов).
Хранится в `library/corpus/index.json`, тексты — в `library/corpus/texts/`. Без внешних зависимостей.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "library" / "corpus"
TEXTS = CORPUS / "texts"
INDEX = CORPUS / "index.json"

WORD = re.compile(r"[A-Za-zА-Яа-я][A-Za-zА-Яа-я\-]{2,}")
SUFFIXES = ("ization", "isation", "ation", "ments", "ment", "ings", "ing", "ies", "ed", "es", "s")


def stem(w: str) -> str:
    w = w.lower()
    for suf in SUFFIXES:
        if len(w) > len(suf) + 4 and w.endswith(suf):
            return w[: -len(suf)]
    return w


def words(text: str) -> list[str]:
    return [stem(m.group(0)) for m in WORD.finditer(text)]


def read_doc(path: Path) -> str | None:
    if path.suffix.lower() == ".txt":
        return path.read_text(encoding="utf-8", errors="replace")
    return None  # PDF извлекается отдельно (pypdf), сюда попадают уже тексты


def add_dir(src: Path, verbose: bool = True) -> int:
    TEXTS.mkdir(parents=True, exist_ok=True)
    index: dict = {"documents": {}, "terms": {}}
    if INDEX.is_file():
        index = json.loads(INDEX.read_text(encoding="utf-8"))
    added = 0
    for path in sorted(src.glob("*.txt")):
        name = path.stem
        target = TEXTS / path.name
        if not target.exists():
            target.write_text(path.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
        text = target.read_text(encoding="utf-8", errors="replace")
        # заголовок: первая непустая строка
        title = next((ln.strip() for ln in text.split("\n") if ln.strip()), name)[:160]
        index["documents"][name] = {"title": title, "chars": len(text), "path": str(target.relative_to(ROOT))}
        counts: dict[str, int] = {}
        for w in words(text):
            counts[w] = counts.get(w, 0) + 1
        for w, c in counts.items():
            index["terms"].setdefault(w, {})[name] = c
        added += 1
        if verbose:
            print(f"  + {name}: {len(text)} символов")
    INDEX.parent.mkdir(parents=True, exist_ok=True)
    INDEX.write_text(json.dumps(index, ensure_ascii=False), encoding="utf-8")
    return added


def search(query: str, doc_filter: str | None = None, context: int = 2, limit: int = 8) -> None:
    if not INDEX.is_file():
        print("индекса нет: сначала --add <каталог с .txt>")
        return
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    terms = [stem(w) for w in WORD.findall(query)]
    if not terms:
        print("пустой запрос"); return
    scores: dict[str, int] = {}
    for t in terms:
        for doc, c in (index["terms"].get(t) or {}).items():
            if doc_filter and doc_filter not in doc:
                continue
            scores[doc] = scores.get(doc, 0) + c
    if not scores:
        print(f"по запросу {query!r} ничего не найдено")
        return
    print(f"запрос {query!r}: документов {len(scores)}, слова {terms}")
    for doc, score in sorted(scores.items(), key=lambda kv: -kv[1])[:limit]:
        info = index["documents"][doc]
        print(f"\n=== {doc} (вес {score}) — {info['title'][:90]}")
        text = (ROOT / info["path"]).read_text(encoding="utf-8", errors="replace")
        # текст из PDF идёт сплошняком: ищем по окнам фиксированной длины и показываем самые плотные
        window = 320
        step = 160
        best = []
        for start in range(0, max(1, len(text) - window), step):
            chunk = text[start:start + window]
            ws = [stem(w) for w in WORD.findall(chunk.lower())]
            hits = sum(1 for t_ in terms if t_ in ws)
            if hits == 0:
                continue
            density = hits / (len(ws) or 1)
            best.append((hits, density, start, chunk))
        best.sort(key=lambda x: (-x[0], -x[1]))
        shown, used = 0, []
        for hits, _d, start, chunk in best:
            if any(abs(start - u) < window for u in used):
                continue
            used.append(start)
            clean = " ".join(chunk.split())
            print(f"  [слов {hits}] …{clean[:300]}…")
            shown += 1
            if shown >= 3:
                break


def stats() -> None:
    if not INDEX.is_file():
        print("индекса нет"); return
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    docs = index["documents"]
    total_terms = len(index["terms"])
    print(f"документов: {len(docs)} | уникальных терминов: {total_terms}")
    for name, info in sorted(docs.items()):
        print(f"  {name:34s} {info['chars']:7d} символов | {info['title'][:60]}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="поиск по полным текстам")
    ap.add_argument("--add", help="каталог с .txt для индексации")
    ap.add_argument("--search", help="запрос")
    ap.add_argument("--doc", help="ограничить документами, содержащими подстроку")
    ap.add_argument("--context", type=int, default=2)
    ap.add_argument("--stats", action="store_true")
    args = ap.parse_args(argv)
    if args.add:
        n = add_dir(Path(args.add))
        print(f"[lit] добавлено документов: {n}")
    if args.search:
        search(args.search, args.doc, args.context)
    if args.stats or (not args.add and not args.search):
        stats()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
