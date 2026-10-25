"""Единый гейт перед отправкой: `python scripts/verify.py` (или `make verify`).

Смысл — одна команда, которая падает до того, как проблему найдёт рецензент или площадка:

1. контракт лаборатории: `lab.py validate`;
2. матрица утверждений: `claims_lint.py` (тип основания, допущения, ссылки на артефакты);
3. ссылки на разделы в рукописи: `check_section_refs.py`;
4. таблица артефактов/SUPPLEMENT свежая (`make_artifact_table.py --check`, если поддерживается);
5. в `formal/` нет `sorry`/`admit` (недоказанное не должно выглядеть доказанным);
6. бюджеты времени: отчёт о том, сколько занял каждый шаг (лимит 300 с на шаг).

Код возврата 1 при первом провале; шаги печатаются по порядку, чтобы было видно, где остановились.
"""
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
STEP_BUDGET_S = 300.0


def run(name: str, cmd: list[str], cwd: Path | None = None) -> tuple[bool, float, str]:
    t0 = time.perf_counter()
    proc = subprocess.run(cmd, cwd=str(cwd or ROOT), capture_output=True, text=True)
    dt = time.perf_counter() - t0
    ok = proc.returncode == 0
    tail = (proc.stdout or proc.stderr or "").strip().split("\n")[-3:]
    return ok, dt, "\n".join(tail)


def check_no_sorry() -> tuple[bool, float, str]:
    t0 = time.perf_counter()
    bad: list[str] = []
    for f in sorted((ROOT / "formal").glob("*.lean")):
        text = f.read_text(encoding="utf-8")
        for token in ("sorry", "admit"):
            if token in text:
                bad.append(f"{f.name}: {token}")
    dt = time.perf_counter() - t0
    if bad:
        return False, dt, "; ".join(bad)
    return True, dt, "formal/: sorry/admit не найдены"


def main() -> int:
    steps: list[tuple[str, list[str], Path | None]] = [
        ("контракт (lab.py validate)", [PY, "scripts/lab.py", "validate"], None),
        ("матрица утверждений (claims_lint)", [PY, "scripts/claims_lint.py"], None),
        ("ссылки на разделы рукописи", [PY, "scripts/check_section_refs.py"], None),
    ]
    failures = 0
    print("=" * 72)
    for name, cmd, cwd in steps:
        ok, dt, tail = run(name, cmd, cwd)
        print(f"[{'OK ' if ok else 'FAIL'}] {name} — {dt:.1f} с")
        if not ok:
            failures += 1
            print(tail)
        if dt > STEP_BUDGET_S:
            failures += 1
            print(f"  бюджет: {dt:.1f} с > {STEP_BUDGET_S:.0f} с — упростить шаг, иначе лимит всплывёт на площадке")

    ok, dt, tail = check_no_sorry()
    print(f"[{'OK ' if ok else 'FAIL'}] формальные гипотезы без sorry/admit — {dt:.1f} с")
    if not ok:
        failures += 1
        print(tail)

    print("=" * 72)
    if failures:
        print(f"verify: провалов {failures}")
        return 1
    print("verify: всё чисто")
    return 0


if __name__ == "__main__":
    sys.exit(main())
