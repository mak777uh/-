#!/usr/bin/env python
"""Сканер результатов: переходы берутся из данных, а не из таймера.

Что делает:
  1) читает library/result-map.json (какое утверждение какими артефактами описывается);
  2) сравнивает артефакты с прошлым снимком (library/.result-scan-state.json);
  3) для новых/изменённых файлов строит запись в library/result-inbox.jsonl;
  4) распознаёт переходы: новый arm, смена вердикта по правилу, невалидный прогон,
     отставание агрегата от сырья;
  5) на каждый переход ставит в work-queue мини-обзор с конкретным вопросом к литературе.

Запуск: python scripts/result_scan.py [--init] [--json]
  --init  только запомнить текущее состояние (без записей и без постановки задач)
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MAP = REPO / "library" / "result-map.json"
STATE = REPO / "library" / ".result-scan-state.json"
INBOX = REPO / "library" / "result-inbox.jsonl"
QUEUE = REPO / "scripts" / "lib_cycle.py"
KEYS = ("pop_time", "median", "mean", "collapses", "n", "excess_mean_abs", "half_life_steps",
        "a_share_final", "invader_share_end", "invader_share_start", "injection_share_actual",
        "injection_share", "invalid_reason", "fixated", "invest_updates", "mutation_rate")


def digest(path: Path) -> str:
    return hashlib.sha1(path.read_bytes()).hexdigest()


def numbers(obj, out: dict, prefix: str = "") -> None:
    if isinstance(obj, dict):
        for key, val in obj.items():
            if key in KEYS and isinstance(val, (int, float, str, bool, type(None))):
                out[f"{prefix}{key}"] = val
                out.setdefault(key, val)
            else:
                numbers(val, out, f"{prefix}{key}." )
    elif isinstance(obj, list):
        for item in obj[:50]:
            numbers(item, out, prefix)


def arm_of(name: str, arms: list[str]) -> str | None:
    for arm in arms:
        if arm in name:
            return arm
    return None


def load(path: Path, default):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return default


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--init", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    cfg = load(MAP, {"claims": [], "arms": []})
    state = load(STATE, {"files": {}, "arms": {}, "baseline": {}})
    now = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M")

    records, transitions = [], []
    for claim in cfg.get("claims", []):
        for pattern in claim.get("globs", []):
            for raw in sorted(glob.glob(str(REPO / pattern))):
                path = Path(raw)
                key = str(path.relative_to(REPO)).replace("\\", "/")
                dg = digest(path)
                prev = state["files"].get(key, {})
                if prev.get("sha") == dg:
                    continue
                data = load(path, {}) if path.suffix == ".json" else {}
                nums: dict = {}
                numbers(data, nums)
                record = {"at": now, "claim": claim["id"], "file": key,
                          "new": not prev, "changed": sorted(
                              k for k in nums if prev.get("nums", {}).get(k) != nums[k])}
                state["files"][key] = {"sha": dg, "nums": nums}
                if not args.init:
                    records.append(record)
                noise = ("colinv", "b2", "b2d", "inherit", "seed", "fd", "uniform",
                         "patches", "gradflip", "matrix", "json", "BinvA", "AinvB", "v2",
                         "v01b", "pond", "ab", "p09", "p10")
                tokens = [t for t in path.stem.replace("-", "_").split("_")
                          if t and not t.isdigit() and not any(n in t for n in noise)]
                known = state.setdefault("arms", {}).setdefault(claim["id"], [])
                for token in tokens:
                    if token not in known:
                        known.append(token)
                        if not args.init:
                            transitions.append({"kind": "new_mode", "claim": claim["id"],
                                                "detail": f"новый режим/плечо «{token}» в {key}",
                                                "question": claim["question"]})
                if claim["id"] == "C6" and not args.init:
                    start = nums.get("injection_share_actual")
                    end = nums.get("a_share_final")
                    if isinstance(start, (int, float)) and isinstance(end, (int, float)):
                        if start <= cfg.get("rules", {}).get("C6_min_start", 0.05) and end >= 0.5:
                            transitions.append({"kind": "verdict", "claim": "C6",
                                                "detail": f"редкий инвайдер зафиксировался: "
                                                          f"start={start:.4f} end={end:.2f} в {key}",
                                                "question": claim["question"]})
                if claim["id"] == "C5" and not args.init:
                    hl = nums.get("half_life_steps")
                    gen = cfg.get("rules", {}).get("C5_generation", 165)
                    if isinstance(hl, (int, float)) and gen and hl / gen >= 0.5:
                        transitions.append({"kind": "verdict", "claim": "C5",
                                            "detail": f"полураспад {hl} шагов = {hl/gen:.2f} поколения "
                                                      f"в {key}",
                                            "question": claim["question"]})
                if isinstance(nums.get("invalid_reason"), str) and nums["invalid_reason"]:
                    if prev.get("nums", {}).get("invalid_reason") != nums["invalid_reason"]:
                        transitions.append({"kind": "invalid", "claim": claim["id"],
                                            "detail": f"{key}: {nums['invalid_reason'][:80]}",
                                            "question": claim["question"]})

    if args.init:
        STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"снимок запомнен: файлов {len(state['files'])}")
        return 0

    if records:
        with INBOX.open("a", encoding="utf-8") as fh:
            for rec in records:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")

    queue = load(REPO / "library" / "work-queue.json", {"items": []})
    have = {item.get("title", "") for item in queue["items"]}
    added = 0
    for tr in transitions:
        title = f"мини-обзор: {tr['kind']} — {tr['detail'][:60]}"
        if any(title[:45] in h for h in have):
            continue
        subprocess.run(["python", str(QUEUE), "add", "review", title, "--impact", "5",
                        "--effort", "2", "--target", f"library/reviews/auto-{tr['claim'].lower()}.md",
                        "--action", f"вопрос к литературе: {tr['question']}"],
                       cwd=REPO, capture_output=True, text=True, encoding="utf-8")
        added += 1

    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = {"at": now, "new_or_changed": len(records), "transitions": transitions,
               "queue_items_added": added}
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(f"[{now}] изменённых артефактов: {len(records)} | переходов: {len(transitions)} "
              f"| задач в очередь: {added}")
        for tr in transitions:
            print(f"  ПЕРЕХОД {tr['claim']} {tr['kind']}: {tr['detail'][:90]}")
            print(f"    вопрос: {tr['question']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
