"""backfill_not_claimed.py — дописать `not_claimed` в старые агрегаты.

Честность важнее аккуратности: агрегаты, собранные до правила (28.10), не знают своего `not_claimed`.
Скрипт дописывает **общий** список с явной пометкой, что он не от агрегатора: пересборка своим агрегатором
заменит его на специфичный. Так гейт `check_aggregate_claims.py` перестаёт быть вечным «50 из 51», но никто
не примет пометку за индивидуальное суждение о конкретной серии.

Использование:
    python scripts/backfill_not_claimed.py --check   # сколько агрегатов без пометки
    python scripts/backfill_not_claimed.py --write   # дописать
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "morphogenesis" / "experiments"

GENERIC = [
    "что мир ведёт себя так же при другом размере поля или другом правиле",
    "что величина воспроизведётся на другой видеокарте",
    "что числа остаются теми же при другом горизонте прогона",
    "что этот агрегат построен по критерию, отличному от записанного в пре-регистрации его серии",
]
MARK = "заполнено backfill 2026-10-28 общим списком; пересборка своим агрегатором заменит его"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="дописать not_claimed в старые агрегаты")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)

    files = sorted(EXPERIMENTS.rglob("*_matrix.json"))
    todo = []
    for path in files:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        nc = data.get("not_claimed")
        if isinstance(nc, list) and any(str(x).strip() for x in nc):
            continue
        todo.append((path, data))

    print(f"[backfill] агрегатов {len(files)}, без not_claimed {len(todo)}")
    if args.check or not args.write:
        for path, _ in todo[:8]:
            print("   ", path.relative_to(ROOT))
        return 0

    for path, data in todo:
        data["not_claimed"] = list(GENERIC)
        data["not_claimed_source"] = MARK
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"[backfill] дописано в {len(todo)} агрегатов (с пометкой о происхождении списка)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
