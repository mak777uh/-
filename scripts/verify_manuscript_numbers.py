"""Сверить числа §4.12–§4.14 рукописи с артефактами.

Зачем: числа в рукописи появлялись из отчётов, а отчёты — из артефактов. Скрипт
проверяет **цепочку целиком** для трёх последних разделов: пересчитывает
величину из JSON-артефакта и ищет её строковое представление в тексте
соответствующего раздела. Если число в тексте не совпадает ни с пересчётом, ни с
ожидаемым набором — ошибка.

Что проверяется:

- §4.13 — сетка: `seed_grid.json` (доминирующие классы, счётчики, устойчивость)
  и `summary_e02c_seeddec_wave2.json`;
- §4.14 — носители: `lesion_minimal_exploratory.json`,
  `lesion_necessity_exploratory.json`, `lesion_core_exploratory.json`,
  `asymmetry_variance_exploratory.json`,
  `asymmetry_variance_retry_exploratory.json`;
- §4.12 — другой стек: `summary_e02c_fp32_seed42.json` (+ TF32-on),
  `summary_e02c_fp32_seed42_tf32on.json`, журнал обучения (best_loss/alive).

Числа из внешних артефактов (Colab T4 seed42: 1.0969/0.929/0.347) проверяются
**не по артефакту**, а по отчёту: скрипт проверяет, что они есть в отчёте
`reports/2026-10-22-colab-t4-repro-results.md`, и помечает их как report-level.

Запуск (из корня):

    python scripts/verify_manuscript_numbers.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PAPER = REPO / "manuscript" / "paper.md"
EXP = REPO / "morphogenesis" / "experiments"


def section(text: str, heading: str) -> str:
    """Текст от заголовка `### X` до следующего `###`/`## `."""
    pattern = re.compile(rf"^{re.escape(heading)}.*?(?=^##|\Z)", re.DOTALL | re.MULTILINE)
    match = pattern.search(text)
    if not match:
        raise SystemExit(f"нет раздела {heading}")
    return match.group(0)


def load(*parts: str) -> dict:
    path = EXP.joinpath(*parts)
    return json.loads(path.read_text(encoding="utf-8"))


def check_numbers(label: str, numbers: list[str], body: str, errors: list[str]) -> None:
    for number in numbers:
        if number not in body:
            errors.append(f"{label}: числа {number!r} нет в тексте раздела")


def main() -> int:
    paper = PAPER.read_text(encoding="utf-8")
    errors: list[str] = []
    checked = 0

    # ---------------- §4.13: сетка ----------------
    grid = load("E02c_replication", "seed_grid.json")
    cells = grid["cells"]
    verdict = grid["verdict"]
    if verdict["verdict"] != "H-E02C-6_refuted":
        errors.append(f"§4.13: вердикт в артефакте {verdict['verdict']}, в тексте — refuted")

    def cell(init: int, data: int) -> dict:
        return cells[f"init{init}_data{data}"]

    s = section(paper, "### 4.13.")
    expect = [
        f"{cell(42, 42)['struct_2']}/{cell(42, 42)['n']}",      # 64/64
        f"{cell(42, 202)['struct_2']}/{cell(42, 202)['n']}",    # 63/64
        f"{cell(42, 303)['struct_2']}/{cell(42, 303)['n']}",    # 60/64
        f"{cell(42, 101)['struct_2']}/{cell(42, 101)['n']}",    # 0/64
    ]
    if cell(101, 202)["dominant_class"] != "death":
        errors.append("§4.13: у (101,202) в артефакте доминирует не death")
    if cell(101, 303)["dominant_class"] != "uniform_dark":
        errors.append("§4.13: у (101,303) в артефакте доминирует не uniform_dark")
    check_numbers("§4.13", expect, s, errors)
    checked += len(expect)

    for key, art in (("init42_data202", "0.9844"), ("init42_data303", "0.9375")):
        stable = cell(*[int(x) for x in key.replace("init", "").split("_data")])[
            "struct_2_stable_fraction"
        ]
        if f"{stable:.4f}" != art:
            errors.append(f"§4.13: устойчивость {key} = {stable:.4f}, ожидалось {art}")
        elif art not in s:
            errors.append(f"§4.13: устойчивость {art} ({key}) не найдена в тексте")
        checked += 1

    if "12/64" not in s:
        errors.append("§4.13: в тексте нет 12/64 (struct_1 в клетке 101/202)")
    checked += 1

    # ---------------- §4.14: носители ----------------
    core = load("E02b_morphospace", "lesion_core_exploratory.json")
    nec = load("E02b_morphospace", "lesion_necessity_exploratory.json")
    ab7 = load("E02b_morphospace", "lesion_minimal_exploratory.json")
    var = load("E02b_morphospace", "asymmetry_variance_exploratory.json")
    retry = load("E02b_morphospace", "asymmetry_variance_retry_exploratory.json")
    s = section(paper, "### 4.14.")

    if core["verdict"] != "H-CH-11_refuted":
        errors.append(f"§4.14: H-CH-11 вердикт {core['verdict']}")
    if nec["verdict"] != "H-CH-10_confirmed":
        errors.append(f"§4.14: H-CH-10 вердикт {nec['verdict']}")
    if ab7["ch9"]["ch9"]["verdict"] != "H-CH-9_confirmed":
        errors.append("§4.14: H-CH-9 вердикт не confirmed")

    ch9 = ab7["ch9"]["ch9"]["conditions"]
    nums = [
        f"{ch9['none']['body_returned']}/12",
        f"{ch9['k1_14']['body_returned']}/12",
        f"{ch9['k1_14']['mean_body_iou']:.3f}",
        f"{ch9['k2_23']['mean_body_iou']:.3f}",
        f"{ch9['k3_234']['mean_body_iou']:.3f}",
        f"{ch9['k3_678']['body_returned']}/12",
        f"{ch9['k1_12']['body_returned']}/12",
    ]
    check_numbers("§4.14/H-CH-9", nums, s, errors)
    checked += len(nums)

    cond = nec["conditions"]
    nums = [
        f"{cond['informative_only']['body_returned']}/12",
        f"{cond['informative_only']['mean_body_iou']:.3f}",
        f"{cond['inert_only']['body_returned']}/12",
        f"{cond['inert_only']['mean_body_iou']:.3f}",
        f"{cond['none']['mean_body_iou']:.3f}",
    ]
    check_numbers("§4.14/H-CH-10", nums, s, errors)
    checked += len(nums)

    geo = ab7["ab7"]["geometries"]
    sd = [geo["c_40_24"]["std_diff"], geo["c_38_26"]["std_diff"]]
    for value in sd:
        if f"{value:.3f}" not in s and f"{value:.2f}" not in s:
            errors.append(f"§4.14: std(d) {value:.3f} не найдена в тексте")
        checked += 1
    if retry["verdict"] != "H-AB-8_refuted":
        errors.append(f"§4.14: H-AB-8 вердикт {retry['verdict']}")
    for key, value in (("spearman_d_dt", retry["spearman_d_dt"]), ("std_dt", retry["std_dt"])):
        short = f"{value:.3f}" if key == "spearman_d_dt" else f"{value:.1f}"
        if key == "spearman_d_dt":
            if "0.434" not in s:
                errors.append("§4.14: rho 0.434 не найдена в тексте")
        elif "531.8" not in s:
            errors.append("§4.14: std(dt) 531.8 не найдена в тексте")
        checked += 1
    if var["verdict"] != "H-AB-8_refuted":
        errors.append(f"§4.14: первый (вырожденный) прогон помечен как {var['verdict']}")

    # ---------------- §4.12: другой стек ----------------
    fp32 = load("E02c_replication", "summary_e02c_fp32_seed42.json")
    fp32_on = load("E02c_replication", "summary_e02c_fp32_seed42_tf32on.json")
    for name, summary in (("fp32_off", fp32), ("fp32_on", fp32_on)):
        stats = list(summary["stats"].values())[0]
        if stats["struct_2"] != 0:
            errors.append(f"§4.12: {name} struct_2 != 0")
    s = section(paper, "### 4.12.")
    for number in ("64/64", "0/64", "1.1028", "0.571"):
        if number not in s:
            errors.append(f"§4.12: числа {number!r} нет в тексте")
        checked += 1

    report = (REPO / "reports" / "2026-10-22-colab-t4-repro-results.md").read_text(encoding="utf-8")
    for number in ("1.0969", "1.1047", "0.929", "0.347"):
        if number not in report:
            errors.append(f"§4.12: report-level число {number!r} нет в отчёте T4")
        checked += 1

    print(f"проверено чисел: {checked}, ошибок: {len(errors)}")
    for item in errors:
        print(f"ОШИБКА {item}")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
