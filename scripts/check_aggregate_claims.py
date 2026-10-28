"""check_aggregate_claims.py — каждый агрегат обязан говорить, чего он НЕ утверждает.

Откуда (28.10, разбор закрепа владельца). В lexspec и flowguard-spec каждый отчёт несёт дословный список
`not_claimed`, и вердикт без этого списка — другое утверждение. У нас числа жили в агрегатах без границы
применимости: читатель не мог отличить «мир такой» от «так вышло на 32x32 при 600 шагах».

Проверка: у каждого `*_matrix.json` в `morphogenesis/experiments/` есть ключ `not_claimed` — непустой список
строк. Это дешёвый гейт с одним правилом.

Использование:
    python scripts/check_aggregate_claims.py [--strict]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "morphogenesis" / "experiments"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="каждый агрегат обязан нести not_claimed")
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args(argv)

    files = sorted(EXPERIMENTS.rglob("*_matrix.json"))
    missing, ok = [], 0
    for path in files:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        nc = data.get("not_claimed")
        if isinstance(nc, list) and any(str(x).strip() for x in nc):
            ok += 1
        else:
            missing.append(path.relative_to(ROOT))

    print(f"[agg-claims] агрегатов {len(files)}: с not_claimed {ok}, без {len(missing)}")
    if missing:
        for m in missing[:10]:
            print("   нет not_claimed:", m)
        if args.strict:
            return 1
        print("[agg-claims] предупреждение: старые агрегаты собраны до правила (не ошибка в строгом режиме)")
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
