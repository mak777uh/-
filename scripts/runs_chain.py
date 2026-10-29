"""runs_chain.py — печать целостности манифестов прогонов (наш аналог аттестации TEE).

Откуда идея (28.10, docs.near.ai). Их облако доказывает, что вычисление прошло **в конкретной защищённой
среде**: клиент криптографически проверяет аттестацию, а не верит провайдеру. У нас нет TEE и нет внешнего
проверяющего, но есть тот же вопрос: **можно ли незаметно переписать след прогона?** Сейчас журнал
append-only, манифесты лежат в git, но подделка отдельного манифеста ничем не ловится, кроме `git log`.

Решение: **цепочка хешей** по манифестам `lab/runs/*.json` в порядке времени старта.

    entry_i = sha256(entry_{i-1} || run_id || status || sha256(содержимого манифеста))

Тогда любое изменение в любом манифесте ломает все последующие хеши. Локально цепочку можно пересчитать
(как и любую локальную подпись), но **в паре с git** это уже содержательно: чтобы подделать прогон, нужно
переписать историю, а не один файл.

Использование:
    python scripts/runs_chain.py --append   # дописать новые манифесты в цепочку
    python scripts/runs_chain.py --check    # проверить цепочку (CI)
    python scripts/runs_chain.py --check --strict   # расхождение = ошибка (код 1)
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "lab" / "runs"
CHAIN = ROOT / "lab" / "runs.chain.json"


def file_sha(path: Path) -> str:
    """sha256 содержимого с НОРМАЛИЗАЦИЕЙ переводов строк.

    Инцидент 29.10: цепочка сходилась локально (Windows, CRLF) и падала в CI (Ubuntu, LF): git отдаёт
    файлы с другими концами строк, и «изменился манифест» означало «изменился перевод строки».
    Перевод строки — не часть артефакта, поэтому хешируем каноническую форму.
    """
    data = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def entry_hash(prev: str, run_id: str, status: str, content_sha: str) -> str:
    payload = f"{prev}|{run_id}|{status}|{content_sha}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def load_chain() -> dict:
    if CHAIN.exists():
        return json.loads(CHAIN.read_text(encoding="utf-8"))
    return {"kind": "runs-chain", "note": "цепочка sha256 по манифестам lab/runs/", "entries": []}


def manifests() -> list[Path]:
    return sorted(RUNS.glob("*.json"), key=lambda p: (p.stat().st_mtime, p.name))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="печать целостности манифестов прогонов")
    ap.add_argument("--append", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args(argv)

    chain = load_chain()
    entries = chain.get("entries") or []
    known = {e["run_id"] for e in entries}
    prev = entries[-1]["hash"] if entries else ""

    if args.append:
        added = 0
        for path in manifests():
            rid = path.name[: -len(".json")]
            if rid in known:
                continue
            data = json.loads(path.read_text(encoding="utf-8"))
            status = str(data.get("status") or "unknown")
            if status == "running":
                # открытый манифест дописывается при завершении прогона — цеплять его рано
                continue
            h = entry_hash(prev, rid, status, file_sha(path))
            entries.append({"run_id": rid, "status": status, "content_sha256": file_sha(path),
                            "prev": prev, "hash": h})
            prev, added = h, added + 1
            known.add(rid)
        chain["entries"] = entries
        CHAIN.write_text(json.dumps(chain, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"[chain] дописано {added} записей, всего {len(entries)}")
        return 0

    # проверка: пересчитываем цепочку заново и сравниваем
    prev_check, problems = "", []
    for e in entries:
        recalculated = entry_hash(prev_check, e["run_id"], e["status"], e["content_sha256"])
        if recalculated != e["hash"]:
            problems.append(f"{e['run_id']}: хеш не сходится — манифест изменён или цепочка переписана")
        prev_check = recalculated

    for e in entries:
        path = RUNS / f"{e['run_id']}.json"
        if not path.exists():
            continue
        try:
            cur_status = str((json.loads(path.read_text(encoding="utf-8")) or {}).get("status") or "")
        except Exception:
            cur_status = ""
        if cur_status == "running":
            continue  # манифест ещё пишется — сверять рано
        if file_sha(path) != e["content_sha256"]:
            problems.append(f"{e['run_id']}: содержимое манифеста изменилось после записи в цепочку")

    closed_manifest_ids = []
    for p_ in manifests():
        try:
            st_ = str((json.loads(p_.read_text(encoding="utf-8")) or {}).get("status") or "")
        except Exception:
            st_ = ""
        if st_ != "running":
            closed_manifest_ids.append(p_.name[: -len(".json")])
    missing = [rid for rid in closed_manifest_ids if rid not in known]
    if missing:
        (problems if args.strict else []).append(f"{len(missing)} манифестов без записи в цепочке — запустите --append")
        if not args.strict:
            print(f"[chain] предупреждение: {len(missing)} манифестов без записи (запустите --append)")

    if problems:
        print(f"[chain] ОШИБКА: {len(problems)} проблем (записей {len(entries)})")
        for p in problems[:10]:
            print("   ", p)
        return 1
    print(f"[chain] OK — записей {len(entries)}, хеши сходятся, изменённых манифестов нет")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
