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
        # аудит библиотекаря 31.10: числа статьи 028 обязаны воспроизводиться из агрегатов
        # гейты, появившиеся после разбора 31.10 (P4, P5)
        ("план разложен без потерь", [PY, "scripts/check_plan_split.py", "--ci"], None),
        ("снимки совпадают с диском", [PY, "scripts/check_snapshots.py", "--ci"], None),
        ("индекс скриптов полон и свеж", [PY, "scripts/check_script_index.py", "--ci"], None),
        ("числа статьи 028 совпадают с агрегатами", [PY, "scripts/check_article_numbers.py", "--ci"], None),
        ("числа статьи 029 совпадают с таблицами и агрегатами", [PY, "scripts/check_article_029_numbers.py", "--ci"], None),
        ("числа статьи 030 совпадают с агрегатами", [PY, "scripts/check_article_030_numbers.py", "--ci"], None),
        ("матрица утверждений (claims_lint --strict)", [PY, "scripts/claims_lint.py", "--strict"], None),
        ("ссылки на разделы рукописи", [PY, "scripts/check_section_refs.py"], None),
        # 01.11: CI падал на шаге «Text integrity», а локальный verify был зелёным, потому что звал
        # check_section_refs и не звал check_links. После разбиения плана 83 ссылки в docs/plan/*.md
        # указывали на уровень выше нужного и вели в никуда; нашлись только в CI. Гейт зовётся здесь.
        ("относительные ссылки ведут в существующие файлы", [PY, "scripts/check_links.py", "--all"], None),
    # 03.11 (X122/X123): the tracker retires a uid when it divides, so no parent may outlive its child. A run that violated it would
    # silently invalidate every survival number in the line, and the check reads stored runs rather than trusting the flags.
    ("правило идентичности uid подтверждено на сохранённых прогонах", [PY, "scripts/check_uid_rule.py"], None),
        # 01.11: CI падал на «Text integrity», потому что семь планов были заведены без строки в индексе отчётов,
        # а check_reports_index не входил в локальный набор. Теперь входит: индекс отчётов — часть гейта.
        ("индекс отчётов покрывает все отчёты", [PY, "scripts/check_reports_index.py"], None),
        # 01.11: у 93 ссылок в плане адрес в _hourly/ указывает в пустоту — артефакты жили вне git и не сохранились.
        # Гейт не чинит историю, он не даёт числу вырасти: новая ссылка на _hourly/ красит проверку.
        ("ссылки не ведут в потерянный _hourly/", [PY, "scripts/check_hourly_refs.py", "--ci"], None),
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
        # 30.10, входящий аудит lexspec (M-2): спека — единственный носитель требований; если их две,
        # читатель не узнает действующую.
        ("одна действующая спецификация", [PY, "scripts/check_single_spec.py", "--ci"], None),
        # B-067 с доски: реализаций интервала Уилсона пять, они могут разойтись незаметно.
        ("реализации интервала Уилсона согласованы", [PY, "scripts/check_wilson_consistency.py", "--ci"], None),
        # B-068 с доски: MI по гистограммам смещена вверх на конечной выборке; калибровка на
        # синтетике с известным ответом (независимые → 0, y=x → H(x), масштаб не влияет).
        ("оценка взаимной информации откалибрована", [PY, "scripts/check_mutual_information.py", "--ci"], None),
        # §4k: агрегат линии поля должен совпадать с артефактами в репозитории (до 30.10 артефакты лежали вне git)
        ("агрегат линии поля совпадает с артефактами", [PY, "scripts/l1_field_matrix.py", "--check"], None),
    ("сид-репликация не выдаёт один мир за пять", [PY, "scripts/check_seed_replication.py", "--check"], None),
    ("пре-регистрации несут пять разделов", [PY, "scripts/check_design.py", "--scan-plans"], None),
    ("политика автономии читается машиной", [PY, "scripts/check_autonomy.py"], None),
        # 08.11: four defects in the world were found by a human reading the code - budding created
        # energy, age killed, repair_cost was charged every step, a step was unaffordable at its own
        # price. No gate tripped. This one checks the invariants directly.
        ("инварианты мира держатся", [PY, "scripts/world_invariants.py"], None),
        ("артефакт восстанавливает мир (полнота конфига)",
         [PY, "scripts/check_config_completeness.py"], None),
    ("страница внимания не теряет решений", [PY, "scripts/attention.py", "--check"], None),
    ("артефакт, на который ссылается утверждение, лежит в git", [PY, "scripts/check_claim_artifacts.py", "--ci"], None),
        # X19 (по схеме LongTails): утверждение отдельно от Setup, бюджет явно, аудит отказывает при выходе за допущения
        ("утверждения проходят аудит против Setup", [PY, "scripts/claim_comparator.py", "--ci"], None),
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
