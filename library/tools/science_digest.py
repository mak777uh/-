#!/usr/bin/env python
"""Суточный научный дайджест: что установлено, что сломалось, что делать.

Отличие от `scripts/self_review.py`: тот считает ПРОЦЕСС (коммиты, правки, тесты), а этот —
НАУКУ: какие агрегаты изменились, какие выводы усилились/ослабли, какие числа противоречат
друг другу, какие рекомендации следуют ИЗ ЦИФР.

Принципы:
1. каждый факт берётся из артефакта (JSON) или git, а не из прозы;
2. каждая рекомендация несёт основание (число/поле), цену и способ проверки;
3. повтор не выдаётся: состояние в `library/.digest-state.json`, хэш рекомендации.

Запуск:
  python library/tools/science_digest.py            # за сегодня
  python library/tools/science_digest.py --date 2026-10-25
  python library/tools/science_digest.py --dry      # печать без записи
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import re
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "library"
STATE = OUT / ".digest-state.json"

AGG_GLOBS = (
    "morphogenesis/experiments/**/*matrix*.json",
    "morphogenesis/experiments/**/analysis/*.json",
    "morphogenesis/experiments/**/*_matrix.json",
)


def git(*args: str) -> str:
    try:
        return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=60).stdout
    except Exception:
        return ""


def commits_since(day: str) -> list[dict]:
    out = git("log", f"--since={day} 00:00", "--until={}".format(day) + " 23:59", "--format=%h|%s")
    rows = []
    for line in out.splitlines():
        if "|" in line:
            sha, subject = line.split("|", 1)
            rows.append({"sha": sha, "subject": subject})
    return rows


def changed_aggregates(day: str) -> list[str]:
    out = git("log", f"--since={day} 00:00", "--name-only", "--format=")
    files = {line.strip() for line in out.splitlines() if line.strip()}
    hits = []
    for f in sorted(files):
        if not f.endswith(".json"):
            continue
        if any(p in f for p in ("matrix", "/analysis/", "_matrix")):
            hits.append(f)
    return hits


def aggregate_summary(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    if not isinstance(data, dict):
        return {}
    out: dict = {}
    if "by_arm" in data and isinstance(data["by_arm"], list):
        for arm in data["by_arm"]:
            name = arm.get("arm")
            if name:
                out[name] = {k: arm.get(k) for k in
                             ("runs", "survived_k", "valid_n", "crow_I_median", "rho_median",
                              "placement_ok_k", "rejected_k")
                             if k in arm}
    if "criteria" in data and isinstance(data["criteria"], dict):
        out["__criteria__"] = {k: v for k, v in data["criteria"].items()
                               if isinstance(v, (bool, int, float, str))}
    if "result" in data and isinstance(data["result"], dict):
        out["__result__"] = {k: v for k, v in data["result"].items()
                             if isinstance(v, (bool, int, float, str))}
    return out


def board_delta(day: str) -> dict:
    path = REPO / "lab" / "lit-board.json"
    if not path.exists():
        return {}
    items = json.loads(path.read_text(encoding="utf-8")).get("items", [])
    new = [i for i in items if str(i.get("created_at", ""))[:10] == day]
    decided = [i for i in items if str(i.get("decided_at", ""))[:10] == day]
    return {"new": len(new), "decided": len(decided),
            "accepted": sum(1 for i in decided if i.get("status") == "accepted"),
            "declined": sum(1 for i in decided if i.get("status") == "declined"),
            "deferred": sum(1 for i in decided if i.get("status") == "deferred")}


def lit_delta() -> tuple[int, list[str]]:
    """Давление литературы и топ-цели (тот же источник, что lit_pressure)."""
    try:
        out = subprocess.run([sys.executable, "scripts/lit_pressure.py"], cwd=REPO,
                             capture_output=True, text=True, encoding="utf-8",
                             errors="replace", timeout=120)
    except Exception:
        return 0, []
    pressure = 0
    targets: list[str] = []
    for line in out.stdout.splitlines():
        m = re.search(r"литдавление:\s*(\d+)", line)
        if m:
            pressure = int(m.group(1))
        if "открытые lit-пункты" in line or "открытые вопросы" in line:
            targets.append(line.strip())
    return pressure, targets


def recommendations(aggs: dict, board: dict, pressure: int, day: str) -> list[dict]:
    recs: list[dict] = []

    def add(rid: str, action: str, basis: str, cost: str, check: str) -> None:
        recs.append({"id": rid, "action": action, "basis": basis, "cost": cost, "check": check,
                     "hash": hashlib.sha1(f"{rid}|{basis}".encode()).hexdigest()[:12]})

    for name, summary in aggs.items():
        crit = summary.get("__criteria__") or {}
        arms = {k: v for k, v in summary.items() if not k.startswith("__")}
        # 1) серия невалидна по данным/постановке
        for key in ("invalid_by_data", "invalid_by_placement", "placement_series_valid"):
            val = crit.get(key)
            broken = (val is False) if key == "placement_series_valid" else (val is True)
            if broken:
                add(f"invalid:{name}", f"починить постановку серии по {name}, вердикт не выносить",
                    f"criteria.{key} = {crit.get(key)}", "1 цикл",
                    f"повторный прогон/пересборка {name}: criteria.{key} = true")
        # 2) пропуск проверки (нет команды сборки / отложено)
        if crit.get("note") and "не выносится" in str(crit.get("note")):
            add(f"gate:{name}", f"не публиковать числа {name} до выполнения gate-условия",
                f"criteria.note = {str(crit.get('note'))[:80]}", "—",
                "criteria.note без «не выносится»")
        # 3) слабая мощность (валидных мало)
        for arm, s in arms.items():
            valid = s.get("valid_n")
            runs = s.get("runs")
            if isinstance(valid, int) and isinstance(runs, int) and runs and valid / runs < 0.5:
                add(f"power:{name}:{arm}",
                    f"добрать линии/сиды для {name}/{arm}: валидных {valid}/{runs}",
                    f"valid_n={valid} из runs={runs} (порог 0.5)", "1 серия",
                    "valid_n/runs >= 0.5")
    if pressure >= 3:
        add("lit:pressure", f"запустить литературный слот: давление {pressure}",
            f"lit_pressure = {pressure} (порог 3)", "15 мин", "слот отработал, давление < 3")
    if board.get("accepted", 0) >= 3:
        add("board:accepted", "проверить, что принятые пункты реализованы (не только приняты)",
            f"принято {board['accepted']} за сутки", "15 мин",
            "гейт «принято, но не сделано» зелёный")
    return recs


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Суточный научный дайджест")
    ap.add_argument("--date", default=date.today().isoformat())
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args(argv)
    day = args.date

    commits = commits_since(day)
    aggs_files = changed_aggregates(day)
    aggs = {}
    for rel in aggs_files:
        p = REPO / rel
        if p.exists():
            summary = aggregate_summary(p)
            if summary:
                aggs[Path(rel).stem] = summary
    board = board_delta(day)
    pressure, targets = lit_delta()
    recs = recommendations(aggs, board, pressure, day)

    state = {}
    if STATE.exists():
        try:
            state = json.loads(STATE.read_text(encoding="utf-8"))
        except Exception:
            state = {}
    prev_crit = state.get("criteria", {}) if isinstance(state.get("criteria"), dict) else {}
    flips: list[str] = []
    for name, summary in aggs.items():
        crit = {k: v for k, v in (summary.get("__criteria__") or {}).items()
                if isinstance(v, (bool, int, float))}
        old = prev_crit.get(name, {})
        for key, value in crit.items():
            if key in old and old[key] != value:
                flips.append(f"{name}.{key}: {old[key]} → {value}")
    seen = set(state.get("hashes", []))
    fresh = [r for r in recs if r["hash"] not in seen]

    lines = [f"# Научный дайджест за {day}", "",
             f"Коммитов за сутки: **{len(commits)}**. Изменённых агрегатов: **{len(aggs)}**.",
             ""]
    if commits:
        lines.append("## Что сделано (по коммитам)")
        for c in commits[:25]:
            lines.append(f"- `{c['sha']}` {c['subject'][:110]}")
        lines.append("")
    if aggs:
        lines.append("## Что изменилось в числах (агрегаты)")
        for name, summary in aggs.items():
            crit = summary.get("__criteria__") or {}
            bits = ", ".join(f"{k}={v}" for k, v in list(crit.items())[:4] if not isinstance(v, dict))
            lines.append(f"- **{name}**: {bits or 'без criteria'}")
        lines.append("")
    if flips:
        lines.append("## Что перевернулось в выводах (с прошлого прогона)")
        for f in flips[:12]:
            lines.append(f"- {f}")
        lines.append("")
    lines.append("## Рекомендации (из чисел, не из прозы)")
    if fresh:
        for r in fresh:
            lines.append(f"- **{r['action']}**  ")
            lines.append(f"  основание: `{r['basis']}`; цена: {r['cost']}; проверка: {r['check']}")
    else:
        lines.append("- новых рекомендаций нет (все уже выдавались и не закрыты)")
    lines.append("")
    lines.append("## Доска и литература")
    lines.append(f"- новых замечаний: {board.get('new', 0)}; решено: {board.get('decided', 0)} "
                 f"(принято {board.get('accepted', 0)}, отклонено {board.get('declined', 0)})")
    lines.append(f"- литдавление: {pressure} (порог 3)")
    for t in targets[:3]:
        lines.append(f"  {t}")
    text = "\n".join(lines) + "\n"

    if args.dry:
        print(text)
        return 0
    out = OUT / f"science-review-{day}.md"
    out.write_text(text, encoding="utf-8", newline="\n")
    state["hashes"] = sorted(seen | {r["hash"] for r in fresh})[-200:]
    state["criteria"] = {name: {k: v for k, v in (summary.get("__criteria__") or {}).items()
                                if isinstance(v, (bool, int, float))}
                         for name, summary in aggs.items()}
    state["last_run"] = datetime.now().isoformat(timespec="seconds")
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"дайджест: {out.relative_to(REPO)} | рекомендаций новых: {len(fresh)} из {len(recs)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
