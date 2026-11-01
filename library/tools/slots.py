#!/usr/bin/env python
"""slots.py — аудит слотов: какие из четырёх дневных слотов реально дали разбор.

Слоты: 09:30, 13:30, 17:30 (рабочие) и 21:40 (процесс+наука).
Признак слота: запись сканера `library/result-inbox.jsonl` в этот час ±60 мин,
либо `library/science-review-<дата>.md` для вечернего.

Зачем: пропуск слота сейчас ничем не наказывается и не виден; по числам видно, что 30–31.10
сканер запускался 1–2 раза в день вместо 3.
"""
from __future__ import annotations

import argparse
import datetime
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
INBOX = REPO / "library" / "result-inbox.jsonl"
SLOTS = (("09:30", 9 * 60 + 30), ("13:30", 13 * 60 + 30), ("17:30", 17 * 60 + 30), ("21:40", 21 * 60 + 40))
WINDOW = 75  # минут


def minutes(at: str):
    try:
        hh, mm = at[11:16].split(":")
        return int(hh) * 60 + int(mm)
    except Exception:
        return None


def audit(day: str, now_min: int | None = None) -> list[tuple[str, bool, str]]:
    records = []
    if INBOX.exists():
        for line in INBOX.read_text(encoding="utf-8").splitlines():
            try:
                rec = json.loads(line)
            except Exception:
                continue
            if (rec.get("at") or "").startswith(day):
                records.append(rec["at"])
    evening = (REPO / "library" / f"science-review-{day}.md").exists()
    now = datetime.datetime.now()
    is_today = day == now.date().isoformat()
    if now_min is None:
        now_min = now.hour * 60 + now.minute
    out = []
    for name, target in SLOTS:
        if is_today and now_min < target:
            out.append((name, True, "ещё не наступил"))  # будущий слот не считается пропуском
            continue
        hit = any(m is not None and abs(m - target) <= WINDOW for m in map(minutes, records))
        if name == "21:40":
            hit = hit or evening
        out.append((name, hit, "запись есть" if hit else "записи нет"))
    return out


def _now_min(value: str | None):
    if not value:
        return None
    hh, mm = value.split(":")
    return int(hh) * 60 + int(mm)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="аудит слотов")
    ap.add_argument("--date", default=datetime.date.today().isoformat())
    ap.add_argument("--days", type=int, default=1)
    ap.add_argument("--now", default=None, help="HH:MM — проверить как в это время (для тестов)")
    args = ap.parse_args(argv)
    start = datetime.date.fromisoformat(args.date)
    worse = 0
    for k in range(args.days):
        day = (start - datetime.timedelta(days=k)).isoformat()
        res = audit(day, _now_min(args.now))
        missed = [n for n, ok, _ in res if not ok]
        print(f"{day}: " + " ".join(f"{n}{'+' if ok else '-'}" for n, ok, _ in res)
              + (f" | пропущено: {', '.join(missed)}" if missed else " | все слоты"))
        worse += len(missed)
    print(f"пропусков всего: {worse}")
    return 0 if worse == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
