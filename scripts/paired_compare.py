"""paired_compare.py — парное сравнение двух плеч по сидам, без «средних по плечу».

Зачем. Идея взята из практики оценки онтологий (NVIDIA auto-ontology): один и тот же вход даётся двум
конфигурациям, и результат сравнивается **механически**, а не по агрегатам. У нас аналог — сид: один и тот
же сид в двух плечах даёт парное наблюдение, и это сильнее, чем два независимых медиана, потому что
убирает разброс между сидами.

Что считается:
  * разность по каждому сиду: d = metric(arm_a, seed) − metric(arm_b, seed);
  * медиана d и её 95 % ДИ (bootstrap по сидам, фиксированный seed — воспроизводимо);
  * знаковый тест (сколько сидов в пользу a, сколько в пользу b, двусторонний точный p);
  * среднее и стандартное отклонение d.

Величина берётся из артефакта честно: `--field` — путь в summary через точку, либо `--derived
effective_lineages` (1/Σp² по type_counts).

Использование:
    python scripts/paired_compare.py --a-dir DIR_A --b-dir DIR_B \
        --pattern "w2bud_async_{arm}_seed{seed}.json" --arm-a cellp10 --arm-b cellp05 \
        --derived effective_lineages
"""
from __future__ import annotations

import argparse
import json
import math
import random
import re
import statistics as st
from pathlib import Path


def load_value(path: Path, field: str | None, derived: str | None) -> float | None:
    s = json.loads(path.read_text(encoding="utf-8")).get("summary") or {}
    if derived == "effective_lineages":
        cells = {str(k).lstrip("T"): int(v) for k, v in (s.get("type_counts") or {}).items()}
        tot = sum(cells.values()) or 0
        p = [v / tot for v in cells.values() if v > 0] if tot else []
        return (1.0 / sum(x * x for x in p)) if p else None
    if derived == "lineages_with_data":
        spores = {str(k): int(v) for k, v in (s.get("lineage_spores") or {}).items()}
        cells = {str(k).lstrip("T"): int(v) for k, v in (s.get("type_counts") or {}).items()}
        return float(len([t for t, c in cells.items() if c >= 5 and spores.get(t, 0) >= 1]))
    if not field:
        return None
    cur = s
    for part in field.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return float(cur) if isinstance(cur, (int, float)) else None


def collect(directory: Path, pattern: str, arm: str, field, derived) -> dict[int, float]:
    rx = re.compile(pattern.replace("{arm}", re.escape(arm)).replace("{seed}", r"(?P<seed>\d+)"))
    out: dict[int, float] = {}
    for path in sorted(directory.glob("*.json")):
        m = rx.match(path.name)
        if not m:
            continue
        v = load_value(path, field, derived)
        if v is not None:
            out[int(m.group("seed"))] = v
    return out


def sign_test_p(wins: int, losses: int) -> float:
    n = wins + losses
    if n == 0:
        return 1.0
    # двусторонний точный биномиальный тест при p = 0.5
    k = min(wins, losses)
    tail = sum(math.comb(n, i) for i in range(0, k + 1)) / (2 ** n)
    return min(1.0, 2 * tail)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--a-dir", required=True)
    ap.add_argument("--b-dir", required=True)
    ap.add_argument("--pattern", default="{arm}_seed{seed}.json")
    ap.add_argument("--arm-a", required=True)
    ap.add_argument("--arm-b", required=True)
    ap.add_argument("--field", default=None)
    ap.add_argument("--derived", default=None,
                    choices=[None, "effective_lineages", "lineages_with_data"])
    ap.add_argument("--boot", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--format", default="text", choices=["text", "json"])
    args = ap.parse_args(argv)

    a = collect(Path(args.a_dir), args.pattern, args.arm_a, args.field, args.derived)
    b = collect(Path(args.b_dir), args.pattern, args.arm_b, args.field, args.derived)
    seeds = sorted(set(a) & set(b))
    if not seeds:
        print("[paired] нет общих сидов — сравнение невозможно")
        return 1
    d = [a[s] - b[s] for s in seeds]
    wins = sum(1 for x in d if x > 0)
    losses = sum(1 for x in d if x < 0)
    ties = sum(1 for x in d if x == 0)
    rnd = random.Random(args.seed)
    boots = sorted(st.median([d[rnd.randrange(len(d))] for _ in d]) for _ in range(args.boot))
    lo, hi = boots[int(0.025 * args.boot)], boots[int(0.975 * args.boot) - 1]
    out = {
        "pairs": len(seeds),
        "arm_a": args.arm_a, "arm_b": args.arm_b,
        "median_a": round(st.median([a[s] for s in seeds]), 4),
        "median_b": round(st.median([b[s] for s in seeds]), 4),
        "median_diff": round(st.median(d), 4),
        "mean_diff": round(st.mean(d), 4),
        "sd_diff": round(st.stdev(d), 4) if len(d) > 1 else None,
        "ci_low": round(lo, 4), "ci_high": round(hi, 4),
        "a_better": wins, "b_better": losses, "ties": ties,
        "sign_test_p": round(sign_test_p(wins, losses), 5),
        "seeds": seeds,
    }
    if args.format == "json":
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0
    print(f"[paired] {args.arm_a} против {args.arm_b}: пар {out['pairs']}")
    print(f"  медианы: {out['median_a']} против {out['median_b']}")
    print(f"  разность: медиана {out['median_diff']}, среднее {out['mean_diff']}, "
          f"95 % ДИ [{out['ci_low']}, {out['ci_high']}]")
    print(f"  счёт: {wins} за {args.arm_a}, {losses} за {args.arm_b}, {ties} ничьих | "
          f"знаковый тест p = {out['sign_test_p']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
