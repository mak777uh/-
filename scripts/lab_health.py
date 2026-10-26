#!/usr/bin/env python
"""lab_health.py — одна команда, которая отвечает: «лаборатория здорова? что делать сейчас?»

Зачем. 25–26.10 три раза подряд повторилась одна картина: гейт красный, но никто не смотрит,
потому что красный давно и стал фоном.
  * библиотека — 36 замечаний без решения, 13 старше суток;
  * серия `W2bud_d2` закрылась в 02:46, агрегат появился в 03:13, заметил владелец;
  * `lab-contract` был красным ~24 часа: проверка пересобирала три агрегата из одного каталога.
Причина одна: **состояние видно по кускам, в разных местах, и ни одно из них не приходит событием.**

Этот скрипт не добавляет нового источника правды. Он **собирает** существующие в один ответ:
репозиторий, CI на GitHub (публичный API, без токена), локальные гейты, очереди, серии, ресурсы.
Выход: человекочитаемая сводка + `reports/health.md` + список действий по приоритету.

Запуск:
    python scripts/lab_health.py               # быстро: без тяжёлых гейтов
    python scripts/lab_health.py --full        # все локальные гейты
    python scripts/lab_health.py --github      # + состояние запусков CI
    python scripts/lab_health.py --ci          # только то, что имеет смысл в CI
Код выхода: 1, если есть блокеры (❌); 0 при предупреждениях.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POND = ROOT / "morphogenesis" / "experiments" / "E09_pond"
REPORT = ROOT / "reports" / "health.md"

# локальные гейты: (метка, аргументы, блокирующий?, тяжёлый?)
GATES = [
    ("контракт", ["scripts/lab.py", "validate", "--ci"], True, False),
    ("размер контракта", ["scripts/check_agents_size.py"], True, False),
    ("числа разделов", ["scripts/verify_sections_numbers.py"], True, False),
    ("числа рукописи", ["scripts/verify_manuscript_numbers.py"], True, True),
    ("утверждения", ["scripts/claims_lint.py"], True, False),
    ("реестр величин", ["scripts/metrics_registry.py", "--check"], True, False),
    ("агрегаты свежие", ["scripts/check_aggregates_fresh.py"], True, True),
    ("схема карточек", ["scripts/validate_runs.py"], True, False),
    ("ревью", ["scripts/check_reviews.py"], True, False),
    ("замечания библиотеки", ["scripts/library_inbox.py", "--ci"], True, False),
    ("доска литературы", ["scripts/lit_board.py", "--check"], True, False),
    ("инсайты", ["scripts/insight.py", "--check"], True, False),
    ("хвосты серий", ["scripts/check_series_followthrough.py", "--strict"], True, False),
    ("очередь экспериментов", ["scripts/queue_runner.py", "--audit"], True, False),
    ("витрина README", ["scripts/check_readme_fresh.py"], True, False),
    ("агрегат↔артефакт", ["scripts/aggregate_check.py", "--strict"], True, True),
]


def run(cmd: list[str], timeout: int = 300) -> tuple[int, str]:
    try:
        r = subprocess.run([sys.executable, *cmd], cwd=ROOT, capture_output=True,
                           text=True, timeout=timeout, encoding="utf-8", errors="replace")
        return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()
    except subprocess.TimeoutExpired:
        return 124, f"таймаут {timeout} с"
    except Exception as exc:  # pragma: no cover
        return 1, str(exc)


def git(args: list[str]) -> str:
    try:
        r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, timeout=60)
        return (r.stdout or "").strip()
    except Exception:
        return ""


def section_repo() -> tuple[list[str], list[str]]:
    bad, warn = [], []
    dirty = [l for l in git(["status", "--porcelain"]).splitlines() if l.strip()]
    ahead = git(["rev-list", "--count", "origin/main...HEAD"])
    try:
        a = int(ahead)
    except ValueError:
        a = 0
    if a:
        warn.append(f"{a} коммит(ов) не отправлены в origin")
    tracked_dirty = [l for l in dirty if not l.startswith("??")]
    if tracked_dirty:
        warn.append(f"незакоммиченных изменений: {len(tracked_dirty)} (первое: {tracked_dirty[0][:60]})")
    return bad, warn


def section_ci_file() -> tuple[list[str], list[str], str]:
    """Статус CI из репозитория (пишет workflow ci-status.yml). Работает без сети и без токена."""
    f = ROOT / "reports" / "ci-status.json"
    if not f.exists():
        return [], ["reports/ci-status.json отсутствует — статус CI в репозитории не пишется"], "нет файла"
    try:
        data = json.loads(f.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"ci-status.json не читается: {exc}"], [], "ошибка"
    bad, warn, parts = [], [], []
    for name, run in (data.get("runs") or {}).items():
        concl = run.get("conclusion", "?")
        at = run.get("at", "")[:16].replace("T", " ")
        parts.append(f"{name}: {concl} ({at})")
        if concl == "failure":
            steps = run.get("failed_steps") or []
            bad.append(f"CI «{name}» упал: " + ("; ".join(steps) if steps else "шаг не определён"))
        elif concl in ("cancelled", "timed_out"):
            warn.append(f"CI «{name}»: {concl}")
    return bad, warn, "; ".join(parts) if parts else "нет записей"


def section_github() -> tuple[list[str], list[str], str]:
    """Последний запуск каждого workflow. Публичный репозиторий — без токена."""
    bad, warn = [], []
    url = "https://api.github.com/repos/{}/actions/runs?per_page=40"
    repo = None
    m = re.search(r"github\.com[:/]([^/]+)/([^/.]+?)(?:\.git)?$", git(["remote", "get-url", "origin"]))
    if m:
        repo = f"{m.group(1)}/{m.group(2)}"
    if not repo:
        return bad, ["не удалось определить репозиторий из remote"], "—"
    try:
        req = urllib.request.Request(url.format(repo), headers={
            "Accept": "application/vnd.github+json", "User-Agent": "lab-health"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
    except Exception as exc:
        return bad, [f"GitHub API недоступен: {str(exc)[:80]}"], "—"

    seen: dict[str, dict] = {}
    for run_ in data.get("workflow_runs", []):
        name = run_.get("name") or "?"
        if name not in seen:
            seen[name] = run_
    lines = []
    for name, run_ in seen.items():
        concl = run_.get("conclusion") or run_.get("status")
        created = run_.get("created_at", "")
        try:
            age_h = (datetime.now(timezone.utc) - datetime.fromisoformat(created.replace("Z", "+00:00"))).total_seconds() / 3600
            age = f"{age_h:.1f} ч назад"
        except Exception:
            age = created
        lines.append(f"{name}: {concl} ({age})")
        if concl == "failure":
            bad.append(f"CI «{name}» упал ({age}): {run_.get('html_url')}")
        elif concl in ("cancelled", "timed_out", "action_required"):
            warn.append(f"CI «{name}»: {concl} ({age})")
    return bad, warn, "; ".join(lines) if lines else "запусков не найдено"


def section_gates(full: bool) -> tuple[list[str], list[str], list[str]]:
    bad, warn, lines = [], [], []
    for label, cmd, blocking, heavy in GATES:
        if heavy and not full:
            continue
        code, out = run(cmd)
        tail = (out.splitlines() or [""])[-1][:110]
        lines.append(f"{'✅' if code == 0 else '❌'} {label}: {tail}")
        if code != 0:
            (bad if blocking else warn).append(f"гейт «{label}»: {tail}")
    return bad, warn, lines


def section_queues() -> tuple[list[str], list[str], str]:
    bad, warn = [], []
    # эксперименты
    try:
        q = json.loads((ROOT / "lab" / "queue.json").read_text(encoding="utf-8"))
        items = q.get("items", [])
        planned = [i for i in items if i.get("status") == "planned"]
        running = [i for i in items if i.get("status") == "running"]
    except Exception as exc:
        return [f"lab/queue.json не читается: {exc}"], [], "—"
    # ферма
    try:
        aq = json.loads((ROOT / "lab" / "analysis-queue.json").read_text(encoding="utf-8"))
        pending = [t for t in aq.get("tasks", []) if t.get("status") == "pending"]
    except Exception:
        pending = []
    # библиотека
    try:
        board = json.loads((ROOT / "lab" / "lit-board.json").read_text(encoding="utf-8"))
        new = [i for i in board.get("items", []) if i.get("status") == "new"]
    except Exception:
        new = []
    if len(pending) > 0:
        warn.append(f"ферма: {len(pending)} задач ждут выполнения")
    if new:
        warn.append(f"доска: {len(new)} замечаний без решения")
    if running and not list((ROOT / "lab" / "locks").glob("*.lock")):
        bad.append("пункт очереди в статусе running, но живого замка нет")
    text = (f"эксперименты: {len(planned)} в плане, {len(running)} идёт; "
            f"ферма: {len(pending)} ждёт; доска: {len(new)} новых")
    return bad, warn, text


def section_series() -> tuple[list[str], list[str], str]:
    code, out = run(["scripts/check_series_followthrough.py"])
    m = re.search(r"серий с артефактами: (\d+); в порядке: (\d+)", out)
    warn = [l.replace("[followthrough] ВНИМАНИЕ: ", "") for l in out.splitlines() if "ВНИМАНИЕ" in l]
    return [], warn, (f"{m.group(2)}/{m.group(1)} серий с агрегатом" if m else out.splitlines()[-1] if out else "—")


def section_resources() -> tuple[list[str], list[str], str]:
    bad, warn = [], []
    free_gb = shutil.disk_usage(ROOT).free / 1024 ** 3
    if free_gb < 10:
        warn.append(f"диск: свободно {free_gb:.1f} ГБ (< 10) — тяжёлые прогоны лучше не запускать")
    locks = list((ROOT / "lab" / "locks").glob("*.lock"))
    if locks:
        warn.append(f"активные замки: {len(locks)} ({', '.join(p.stem for p in locks[:3])})")
    return bad, warn, f"диск: {free_gb:.1f} ГБ свободно; замков: {len(locks)}"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="здоровье лаборатории одной командой")
    ap.add_argument("--full", action="store_true", help="включая тяжёлые гейты")
    ap.add_argument("--github", action="store_true", help="проверить запуски CI (публичный API)")
    ap.add_argument("--ci", action="store_true", help="режим CI: без сети, только гейты")
    ap.add_argument("--quiet", action="store_true", help="только проблемы")
    args = ap.parse_args(argv)

    blockers: list[str] = []
    warnings: list[str] = []
    lines: list[str] = []

    b, w = section_repo(); blockers += b; warnings += w
    if not args.ci:
        gh_bad, gh_warn, gh_text = section_ci_file()
        blockers += gh_bad; warnings += gh_warn
        lines.append(f"CI (по reports/ci-status.json): {gh_text}")
        if args.github:  # живой API: свежее файла, но нужен при молчащем workflow
            api_bad, api_warn, api_text = section_github()
            if api_bad or api_warn:
                lines.append(f"CI (живой API): {api_text}")
            blockers += api_bad; warnings += api_warn

    gb, gw, gate_lines = section_gates(args.full)
    blockers += gb; warnings += gw; lines += gate_lines

    qb, qw, q_text = section_queues(); blockers += qb; warnings += qw
    lines.append(f"очереди: {q_text}")
    _, s_warn, s_text = section_series(); warnings += s_warn
    lines.append(f"серии: {s_text}")
    _, r_warn, r_text = section_resources(); warnings += r_warn
    lines.append(f"ресурсы: {r_text}")

    if not args.quiet:
        print("=== здоровье лаборатории ===")
        for line in lines:
            print("  " + line)
        print(f"\nблокеров: {len(blockers)}; предупреждений: {len(warnings)}")
        for p in blockers:
            print(f"  ❌ {p}")
        for p in warnings:
            print(f"  ⚠ {p}")
        if not blockers and not warnings:
            print("  всё чисто")

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    md = ["# Здоровье лаборатории", "",
          f"Обновлено: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC", ""]
    md += ["## Состояние", ""] + [f"- {l}" for l in lines]
    md += ["", "## Блокеры", ""] + ([f"- ❌ {p}" for p in blockers] or ["нет"])
    md += ["", "## Предупреждения", ""] + ([f"- ⚠ {p}" for p in warnings] or ["нет"])
    REPORT.write_text("\n".join(md) + "\n", encoding="utf-8", newline="\n")

    return 1 if blockers else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
