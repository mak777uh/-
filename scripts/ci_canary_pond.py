#!/usr/bin/env python
"""Канарейка для GitHub Actions: маленький прогон пруда на чужой машине (CPU).

Зачем. GitHub Actions даёт бесплатный CPU в рамках лимитов, и на нём можно проверять
не только контракт, но и сам мир: воспроизводится ли прогон на другой машине, те же ли
инварианты (детерминизм по сиду, согласованность счётчиков смертей, ненулевой pop_time).

Скрипт запускает 2 плеча, одно из них дважды для проверки детерминизма, сверяет
инварианты и пишет `_ci_canary.json`. Полный прогон на GPU он не заменяет — это дешёвая
проверка переносимости, а не научный результат.

Запуск (из repo/morphogenesis, как и остальные прогоны):
    python ../scripts/ci_canary_pond.py
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MORPH = ROOT / "morphogenesis"
BASE = ["--steps", "150", "--grid", "32", "--seed", "7"]


def run_arm(name: str, extra: list[str]) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / f"{name}.json"
        cmd = [sys.executable, "world/run_pond.py", "--device", "cpu", "--out", str(out), *BASE, *extra]
        proc = subprocess.run(cmd, cwd=MORPH, capture_output=True, text=True, timeout=1800)
        if proc.returncode != 0:
            print(proc.stdout[-2000:])
            print(proc.stderr[-2000:], file=sys.stderr)
            raise SystemExit(f"канарейка: плечо {name} упало с кодом {proc.returncode}")
        data = json.loads(out.read_text(encoding="utf-8"))
        summary = data.get("summary", data)
        final = summary.get("final") or {}
        return {
            "arm": name,
            "pop_time": summary.get("pop_time"),
            "alive_final": final.get("alive_cells"),
            "died": final.get("died"),
            "born": final.get("born"),
            "deaths_by_zone": summary.get("deaths_by_zone"),
        }


def check(results: list[dict]) -> list[str]:
    problems: list[str] = []
    for item in results:
        if not item["pop_time"] or item["pop_time"] <= 0:
            problems.append(f"{item['arm']}: pop_time не положителен ({item['pop_time']})")
        if item["alive_final"] is None:
            problems.append(f"{item['arm']}: нет alive_final")
        zones = item.get("deaths_by_zone") or {}
        zone_total = sum(v for v in zones.values() if isinstance(v, int))
        if isinstance(item.get("died"), int) and zone_total and zone_total != item["died"]:
            problems.append(
                f"{item['arm']}: счётчики смертей расходятся (зоны {zone_total}, died {item['died']})"
            )
    repeats = [r for r in results if r["arm"].startswith("determinism")]
    if len(repeats) == 2 and repeats[0]["pop_time"] != repeats[1]["pop_time"]:
        problems.append(
            f"детерминизм: один и тот же сид дал разные pop_time "
            f"({repeats[0]['pop_time']} и {repeats[1]['pop_time']})"
        )
    return problems


def main() -> int:
    results = [
        run_arm("baseline", []),
        run_arm("ifd", ["--spore-bias", "ifd"]),
        run_arm("determinism_1", []),
        run_arm("determinism_2", []),
    ]
    problems = check(results)
    payload = {"device": "cpu", "arms": results, "problems": problems}
    (ROOT / "_ci_canary.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if problems:
        print("канарейка: провал", file=sys.stderr)
        return 1
    print("канарейка: инварианты держатся на CPU")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
