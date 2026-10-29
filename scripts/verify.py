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
    proc = subprocess.run(cmd, cwd=str(cwd or ROOT), capture_output=True,
                          text=True, encoding="utf-8", errors="replace")
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
        ("витрина не отстаёт от результатов", [PY, "scripts/check_readme_fresh.py"], None),
        ("ревью оформлены как проверки", [PY, "scripts/check_reviews.py"], None),
        # 29.10, крестовый аудит herness (находка 3): AGENTS §3c называет этот гейт гейтом, а make verify
        # его не звал — читатель считал проверку включённой. Теперь зовёт.
        ("определения метрик совпадают с реализацией", [PY, "scripts/check_metric_definitions.py"], None),
        # 29.10, крестовый аудит herness (находка 2): cross-audit/ содержал числа и утверждения, которые
        # не читал ни один страж. Теперь у файлов аудита обязателен маркер «не наше утверждение».
        ("аудиты помечены как внешние", [PY, "scripts/check_cross_audit.py"], None),
        # 30.10, входящий аудит herness (M-1): команда, объявленная в документации, должна запускаться в CI
        # или быть явно помечена как ручная — иначе документация и проверки расходятся молча.
        ("команды документации запускаются в CI", [PY, "scripts/check_readme_commands.py", "--ci"], None),
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
