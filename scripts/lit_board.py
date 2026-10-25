"""Доска литературы: замечания к текущей работе.

Машинный источник — `lab/lit-board.json`; человеческий вид — `library/board.md`
(генерируется `--view`). Замечание без ссылки на запись `library/` не заводится:
иначе это мнение, а не литература.

Команды:
  --list [--status new]        показать замечания
  --for <target-id>            замечания, адресованные цели
  --add ...                    добавить замечание
  --accept ID --why "..." [--insight I-xxx] [--task "..."] [--report "..."]
  --decline ID --why "..."
  --defer ID --why "..."
  --done ID --why "..."
  --view [--out PATH]          перегенерировать человеческий вид
  --check                      проверить схему и сроки (код возврата 1 при ошибке)
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
BOARD = ROOT / "lab" / "lit-board.json"
VIEW = ROOT / "library" / "board.md"

TYPES = {
    "prior_art",
    "known_fact",
    "missing_baseline",
    "naming",
    "contradiction",
    "risk",
    "opportunity",
}
STATUSES = {"new", "accepted", "declined", "deferred", "done"}
WAVES = {"current", "paused"}
TARGET_KINDS = {"hypothesis", "experiment", "report", "section", "artifact", "metric"}
ACTION_KINDS = {"text", "method", "param", "experiment", "experiment_change", "baseline", "none"}
DECIDED = {"accepted", "declined", "deferred", "done"}
# Пороги устаревания зависят от волны: замечание к ТЕКУЩЕЙ волне бессмысленно, если
# волна уже сменилась. 25.10 доска выросла до 42 неразобранных замечаний за день — и
# проверка молчала, потому что пороги были 7/14 дней. Для текущей волны: 2 дня — сигнал,
# 5 дней — ошибка CI. Для отложенной волны пороги мягче.
STALE_WARN_DAYS = 7
STALE_ERR_DAYS = 14
CURRENT_WAVE_WARN_DAYS = 2
CURRENT_WAVE_ERR_DAYS = 5
# «принято» без закрытия — тихая ловушка: замечание выглядит решённым, а работа не сделана.
ACCEPTED_WARN_DAYS = 3
ACCEPTED_ERR_DAYS = 6
ID_RE = re.compile(r"^B-\d{3}$")


def load(path: pathlib.Path | None = None) -> dict:
    path = path or BOARD
    if not path.exists():
        return {"schema_version": 1, "items": []}
    return json.loads(path.read_text(encoding="utf-8"))


def save(data: dict, path: pathlib.Path | None = None) -> None:
    path = path or BOARD
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def next_id(items: list[dict]) -> str:
    numbers = [int(i["id"].split("-")[1]) for i in items if ID_RE.match(str(i.get("id", "")))]
    return "B-%03d" % ((max(numbers) + 1) if numbers else 1)


def _days_since(value: str) -> float | None:
    try:
        stamp = dt.datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None
    if stamp.tzinfo is None:
        stamp = stamp.replace(tzinfo=dt.timezone.utc)
    return (dt.datetime.now(dt.timezone.utc) - stamp).total_seconds() / 86400.0


def validate_items(items: list[dict]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    seen: set[str] = set()
    for item in items:
        ident = str(item.get("id", ""))
        where = f"lit-board.{ident or '?'}"
        if not ID_RE.match(ident):
            errors.append(f"{where}: id должен быть вида B-001")
            continue
        if ident in seen:
            errors.append(f"{where}: дубль id")
        seen.add(ident)
        if item.get("type") not in TYPES:
            errors.append(f"{where}: недопустимый type={item.get('type')!r}")
        status = item.get("status")
        if status not in STATUSES:
            errors.append(f"{where}: недопустимый status={status!r}")
        if item.get("wave") not in WAVES:
            errors.append(f"{where}: недопустимый wave={item.get('wave')!r}")
        if not str(item.get("statement") or "").strip():
            errors.append(f"{where}: пустое statement")
        target = item.get("target") or {}
        if not isinstance(target, dict):
            errors.append(f"{where}: target должен быть объектом")
        else:
            if target.get("kind") not in TARGET_KINDS:
                errors.append(f"{where}: недопустимый target.kind={target.get('kind')!r}")
            if not str(target.get("id") or "").strip():
                errors.append(f"{where}: пустой target.id")
        evidence = item.get("evidence") or []
        if not isinstance(evidence, list) or not evidence:
            errors.append(f"{where}: нужна хотя бы одна ссылка в evidence")
        else:
            for ev in evidence:
                lib = str((ev or {}).get("library") or "")
                rel = lib.split("#", 1)[0].strip()
                if not rel:
                    errors.append(f"{where}: evidence без library")
                    continue
                if not (ROOT / "library" / rel).exists():
                    errors.append(f"{where}: evidence ссылается на несуществующий {rel}")
        action = item.get("action") or {}
        if not isinstance(action, dict):
            errors.append(f"{where}: action должен быть объектом")
        else:
            if action.get("kind") not in ACTION_KINDS:
                errors.append(f"{where}: недопустимый action.kind={action.get('kind')!r}")
            if action.get("kind") != "none" and not str(action.get("detail") or "").strip():
                errors.append(f"{where}: пустой action.detail")
        if status in DECIDED:
            if not str(item.get("why") or "").strip():
                errors.append(f"{where}: для {status} нужна причина (why)")
            if not str(item.get("decided_at") or "").strip():
                errors.append(f"{where}: для {status} нужен decided_at")
        if status == "accepted":
            links = item.get("links") or {}
            has_link = any(links.get(k) for k in ("insights", "tasks", "reports"))
            if not has_link:
                errors.append(f"{where}: accepted требует ссылки на инсайт/задачу/отчёт")
            # «принято» — не «сделано»: без этого замечания копятся как кладбище
            age_acc = _days_since(str(item.get("decided_at") or item.get("created_at") or ""))
            if age_acc is not None:
                if age_acc > ACCEPTED_ERR_DAYS:
                    errors.append(
                        f"{where}: принято {age_acc:.0f} дн назад (> {ACCEPTED_ERR_DAYS}) и не закрыто — "
                        f"выполните действие или переведите в deferred с условием возврата"
                    )
                elif age_acc > ACCEPTED_WARN_DAYS:
                    warnings.append(
                        f"{where}: принято {age_acc:.0f} дн назад (> {ACCEPTED_WARN_DAYS}) — пора либо закрыть, "
                        f"либо отложить с условием"
                    )
        if status == "new":
            age = _days_since(str(item.get("created_at") or ""))
            current = str(item.get("wave") or "current") == "current"
            warn_days = CURRENT_WAVE_WARN_DAYS if current else STALE_WARN_DAYS
            err_days = CURRENT_WAVE_ERR_DAYS if current else STALE_ERR_DAYS
            if age is None:
                warnings.append(f"{where}: created_at не читается")
            elif age > err_days:
                errors.append(
                    f"{where}: замечание открыто {age:.0f} дн (> {err_days}) без решения"
                )
            elif age > warn_days:
                warnings.append(
                    f"{where}: замечание открыто {age:.0f} дн (> {warn_days}) без решения"
                )
    return errors, warnings


def _render_item(item: dict) -> list[str]:
    target = item.get("target") or {}
    action = item.get("action") or {}
    lines = [
        f"### {item['id']}. {item.get('title') or item['statement'][:80]}",
        "",
        f"- **Тип:** `{item.get('type')}`; **статус:** `{item.get('status')}`; "
        f"**волна:** `{item.get('wave')}`",
        f"- **Цель:** `{target.get('kind')}` `{target.get('id')}`"
        + (f", {target.get('ref')}" if target.get("ref") else ""),
        f"- **Утверждение:** {item.get('statement')}",
    ]
    evidence = item.get("evidence") or []
    if evidence:
        refs = ", ".join(
            f"[`library/{ev.get('library')}`](../library/{ev.get('library')})" for ev in evidence
        )
        lines.append(f"- **Доказательство:** {refs}")
    if action:
        lines.append(f"- **Действие:** `{action.get('kind')}` — {action.get('detail')}")
    links = item.get("links") or {}
    linked = [f"{k}: {', '.join(map(str, v))}" for k, v in links.items() if v]
    if linked:
        lines.append("- **След:** " + "; ".join(linked))
    if item.get("why"):
        lines.append(f"- **Решение:** {item['why']}")
    if item.get("decided_at"):
        lines.append(f"- **Когда:** {item['decided_at']}")
    lines.append("")
    return lines


def render(data: dict) -> str:
    items = data.get("items", [])
    current = [i for i in items if i.get("status") in {"new", "accepted"} and i.get("wave") == "current"]
    paused = [i for i in items if i.get("wave") == "paused"]
    done = [i for i in items if i.get("status") in {"done", "declined"} and i.get("wave") != "paused"]
    lines = [
        "# Доска литературы: замечания к текущей работе",
        "",
        "> Сгенерировано из [`lab/lit-board.json`](../lab/lit-board.json) командой",
        "> `python scripts/lit_board.py --view`. Править здесь — бессмысленно: меняется JSON.",
        "",
        "Доска — второй режим работы с литературой (**push**): не «что искать по задаче», а",
        "«что в текущей работе уже известно науке». Замечание заводит библиотекарь, решение",
        "(`accepted` / `declined` / `deferred`) ставит ведущий; `deferred` означает «линия",
        "приостановлена, вернуть при её возобновлении».",
        "",
        f"Открытых в текущей волне: **{len(current)}**; отложенных: **{len(paused)}**;",
        f"закрытых/отклонённых: **{len(done)}**.",
        "",
        "## Текущая волна",
        "",
    ]
    if current:
        for item in current:
            lines += _render_item(item)
    else:
        lines += ["_Открытых замечаний нет._", ""]
    lines += [
        "## Отложено (линия на паузе)",
        "",
    ]
    if paused:
        for item in paused:
            lines += _render_item(item)
    else:
        lines += ["_Нет._", ""]
    lines += [
        "## Закрыто и отклонено",
        "",
    ]
    if done:
        lines += ["| id | цель | решение | почему |", "| --- | --- | --- | --- |"]
        for item in done:
            target = item.get("target") or {}
            lines.append(
                f"| {item['id']} | `{target.get('kind')}` `{target.get('id')}` | "
                f"{item.get('status')} | {item.get('why') or '—'} |"
            )
        lines.append("")
    else:
        lines += ["_Пока пусто._", ""]
    lines += [
        "## Правила (коротко)",
        "",
        "1. Одно замечание — одна строка: тип, цель, утверждение, доказательство, действие.",
        "2. Без ссылки на запись `library/` замечание не заводится.",
        "3. Статус ставит не библиотекарь; `declined`/`deferred` — только с причиной.",
        "4. Потолок шума: ≤ 3 новых замечания за проверку библиотекаря.",
        "5. Отклонённое и отложенное остаётся: это след, а не мусор.",
        "",
    ]
    return "\n".join(lines)


def _find(data: dict, ident: str) -> dict:
    for item in data.get("items", []):
        if item.get("id") == ident:
            return item
    raise SystemExit(f"замечание {ident} не найдено")


def _transition(data: dict, ident: str, status: str, why: str, **extra) -> dict:
    if not why.strip():
        raise SystemExit("решение без причины не принимается")
    item = _find(data, ident)
    item["status"] = status
    item["why"] = why
    item["decided_at"] = dt.date.today().isoformat()
    if status == "accepted":
        item["wave"] = "current"
    if status == "deferred":
        item["wave"] = "paused"
    links = item.setdefault("links", {})
    for key in ("insights", "tasks", "reports"):
        values = extra.get(key) or []
        if values:
            links[key] = sorted(set(links.get(key, [])) | set(values))
    return item


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Доска литературы: замечания к текущей работе")
    ap.add_argument("--file", type=pathlib.Path, default=BOARD, help="путь к JSON (для тестов)")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--status", choices=sorted(STATUSES))
    ap.add_argument("--for", dest="for_target")
    ap.add_argument("--add", action="store_true")
    ap.add_argument("--type", choices=sorted(TYPES))
    ap.add_argument("--target-kind", choices=sorted(TARGET_KINDS))
    ap.add_argument("--target-id")
    ap.add_argument("--target-ref", default="")
    ap.add_argument("--statement")
    ap.add_argument("--library", action="append", default=[], help="library/<path>#anchor")
    ap.add_argument("--note", default="")
    ap.add_argument("--action-kind", choices=sorted(ACTION_KINDS))
    ap.add_argument("--action-detail", default="")
    ap.add_argument("--wave", choices=sorted(WAVES), default="current")
    ap.add_argument("--accept")
    ap.add_argument("--decline")
    ap.add_argument("--defer")
    ap.add_argument("--done")
    ap.add_argument("--why", default="")
    ap.add_argument("--insight", action="append", default=[])
    ap.add_argument("--task", action="append", default=[])
    ap.add_argument("--report", action="append", default=[])
    ap.add_argument("--view", action="store_true")
    ap.add_argument("--out", type=pathlib.Path, default=VIEW)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)

    data = load(args.file)

    if args.add:
        missing = [
            name
            for name, value in (
                ("--type", args.type),
                ("--target-kind", args.target_kind),
                ("--target-id", args.target_id),
                ("--statement", args.statement),
                ("--action-kind", args.action_kind),
            )
            if not value
        ]
        if not args.library:
            missing.append("--library")
        if missing:
            raise SystemExit("не хватает: " + ", ".join(missing))
        if not (ROOT / "library" / args.library[0].split("#")[0]).exists():
            raise SystemExit(f"нет такой записи библиотеки: {args.library[0]}")
        ident = next_id(data["items"])
        item = {
            "id": ident,
            "type": args.type,
            "target": {"kind": args.target_kind, "id": args.target_id, "ref": args.target_ref},
            "statement": args.statement,
            "evidence": [{"library": lib, "note": args.note} for lib in args.library],
            "action": {"kind": args.action_kind, "detail": args.action_detail},
            "status": "new",
            "wave": args.wave,
            "owner": "librarian",
            "created_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
            "decided_at": None,
            "why": None,
            "links": {"insights": [], "tasks": [], "reports": []},
        }
        data["items"].append(item)
        save(data, args.file)
        print(f"{ident}: заведено")
        return 0

    transitions = [
        ("accepted", args.accept),
        ("declined", args.decline),
        ("deferred", args.defer),
        ("done", args.done),
    ]
    for status, ident in transitions:
        if ident:
            _transition(
                data,
                ident,
                status,
                args.why,
                insights=args.insight,
                tasks=args.task,
                reports=args.report,
            )
            save(data, args.file)
            print(f"{ident}: {status}")
            return 0

    if args.view:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(render(data), encoding="utf-8")
        print(f"вид обновлён: {args.out}")
        return 0

    if args.check:
        errors, warnings = validate_items(data.get("items", []))
        for line in warnings:
            print(f"  предупреждение: {line}")
        for line in errors:
            print(f"  ошибка: {line}")
        print(f"замечаний: {len(data.get('items', []))}; ошибок: {len(errors)}")
        return 1 if errors else 0

    items = data.get("items", [])
    if args.for_target:
        items = [
            i
            for i in items
            if str((i.get("target") or {}).get("id")) == args.for_target
            or args.for_target in str((i.get("target") or {}).get("ref", ""))
        ]
    if args.status:
        items = [i for i in items if i.get("status") == args.status]
    if args.list or args.for_target or args.status:
        for item in items:
            target = item.get("target") or {}
            print(
                f"{item['id']} [{item.get('status')}/{item.get('wave')}] {item.get('type')}: "
                f"{target.get('id')} — {str(item.get('statement'))[:90]}"
            )
        if not items:
            print("замечаний нет")
        return 0

    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
