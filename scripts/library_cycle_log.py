"""Лог работы библиотекаря по циклу волны.

Зачем. «Библиотекарь отрабатывает в циклах?» — вопрос, на который нельзя отвечать
обещанием. Этот скрипт пересобирает человеческий лог из артефактов: какие файлы
библиотеки затронуты в каждой фазе волны (`library/`), какие замечания доски получили
решение, какие инсайты появились. Правится не руками, а переgeneration.

Источник: `lab/cycle.json` (`phase_history`), git, `lab/lit-board.json`,
`lab/insights.json`. Выход: `library/cycle-log.md`.

Команды:
  --write (по умолчанию)   перегенерировать `library/cycle-log.md`
  --print                  напечатать, не писать
  --root PATH              другой корень (для тестов)
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "library" / "cycle-log.md"
LIBRARY_PREFIXES = ("library/answers.md", "library/synthesis/", "library/review-", "library/board.md", "library/hypotheses/")


def _parse(value: str | None) -> dt.datetime | None:
    if not value:
        return None
    text = str(value).replace("Z", "+00:00")
    try:
        stamp = dt.datetime.fromisoformat(text)
    except ValueError:
        return None
    if stamp.tzinfo is None:
        stamp = stamp.replace(tzinfo=dt.timezone.utc)
    return stamp


def windows(history: list[dict], now: dt.datetime | None = None) -> list[dict]:
    """Фазы волны с интервалом [at, next_at); последняя — до сейчас."""
    now = now or dt.datetime.now(dt.timezone.utc)
    entries = [h for h in history if _parse(h.get("at"))]
    entries.sort(key=lambda h: _parse(h["at"]))
    out = []
    for i, entry in enumerate(entries):
        start = _parse(entry["at"])
        end = _parse(entries[i + 1]["at"]) if i + 1 < len(entries) else now
        out.append(
            {
                "phase": entry.get("phase"),
                "by": entry.get("by"),
                "start": start,
                "end": end,
                "note": entry.get("note"),
            }
        )
    return out


def git_files(start: dt.datetime, end: dt.datetime, root: pathlib.Path) -> list[str] | None:
    cmd = [
        "git",
        "-C",
        str(root),
        "log",
        "--name-only",
        "--pretty=format:",
        f"--since={start.isoformat()}",
        f"--until={end.isoformat()}",
        "--",
        "library/",
    ]
    try:
        out = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
    except (OSError, subprocess.CalledProcessError):
        return None
    return sorted({line.strip() for line in out.splitlines() if line.strip()})


def load_json(path: pathlib.Path, key: str = "items") -> list[dict]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return data.get(key, []) if isinstance(data, dict) else []


def events_for(window: dict, root: pathlib.Path) -> dict:
    files = git_files(window["start"], window["end"], root) or []
    useful = [f for f in files if any(f.startswith(p) for p in LIBRARY_PREFIXES)]
    board = []
    for item in load_json(root / "lab" / "lit-board.json"):
        if str(item.get("status")) not in {"accepted", "declined", "deferred", "done"}:
            continue
        raw = str(item.get("decided_at") or "")
        stamp = _parse(raw)
        # у доски решение часто записано только датой: к какой фазе его отнести — неизвестно,
        # поэтому такие решения показываются отдельной строкой, а не в фазе
        if not stamp or "T" not in raw:
            continue
        if window["start"] <= stamp < window["end"]:
            board.append(item)
    insights = []
    for item in load_json(root / "lab" / "insights.json"):
        stamp = _parse(item.get("created_at"))
        if stamp and window["start"] <= stamp < window["end"]:
            insights.append(item)
    return {"files": useful, "board": board, "insights": insights, "git_ok": files is not None}


def _short(path: str) -> str:
    return path.replace("library/", "", 1)


def summarize(events: dict) -> str:
    parts: list[str] = []
    if events["files"]:
        parts.append("файлы: " + ", ".join(_short(f) for f in events["files"][:6]))
    if events["board"]:
        parts.append("решения доски: " + ", ".join(f"{i.get('id')}→{i.get('status')}" for i in events["board"]))
    if events["insights"]:
        parts.append("инсайты: " + ", ".join(str(i.get("id")) for i in events["insights"]))
    if not parts:
        return "—"
    if not events["git_ok"]:
        parts.append("(git недоступен: файлы не проверены)")
    return "; ".join(parts)


def render(cycle: dict, root: pathlib.Path) -> str:
    history = cycle.get("phase_history") or []
    rows = []
    for window in windows(history):
        events = events_for(window, root) if window["start"] and window["end"] else {"files": [], "board": [], "insights": [], "git_ok": True}
        rows.append((window, events))
    lines = [
        "# Лог циклов: что делал библиотекарь",
        "",
        "> Сгенерировано из `lab/cycle.json`, git, `lab/lit-board.json` и `lab/insights.json`",
        "> командой `python scripts/library_cycle_log.py`. Руками не править.",
        "",
        f"- Волна: **{cycle.get('id')}** — {cycle.get('wave') or ''}",
        f"- Тип: `{cycle.get('type') or '?'}`; текущая фаза: `{cycle.get('phase')}`",
        f"- Гипотезы: {', '.join(map(str, cycle.get('hypothesis_ids') or [])) or '—'}",
        "",
        "| фаза | с | кто поставил | что сделал библиотекарь |",
        "| --- | --- | --- | --- |",
    ]
    for window, events in rows:
        start = window["start"].astimezone().strftime("%d.%m %H:%M") if window["start"] else "?"
        lines.append(
            f"| `{window['phase']}` | {start} | {window.get('by') or '—'} | {summarize(events)} |"
        )
    if not rows:
        lines.append("| — | — | — | истории фаз нет |")
    dated_only = [
        i
        for i in load_json(root / "lab" / "lit-board.json")
        if str(i.get("status")) in {"accepted", "declined", "deferred", "done"}
        and "T" not in str(i.get("decided_at") or "")
    ]
    if dated_only:
        lines += [
            "",
            "Решения доски, записанные только датой (к фазе не отнесены): "
            + ", ".join(f"{i.get('id')}→{i.get('status')}" for i in dated_only) + ".",
        ]

    notes = [w["note"] for w in windows(history) if w.get("note")]
    if notes:
        lines += ["", "## Что было сказано при смене фаз", ""]
        for window in windows(history):
            if window.get("note"):
                lines.append(f"- **{window['phase']}**: {window['note']}")
    lines += [
        "",
        "## Как читать",
        "",
        "Строка без файлов и решений означает, что фаза прошла без видимого выхода библиотеки.",
        "Если таких строк подряд больше двух — вопрос не к логу, а к циклу: фаза менялась,",
        "а работа не начиналась.",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Лог работы библиотекаря по циклу")
    ap.add_argument("--root", type=pathlib.Path, default=ROOT)
    ap.add_argument("--print", dest="print_only", action="store_true")
    args = ap.parse_args(argv)
    cycle_path = args.root / "lab" / "cycle.json"
    if not cycle_path.exists():
        print(f"нет {cycle_path}")
        return 0
    cycle = json.loads(cycle_path.read_text(encoding="utf-8"))
    text = render(cycle, args.root)
    if args.print_only:
        print(text)
        return 0
    out = args.root / "library" / "cycle-log.md"
    out.write_text(text, encoding="utf-8", newline="\n")
    print(f"обновлено: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
