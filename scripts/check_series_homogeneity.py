"""Гейт: серия должна быть снята одним кодом.

Класс ошибки (26.10, вечер): серия `w1niche` (§10ay) собиралась **на четырёх коммитах кода** —
`legacy` на `65c77e5`, `adjacency_exact` на `e2ce18c`/`984454a`/`f365ec3`. Парное сравнение плеч по сидам
предполагает одинаковую физику; её не было. Прогон на текущем коде не воспроизводит старые артефакты
(`prepared_cells_total` 766 против 1988), хотя текущий код детерминирован — значит различие не в шуме,
а в коде. Вывод «5 из 9» при этом был записан как «на границе», то есть почти как результат.

Индикатор, который мы смотрели раньше (`git_dirty`), этого не показывает: он про незакоммиченные файлы
рабочей копии, а не про код, которым снят артефакт. Правильный индикатор — `config.git_code_commit`.

**`git_dirty` как индикатор не годится** (проверено 26.10): он считается по всей рабочей копии, а в ней
одновременно работают несколько агентов и постоянно меняется журнал, поэтому `dirty = true` почти всегда
(144 из 295 артефактов пруда). Поэтому в этом гейте он не используется — только `git_code_commit`.

Правило: **все артефакты одной серии обязаны нести один `git_code_commit`** (или явное исключение в
`lab/homogeneity-exemptions.json` с причиной). Иначе серия `invalid_by_data` по гомогенности, и её числа
не публикуются.
"""

from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "morphogenesis" / "experiments"
REGISTRY = ROOT / "lab" / "homogeneity.json"
# серия = каталог с артефактами; файлы агрегатов (*_matrix.json) не считаются
SKIP = re.compile(r"(_matrix\.json$|/pilot/|/quarantine/)")

IGNORED_KEYS = {"git_commit", "git_dirty", "wall_seconds", "run_id", "timestamp", "notes"}


def code_commit(payload: dict) -> str | None:
    for container in (payload.get("summary") or {}, payload, payload.get("config") or {}):
        cfg = container.get("config") if isinstance(container, dict) else None
        for source in (cfg, container):
            if isinstance(source, dict):
                for key in ("git_code_commit", "code_commit"):
                    value = source.get(key)
                    if isinstance(value, str) and value.strip():
                        return value.strip()
    return None


def scan() -> dict[str, dict]:
    series: dict[str, dict] = {}
    for path in sorted(EXPERIMENTS.rglob("*.json")):
        rel = path.relative_to(ROOT).as_posix()
        if SKIP.search(rel):
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if not isinstance(payload, dict):
            continue
        commit = code_commit(payload)
        dirty = None
        for container in (payload.get("summary") or {}, payload):
            source = container.get("config") if isinstance(container, dict) else None
            for candidate in (source, container):
                if isinstance(candidate, dict) and isinstance(candidate.get("git_dirty"), bool):
                    dirty = candidate["git_dirty"]
                    break
            if dirty is not None:
                break

        family = path.parent.relative_to(EXPERIMENTS).as_posix()
        entry = series.setdefault(family, {"files": 0, "commits": collections.Counter(), "dirty": set()})
        entry["files"] += 1
        entry["commits"][commit or "unknown"] += 1
        if dirty is not None:
            entry["dirty"].add(dirty)
    return series


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="серия должна быть снята одним кодом")
    ap.add_argument("--strict", action="store_true", help="различия = ошибка (в lab_health)")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args(argv)

    registry: dict[str, dict] = {}
    if REGISTRY.exists():
        loaded = json.loads(REGISTRY.read_text(encoding="utf-8"))
        for key in ("invalid", "archived_invalid", "verified_equivalent", "unverified"):
            for family, reason in (loaded.get(key) or {}).items():
                registry[family] = {"kind": key, "reason": reason}

    series = scan()
    for family, entry in sorted(series.items()):
        # «все грязные» = снято с одного незакоммиченного состояния (допустимо, если нейтральность проверена).
        # «разные значения внутри серии» = дерево менялось по ходу серии — это красный флаг.
        if len(entry.get("dirty") or ()) > 1:
            mixed_dirty.append(f"{family}: внутри серии разные git_dirty ({entry['dirty']}) — дерево менялось по ходу")
    problems: list[str] = []
    warned: list[str] = []
    mixed_dirty: list[str] = []
    mixed = 0
    for family, entry in sorted(series.items()):
        real = {c: n for c, n in entry["commits"].items() if c != "unknown"}
        if len(real) <= 1:
            if args.verbose:
                print(f"[homogeneity] {family}: {entry['files']} файлов, код: {list(real) or 'не записан'}")
            continue
        mixed += 1
        detail = ", ".join(f"{c}×{n}" for c, n in sorted(real.items(), key=lambda kv: -kv[1]))
        known = registry.get(family) or registry.get(family + "/")
        if known and known["kind"] == "verified_equivalent":
            print(f"[homogeneity] проверено эквивалентным {family}: {known['reason']}")
            continue
        if known and known["kind"] == "archived_invalid":
            print(f"[homogeneity] отозвано {family}: {known['reason']}")
            continue
        if known and known["kind"] == "invalid":
            problems.append(f"{family}: СЕРИЯ НЕВАЛИДНА по гомогенности ({detail}) — {known['reason']}")
            continue
        if known and known["kind"] == "unverified":
            warned.append(f"{family}: {len(real)} коммитов ({detail}) — {known['reason']}")
            continue
        problems.append(f"{family}: {entry['files']} файлов на {len(real)} коммитах кода ({detail}) — не в реестре")

    for note in mixed_dirty:
        print(f"[homogeneity] предупреждение: {note}")
    for note in warned:
        print(f"[homogeneity] предупреждение: {note}")
    if problems:
        print(f"[homogeneity] серий с несколькими коммитами: {mixed}")
        for problem in problems:
            print(f"[homogeneity]   ОШИБКА: {problem}")
        print("[homogeneity] серия должна быть снята одним кодом, иначе парное сравнение плеч недействительно")
        return 1 if args.strict else 0
    print(f"[homogeneity] OK — серий на нескольких коммитах нет (проверено {len(series)} семейств)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
