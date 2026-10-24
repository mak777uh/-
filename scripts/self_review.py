#!/usr/bin/env python
"""Дневной самоаудит библиотеки: что сработало, что нет, что поправить.

Считает по репозиторию (без домыслов):
  * коммиты за сутки, отдельно свои и чужие;
  * свои самоисправления (исправл/уточн/снимаю/неверн) — доля от содержательных;
  * закрытые пункты очереди и сколько с заметкой/артефактом;
  * новые источники, ответы, notices за сутки;
  * записи сканера переходов за сутки и сколько переходов получили мини-обзор;
  * проверки: claim_audit, test_lib_tools;
  * принятие наружу: чужие коммиты со ссылкой на B-###/P##/«библиотек».

Пишет library/self-review-<дата>.md и печатает до трёх предложений по улучшению.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MINE = ("library:", "notices:", "cycle:", "board:", "B-")
CORRECTION = re.compile(r"исправл|уточн|снимаю|неверн|вернуть нельзя|переписать", re.I)
EXTERNAL_REF = re.compile(r"B-0\d\d|\bP\d{2}\b|библиотек", re.I)


def git(*args: str) -> str:
    try:
        return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=60).stdout
    except Exception:
        return ""


def count_md(path: Path, pattern: str) -> int:
    if not path.exists():
        return 0
    return len(re.findall(pattern, path.read_text(encoding="utf-8"), re.M))


def file_at(rev: str, path: str) -> str:
    return git("show", f"{rev}:{path}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--date", default=None, help="день (по умолчанию сегодня)")
    ap.add_argument("--json", default=None)
    ap.add_argument("--no-tests", action="store_true")
    args = ap.parse_args(argv)

    day = args.date or datetime.now().strftime("%Y-%m-%d")
    since = f"{day} 00:00"
    until = f"{day} 23:59"
    rev_before = git("rev-list", "-1", f"--before={since}", "HEAD").strip() or "HEAD~1"

    commits = [l for l in git("log", f"--since={since}", f"--until={until}",
                              "--format=%h|%s", "--no-merges").splitlines() if l]
    mine = [c for c in commits if c.split("|", 1)[1].startswith(MINE)]
    external = [c for c in commits if c not in mine]
    corrections = [c for c in mine if CORRECTION.search(c.split("|", 1)[1])]
    substantive = [c for c in mine if not CORRECTION.search(c.split("|", 1)[1])]
    adopted = [c for c in external if EXTERNAL_REF.search(c.split("|", 1)[1])]

    def delta(path: str, pattern: str) -> int:
        now_n = count_md(REPO / path, pattern)
        old_text = file_at(rev_before, path)
        old_n = len(re.findall(pattern, old_text, re.M)) if old_text else 0
        return now_n - old_n

    sources_delta = sum(delta(p, r"^\| [A-Z]\d+ \|") for p in
                        ("library/hypotheses/pond-lineage.md", "library/hypotheses/alife-lineage.md"))
    answers_delta = delta("library/answers.md", r"^## \d+\.")
    notices_delta = delta("lab/notices.md", r"^### \d{4}-\d{2}-\d{2}")

    queue = json.loads((REPO / "library" / "work-queue.json").read_text(encoding="utf-8"))
    items = queue.get("items", [])
    closed_today = [i for i in items if i.get("status") == "done"
                    and (i.get("done_at") or "").startswith(day)]
    closed_with_note = [i for i in closed_today if (i.get("result") or "").strip()]
    open_items = [i for i in items if i.get("status") != "done"]
    blocked = [i for i in open_items if i.get("blocked_by")]
    no_date = [i for i in open_items if not i.get("created_at")]

    inbox = REPO / "library" / "result-inbox.jsonl"
    transitions_today = 0
    if inbox.exists():
        for line in inbox.read_text(encoding="utf-8").splitlines():
            try:
                rec = json.loads(line)
            except Exception:
                continue
            if (rec.get("at") or "").startswith(day):
                transitions_today += 1

    audit = subprocess.run([sys.executable, "scripts/claim_audit.py"], cwd=REPO,
                           capture_output=True, text=True, encoding="utf-8")
    audit_ok = audit.returncode == 0
    tests_ok = None
    if not args.no_tests:
        tests = subprocess.run([sys.executable, "scripts/test_lib_tools.py"], cwd=REPO,
                               capture_output=True, text=True, encoding="utf-8")
        tests_ok = tests.returncode == 0

    data = {
        "day": day,
        "commits_total": len(commits),
        "commits_mine": len(mine),
        "commits_external": len(external),
        "corrections": len(corrections),
        "substantive": len(substantive),
        "adopted_external": len(adopted),
        "sources_added": sources_delta,
        "answers_added": answers_delta,
        "notices_added": notices_delta,
        "items_closed": len(closed_today),
        "items_closed_with_note": len(closed_with_note),
        "items_open": len(open_items),
        "items_blocked": len(blocked),
        "items_without_created_at": len(no_date),
        "transitions_seen": transitions_today,
        "claim_audit_ok": audit_ok,
        "tests_ok": tests_ok,
    }

    corr_rate = (len(corrections) / len(mine)) if mine else 0.0
    note_rate = (len(closed_with_note) / len(closed_today)) if closed_today else 1.0

    proposals = []
    if corr_rate > 0.3:
        proposals.append(("усилить проверку перед публикацией вывода",
                          f"доля самоисправлений {corr_rate:.0%} от своих коммитов",
                          "в каждом выводе сначала семантика метрики и контроль, потом текст"))
    if not audit_ok:
        proposals.append(("починить пакеты доказательств",
                          "claim_audit вернул ошибки", "не двигать очередь, пока пакеты не зелёные"))
    if tests_ok is False:
        proposals.append(("починить инструменты", "тесты падают",
                          "сначала тесты, потом новые пункты"))
    if note_rate < 1.0:
        proposals.append(("закрывать пункты только с заметкой",
                          f"заметка есть у {note_rate:.0%} закрытых",
                          "без артефакта и заметки пункт не закрывается"))
    if len(no_date) > 0:
        proposals.append(("проставить даты создания пунктам",
                          f"{len(no_date)} пунктов без created_at",
                          "возраст пункта нужен, чтобы ловить зависшие"))
    if len(open_items) > 20:
        proposals.append(("сократить очередь",
                          f"{len(open_items)} открытых пунктов — она перестаёт быть приоритетной",
                          "оставить 10 самых дешёвых и важных, остальные отложить"))
    if transitions_today and len(closed_today) == 0:
        proposals.append(("переходы есть, а мини-обзоры не закрывались",
                          f"переходов за день: {transitions_today}",
                          "сначала мини-обзор перехода, потом остальная работа"))
    proposals = proposals[:3]

    lines = [f"# Самоаудит за {day}", "",
             "## Факты", "",
             "| Показатель | Значение |", "|---|---|"]
    for key, label in (("commits_total", "коммитов всего"), ("commits_mine", "моих"),
                       ("commits_external", "чужих"), ("corrections", "самоисправлений"),
                       ("substantive", "содержательных"), ("adopted_external", "чужих, где принята библиотека"),
                       ("sources_added", "новых источников"), ("answers_added", "новых ответов"),
                       ("notices_added", "новых notices"), ("items_closed", "закрыто пунктов"),
                       ("items_closed_with_note", "из них с заметкой"), ("items_open", "открыто пунктов"),
                       ("items_blocked", "заблокировано"), ("transitions_seen", "записей сканера"),
                       ("claim_audit_ok", "claim_audit зелёный"), ("tests_ok", "тесты зелёные")):
        lines.append(f"| {label} | {data[key]} |")

    lines += ["", "## Что сработало", ""]
    if data["adopted_external"]:
        lines.append(f"- принято наружу: {data['adopted_external']} коммитов со ссылкой на находки")
    if data["items_closed_with_note"]:
        lines.append(f"- закрыто с подтверждением: {data['items_closed_with_note']} пунктов")
    if audit_ok and tests_ok:
        lines.append("- проверки зелёные, инструменты согласованы")
    if not (data["adopted_external"] or data["items_closed_with_note"]):
        lines.append("- убедительных следов импакта за день нет")

    lines += ["", "## Что не сработало", ""]
    if corr_rate > 0:
        lines.append(f"- самоисправлений: {len(corrections)} ({corr_rate:.0%} от своих коммитов)")
    if not note_rate >= 1.0:
        lines.append("- закрытые пункты без заметки — учёт формальный")
    if transitions_today and not closed_today:
        lines.append("- переходы фиксировались, мини-обзоры не закрывались")
    if len(open_items) > 20:
        lines.append(f"- очередь раздута: {len(open_items)} открытых")
    if not (corr_rate or transitions_today or len(open_items) > 20):
        lines.append("- серьёзных провалов не видно")

    lines += ["", "## Предложения (не больше трёх, по одному за цикл)", ""]
    if proposals:
        for idx, (title, why, how) in enumerate(proposals, 1):
            lines.append(f"{idx}. **{title}** — основание: {why}. Действие: {how}.")
    else:
        lines.append("Нет. Менять нечего — работаем как есть.")

    lines += ["", "## Как принимается поправка", "",
              "Одна поправка за день. Она записывается в `library/self-rules.md` с датой, основанием "
              "и способом отката. Через день проверяется, стало ли лучше по тем же цифрам; если нет — "
              "откат.", ""]

    out = REPO / "library" / f"self-review-{day}.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    if args.json:
        Path(args.json).write_text(json.dumps({**data, "proposals": proposals},
                                              ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"отчёт: {out.relative_to(REPO)}")
    print(f"своих коммитов {len(mine)}, самоисправлений {len(corrections)}, закрыто {len(closed_today)}, "
          f"переходов {transitions_today}, audit_ok={audit_ok}, tests_ok={tests_ok}")
    for idx, (title, why, _) in enumerate(proposals, 1):
        print(f"  {idx}. {title} — {why}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
