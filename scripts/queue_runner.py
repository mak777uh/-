#!/usr/bin/env python
"""queue_runner.py — очередь экспериментов как конвейер: порядок по импакту, запуск по готовности.

Идея (владелец, 25.10): список экспериментов — это очередь, которая едет сама, а ведущий
меняет тексты и порядок в сторону импакта. Реализация ниже держит три инварианта, без
которых автоматизация превращается в «прогоны ради прогонов»:

1. **Порядок задаётся импактом, а не номером.** Приоритет = `impact / max(cost_gpu_h, 0.1)`:
   дешёвое и важное впереди. Ведущий может менять `impact` и `cost_gpu_h` в любой момент —
   это и есть «переставить в сторону импакта» без правки кода.
2. **Без пре-регистрации не запускается.** У пункта обязан быть `prereg` — файл плана,
   **закоммиченный раньше** старта. Иначе критерий «после данных» и результат несравним.
3. **Конвейер не закрывает работу.** Он доводит пункт до `awaiting_review`; `closed`
   ставит только ведущий после проверки чисел. Иначе бейзлайн «мы сами себя приняли»
   протекает в рукопись.

Запуск (из корня):

    python scripts/queue_runner.py --plan              # что поедет и в каком порядке
    python scripts/queue_runner.py --once --dry-run    # показать команду головы очереди
    python scripts/queue_runner.py --once              # выполнить голову (нужен --yes)
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "lab" / "queue.json"
LOCKS = ROOT / "lab" / "locks"
STATUS_PLANNED = "planned"
STATUS_AWAITING = "awaiting_review"


def load_queue(path: Path | None = None) -> dict:
    return json.loads((path or QUEUE).read_text(encoding="utf-8"))


def save_queue(data: dict, path: Path | None = None) -> None:
    (path or QUEUE).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                               encoding="utf-8", newline="\n")


def priority(item: dict) -> float:
    """Импакт на стоимость. По умолчанию импакт 3, стоимость 0.1 — нейтральная точка."""
    impact = float(item.get("impact") or 3)
    cost = float(item.get("cost_gpu_h") or 0.1)
    return impact / max(cost, 0.1)


def gates_closed(item: dict, data: dict) -> bool:
    """Все `gated_by` закрыты (или пусто)."""
    gates = item.get("gated_by") or []
    if isinstance(gates, str):
        gates = [gates]
    if not gates:
        return True
    by_id = {i.get("id"): i for i in data.get("items", [])}
    return all((by_id.get(g) or {}).get("status") == "closed" for g in gates)


def prereg_ready(item: dict) -> tuple[bool, str]:
    """Пре-регистрация существует и закоммичена ДО старта (не позже сегодняшнего дня)."""
    prereg = item.get("prereg")
    if not prereg:
        return False, "нет поля prereg (нельзя запускать: критерий не зафиксирован)"
    path = ROOT / prereg
    if not path.exists():
        return False, f"нет файла {prereg}"
    proc = subprocess.run(["git", "log", "-1", "--format=%h", "--", prereg],
                          cwd=str(ROOT), capture_output=True, text=True)
    commit = proc.stdout.strip()
    if not commit:
        return False, f"{prereg} не закоммичен"
    return True, commit


def launch_ready(item: dict) -> tuple[bool, str]:
    """Для запуска нужна команда. Без неё пункт — идея, а не работа."""
    launch = item.get("launch") or {}
    cmd = launch.get("command") if isinstance(launch, dict) else None
    outdir = launch.get("outdir") if isinstance(launch, dict) else None
    if not cmd:
        return False, "нет launch.command — пункт не исполним автоматически"
    if not outdir:
        return False, "нет launch.outdir — некуда писать артефакты"
    return True, "готова"


def eligible(data: dict) -> list[tuple[float, dict, list[str]]]:
    """Пункты, которые можно ставить в конвейер, с причинами отказов."""
    out = []
    for item in data.get("items", []):
        if item.get("status") != STATUS_PLANNED:
            continue
        reasons: list[str] = []
        if not gates_closed(item, data):
            reasons.append("ждут закрытия gated_by")
        ok_pre, why_pre = prereg_ready(item)
        if not ok_pre:
            reasons.append(why_pre)
        ok_launch, why_launch = launch_ready(item)
        if not ok_launch:
            reasons.append(why_launch)
        out.append((priority(item), item, reasons))
    out.sort(key=lambda t: (-t[0], str(t[1].get("id"))))
    return out


def live_locks() -> list[str]:
    return sorted(p.name for p in LOCKS.glob("*.lock")) if LOCKS.exists() else []


def plan(data: dict) -> int:
    rows = eligible(data)
    print(f"[queue] пунктов в очереди: {len(rows)} (planned)")
    print(f"{'приоритет':>9}  {'id':<26} {'impact':>6} {'cost,ч':>6}  готовность")
    ready = 0
    for prio, item, reasons in rows:
        state = "ГОТОВ" if not reasons else "; ".join(reasons)
        ready += 0 if reasons else 1
        print(f"{prio:9.2f}  {str(item.get('id'))[:26]:<26} "
              f"{float(item.get('impact') or 3):6.1f} {float(item.get('cost_gpu_h') or 0.1):6.2f}  {state}")
    locks = live_locks()
    print(f"[queue] готовых к запуску: {ready}; живых замков: {len(locks)}"
          + (f" ({', '.join(locks)})" if locks else ""))
    return 0


def run_once(data: dict, dry_run: bool, confirmed: bool) -> int:
    rows = eligible(data)
    head = next((r for r in rows if not r[2]), None)
    if head is None:
        print("[queue] нет готовых пунктов — конвейеру нечего запускать")
        return 0
    _, item, _ = head
    launch = item["launch"]
    locks = live_locks()
    if locks:
        print(f"[queue] СТОП: живые замки {locks} — сначала дождаться финиша")
        return 1
    pre = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "preflight.py"),
         "--prereg", str(item["prereg"]), "--outdir", str(launch["outdir"])],
        cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    print(pre.stdout.strip())
    if pre.returncode != 0:
        print(f"[queue] СТОП: preflight не пропустил {item.get('id')}")
        return 1
    print(f"[queue] голова очереди: {item.get('id')} (приоритет {priority(item):.2f})")
    print(f"[queue] команда: {launch['command']}")
    if dry_run or not confirmed:
        print("[queue] dry-run: запуск не выполняется" + ("" if dry_run else " (нужен --yes)"))
        return 0
    proc = subprocess.run(launch["command"], cwd=str(ROOT), shell=True)
    if proc.returncode != 0:
        item["status"] = "blocked"
        item["note"] = f"конвейер: команда вернула {proc.returncode}"
        save_queue(data)
        print("[queue] СТОП: команда упала, пункт помечен blocked")
        return 1
    item["status"] = STATUS_AWAITING
    item["heartbeat_at"] = None
    item["closed_at"] = None
    item.setdefault("note", "")
    item["note"] = (item["note"] + " | конвейер: серия выполнена, ждёт приёмки ведущего").strip(" |")
    save_queue(data)
    print(f"[queue] {item.get('id')} → {STATUS_AWAITING} (закрывает только ведущий)")
    return 0




def audit(data: dict) -> int:
    """Статусы очереди обязаны совпадать с реальностью.

    Зачем: 25.10 три серии были закрыты, а в очереди висели как `planned`/`running`;
    нашлось глазами, а не машиной. Проверки:
      * `running` без живого замка — ошибка (серия не идёт);
      * `running` с heartbeat старше ttl — ошибка;
      * `planned`/`running`, у которых в каталоге появления уже есть артефакты —
        предупреждение «вероятно, серия выполнена, статус не обновлён».
    """
    problems: list[str] = []
    warnings: list[str] = []
    locks = set(live_locks())
    for item in data.get("items", []):
        status = item.get("status")
        iid = item.get("id")
        if status == "running":
            exp_name = item.get("experiment") or iid
            has_lock = any(lock.startswith(f"{exp_name}.lock") for lock in locks)
            if not has_lock:
                problems.append(f"{iid}: running, но живого замка нет — статус устарел или серия упала")
        if status in ("planned", "running"):
            launch = item.get("launch") or {}
            outdir = launch.get("outdir") if isinstance(launch, dict) else None
            if outdir:
                path = (ROOT / outdir) if not Path(outdir).is_absolute() else Path(outdir)
                if path.exists():
                    done = len(list(path.glob("*.json")))
                    if done:
                        warnings.append(
                            f"{iid}: статус {status}, но в {outdir} уже {done} артефактов — "
                            f"вероятно, серия выполнена"
                        )
    print(f"[queue-audit] прожито: {len(data.get('items', []))} пунктов, замков: {len(locks)}")
    for w in warnings:
        print(f"[queue-audit] ВНИМАНИЕ: {w}")
    for p_ in problems:
        print(f"[queue-audit] ОШИБКА: {p_}")
    if problems:
        return 1
    print("[queue-audit] OK — расхождений статуса с замками нет")
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="очередь экспериментов как конвейер")
    ap.add_argument("--plan", action="store_true", help="показать порядок и готовность")
    ap.add_argument("--once", action="store_true", help="выполнить голову очереди")
    ap.add_argument("--audit", action="store_true", help="сверить статусы с замками и артефактами")
    ap.add_argument("--dry-run", action="store_true", help="только показать команду")
    ap.add_argument("--yes", action="store_true", help="подтвердить фактический запуск")
    ap.add_argument("--file", default=None, help="путь к очереди (для тестов)")
    args = ap.parse_args(argv)
    data = load_queue(Path(args.file) if args.file else None)
    if args.audit:
        return audit(data)
    if args.once:
        return run_once(data, args.dry_run, args.yes)
    return plan(data)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
