"""Независимая проверка артефакта E02b clusters-3 (H-CH-8, H-AB-6).

Сводки пересчитываются из сырых строк (`clusters3_rows.jsonl`), вердикты — заново
по протоколу `reports/2026-10-22-clusters3-plan.md`. Без строк (свежий клон)
проверяется внутренняя согласованность артефакта.

Запуск: `python e02b_verify_clusters3.py` из корня репозитория.
"""
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve()
EXP = HERE.parents[1]
OUT = EXP / "clusters3_exploratory.json"
ROWS = EXP / "clusters3_rows.jsonl"

IOU_MIN = 0.5
SIGN_MIN = 11
REPEATS = 12
DEAD_ALIVE = 0.05
MASS_TOL = 0.01
AB6_LOW, AB6_HIGH = 0.58, 0.68

errors = []
warnings = []


def check(cond, msg):
    if cond:
        print("OK  ", msg)
    else:
        print("FAIL", msg)
        errors.append(msg)


def warn(cond, msg):
    if not cond:
        print("WARN", msg)
        warnings.append(msg)


def load_rows(path):
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


artifact = json.load(open(OUT, encoding="utf-8")) if OUT.exists() else None
if artifact is None:
    sys.exit("нет артефакта — проверять нечего")
rows = load_rows(ROWS)
has_rows = bool(rows)
print(f"[verify] строк={len(rows)} моделей={len(artifact.get('models') or [])}")
if not has_rows:
    warn(False, f"нет {ROWS.name}: сверка со строками пропущена (файл локальный)")

check(artifact.get("protocol") == "reports/2026-10-22-clusters3-plan.md",
      "артефакт ссылается на замороженный протокол")
check(artifact.get("steps") == 2000, "шагов 2000")
check(artifact.get("repeats") == REPEATS, f"повторов {REPEATS}")

models = {m["family"]: m for m in artifact.get("models") or [] if m.get("ch8")}
struct2 = models.get("WP4_R-9_s2000_seed42")
check(struct2 is not None, "есть модель struct_2 с секцией H-CH-8")

rows_by = {}
for row in rows:
    rows_by.setdefault((row["section"], row["family"], row.get("condition")), []).append(row)

if struct2:
    for cond, summary in struct2["ch8"].items():
        check(summary.get("n") == REPEATS, f"struct_2 {cond}: n={REPEATS}")
        if not has_rows:
            continue
        subset = rows_by.get(("H-CH-8", "WP4_R-9_s2000_seed42", cond), [])
        check(len(subset) == summary.get("n"),
              f"struct_2 {cond}: n сходится со строками ({len(subset)})")
        body = sum(1 for r in subset if r["body_iou"] >= IOU_MIN)
        alive = sum(1 for r in subset if r["alive_fraction"] >= DEAD_ALIVE)
        check(body == summary.get("body_returned"),
              f"struct_2 {cond}: body_returned {summary.get('body_returned')} пересчитан как {body}")
        check(alive == summary.get("alive"),
              f"struct_2 {cond}: alive {summary.get('alive')} пересчитан как {alive}")
        check(dict(Counter(r["final_class"] for r in subset)) == summary.get("classes"),
              f"struct_2 {cond}: классы сходятся")
        mean = round(float(sum(r["body_iou"] for r in subset) / len(subset)), 4)
        check(abs(mean - summary.get("mean_body_iou", 0.0)) < 1e-6,
              f"struct_2 {cond}: средний body_iou сходится ({mean})")

# --- H-CH-8 вердикт ----------------------------------------------------------
if struct2:
    none_st = struct2["ch8"].get("none", {})
    a_st = struct2["ch8"].get("group_a_only", {})
    b_st = struct2["ch8"].get("group_b_only", {})
    if none_st.get("body_returned", 0) < SIGN_MIN:
        expected = {"applicable": False}
    else:
        ok = [name for name, st in (("group_a_2_7", a_st), ("group_b_8_14", b_st))
              if st.get("body_returned", 0) >= SIGN_MIN]
        expected = {
            "applicable": True,
            "verdict": "confirmed_single_group_sufficient" if ok else "refuted_single_group_insufficient",
        }
    got = artifact.get("verdict_ch8") or {}
    check(bool(got.get("applicable")) == expected["applicable"],
          f"H-CH-8 applicable={got.get('applicable')} соответствует протоколу")
    if expected.get("verdict"):
        check(got.get("verdict") == expected["verdict"],
              f"H-CH-8 вердикт {got.get('verdict')} соответствует пересчёту ({expected['verdict']})")
        if expected["verdict"] == "confirmed_single_group_sufficient":
            check(set(got.get("sufficient_groups") or []) == set(
                [n for n, st in (("group_a_2_7", a_st), ("group_b_8_14", b_st))
                 if st.get("body_returned", 0) >= SIGN_MIN]),
                "H-CH-8: список достаточных групп сходится")
    print("[verify] H-CH-8:", got.get("verdict"), "—", (got.get("reason") or "")[:150])

# --- H-AB-6 ------------------------------------------------------------------
ab6 = next((m["ab6"] for m in artifact.get("models") or [] if m.get("ab6")), None)
check(ab6 is not None, "есть секция H-AB-6")
if ab6:
    pairs = ab6.get("pairs") or []
    check(len(pairs) == 11, f"H-AB-6: пар {len(pairs)} (ожидалось 11)")
    valid = [p for p in pairs if p.get("valid")]
    for pair in valid:
        gap = abs(pair["removed_fraction_left"] - pair["removed_fraction_right"])
        check(gap <= MASS_TOL + 1e-9, f"H-AB-6 пара {pair['pair']}: масса выровнена (gap={gap:.4f})")
        check(0.50 <= pair["removed_fraction_left"] <= 0.70,
              f"H-AB-6 пара {pair['pair']}: q в заявленном диапазоне")
        recomputed = round(pair["iou_left"] - pair["iou_right"], 4)
        check(abs(recomputed - pair["diff"]) < 1e-9,
              f"H-AB-6 пара {pair['pair']}: diff пересчитан {recomputed:+.4f}")
    diffs = [p["diff"] for p in valid]
    abs_max = max((abs(d) for d in diffs), default=0.0)
    all_neg = bool(diffs) and all(d < 0 for d in diffs)
    check(abs(abs_max - ab6.get("max_abs_diff", 0.0)) < 1e-3,
          f"H-AB-6: max|d| {ab6.get('max_abs_diff')} пересчитан {round(abs_max, 4)}")
    check(all_neg == ab6.get("all_negative"), "H-AB-6: флаг «все отрицательны» сходится")
    expected_verdict = (
        "confirmed_hump" if (all_neg and AB6_LOW <= abs_max <= AB6_HIGH) else "not_confirmed"
    )
    check(ab6.get("verdict") == expected_verdict,
          f"H-AB-6 вердикт {ab6.get('verdict')} соответствует критерию ({expected_verdict})")
    print(f"[verify] H-AB-6: max|d|={round(abs_max, 4)}, все отрицательны={all_neg} -> {ab6.get('verdict')}")

print()
if errors:
    print(f"ИТОГ: {len(errors)} ошибок, {len(warnings)} предупреждений")
    for err in errors:
        print("  -", err)
    sys.exit(1)
print(f"ИТОГ: 0 ошибок, {len(warnings)} предупреждений")
