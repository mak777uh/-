"""predictions.py — реестр предсказаний: что мы обещали до данных и что вышло.

Зачем (EBT, 27.10). У нас есть пре-регистрации, но не было учёта, СБЫЛИСЬ ли они.
За сутки набралось четыре промаха из четырёх (просторная зона, квота, рефрактерный
период, среднее по Фишеру), и без реестра это выглядело бы как «так и планировали».
Реестр даёт три вещи: (1) калибровку собственной интуиции; (2) материал для честного
раздела «как мы ошибались»; (3) запрет тихо переписать предсказание после факта —
запись несёт дату и коммит пре-регистрации.

Использование:
    python scripts/predictions.py --list
    python scripts/predictions.py --check          # гейт: у открытых нет исхода, у закрытых есть
    python scripts/predictions.py --close P-003 --outcome "факт" --hit no --note "..."
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STORE = ROOT / "lab" / "predictions.json"


def load() -> dict:
    if not STORE.exists():
        return {"kind": "prediction-ledger", "items": []}
    return json.loads(STORE.read_text(encoding="utf-8"))


def save(data: dict) -> None:
    data["updated"] = dt.date.today().isoformat()
    STORE.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                     encoding="utf-8", newline="\n")


def cmd_close(args) -> int:
    data = load()
    for it in data["items"]:
        if it.get("id") == args.close:
            if it.get("hit"):
                print(f"{args.close}: уже закрыто ({it['hit']}) — предсказание не переписывается")
                return 1
            it["outcome"] = args.outcome
            it["hit"] = args.hit
            it["closed_at"] = dt.date.today().isoformat()
            if args.note:
                it["note"] = args.note
            save(data)
            print(f"{args.close}: закрыто как «{args.hit}»")
            return 0
    print(f"{args.close}: нет такого предсказания")
    return 1


def cmd_check(args) -> int:
    data = load()
    items = data.get("items") or []
    errors = []
    for it in items:
        pid = it.get("id")
        if not pid or not it.get("statement") or not it.get("prereg_commit"):
            errors.append(f"{pid}: нужны statement и prereg_commit (дата и коммит пре-регистрации)")
        if it.get("hit") and not it.get("outcome"):
            errors.append(f"{pid}: закрыто, но нет outcome")
        if not it.get("hit") and it.get("outcome"):
            errors.append(f"{pid}: есть outcome, но не указан hit (yes/no/mixed)")
        if it.get("hit") and it["hit"] not in ("yes", "no", "mixed"):
            errors.append(f"{pid}: hit должен быть yes/no/mixed")
    closed = [i for i in items if i.get("hit")]
    hits = sum(1 for i in closed if i["hit"] == "yes")
    print(f"[predictions] всего {len(items)} | закрыто {len(closed)} | сбылось {hits}")
    if errors:
        for e in errors:
            print("  ошибка:", e)
        return 1
    return 0


def cmd_list(args) -> int:
    data = load()
    for it in data.get("items") or []:
        mark = {"yes": "✓", "no": "✗", "mixed": "~"}.get(it.get("hit") or "", "·")
        print(f"{mark} {it['id']}: {it['statement'][:90]}")
        if it.get("outcome"):
            print(f"      факт: {it['outcome'][:110]}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--close", metavar="ID")
    ap.add_argument("--outcome")
    ap.add_argument("--hit", choices=["yes", "no", "mixed"])
    ap.add_argument("--note")
    args = ap.parse_args(argv)
    if args.check:
        return cmd_check(args)
    if args.close:
        if not args.outcome or not args.hit:
            print("нужны --outcome и --hit"); return 2
        return cmd_close(args)
    return cmd_list(args)


if __name__ == "__main__":
    raise SystemExit(main())
