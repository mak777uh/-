"""log_signal_scan.py — майнер логов прогонов (LDD): какие сбои повторяются.

Зачем (LDD, 27.10). За сутки четыре раза прогон умирал «тихо»: `OSError: [Errno 22]
Invalid argument` при записи в закрытый пайп (PowerShell `*>>` тоже пайп). Каждый раз
это находил человек, вручную открыв `.log`. Логи у нас есть — нет их чтения.

Что делает: сканирует `morphogenesis/logs/*.log` на известные сигнатуры сбоев и
печатает таблицу «сигнатура → прогонов → последний случай → есть ли разбор».
Возвращает ⚠-уровень (не ❌): шум в логах не должен быть блокером.

Использование:
    python scripts/log_signal_scan.py                 # таблица
    python scripts/log_signal_scan.py --json out.json # машинный вид
    python scripts/log_signal_scan.py --since 2026-10-26
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOGS = ROOT / "morphogenesis" / "logs"
INCIDENTS = ROOT / "docs" / "incidents.md"

SIGNATURES = {
    "OSError / Invalid argument": re.compile(r"OSError.*Invalid argument"),
    "OSError (любой)": re.compile(r"OSError"),
    "Traceback": re.compile(r"Traceback \(most recent call last\)"),
    "CUDA out of memory": re.compile(r"CUDA out of memory"),
    "NaN / inf в сводке": re.compile(r"\bNaN\b|\binf\b"),
    "artifact=НЕТ / нет артефакта": re.compile(r"artifact=\S*НЕТ|нет артефакта"),
    "замок занят": re.compile(r"Замок: .*возраст"),
}


def scan(since: dt.date | None = None) -> dict:
    hits: dict[str, list[dict]] = {name: [] for name in SIGNATURES}
    files = sorted(LOGS.glob("*.log")) if LOGS.exists() else []
    for path in files:
        mtime = dt.date.fromtimestamp(path.stat().st_mtime)
        if since and mtime < since:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for name, rx in SIGNATURES.items():
            m = rx.search(text)
            if m:
                line = text[max(0, m.start() - 80):m.end() + 80].replace("\n", " ")
                hits[name].append({"log": path.name, "date": mtime.isoformat(), "snippet": line[:160]})
    return {
        "kind": "log-signal-scan",
        "scanned_logs": len(files),
        "signatures": {k: {"count": len(v), "last": (v[-1] if v else None)} for k, v in hits.items()},
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--since", help="YYYY-MM-DD")
    ap.add_argument("--json", help="куда записать машинный вид")
    args = ap.parse_args(argv)
    since = dt.date.fromisoformat(args.since) if args.since else None
    res = scan(since)
    has_incidents = INCIDENTS.exists()
    print(f"[log-scan] логов просмотрено: {res['scanned_logs']}"
          + (f" (с {args.since})" if since else "")
          + f" | разборы: {'есть' if has_incidents else 'нет'}")
    for name, info in res["signatures"].items():
        if not info["count"]:
            continue
        last = info["last"] or {}
        print(f"  ⚠ {name}: {info['count']} прогонов | последний {last.get('date')} ({last.get('log')})")
    if args.json:
        Path(args.json).write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n",
                                   encoding="utf-8", newline="\n")
        print(f"  записано: {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
