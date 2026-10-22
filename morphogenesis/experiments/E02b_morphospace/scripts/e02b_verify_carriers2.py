"""Независимая проверка артефакта E02b carriers-2 (H-CH-7, H-AB-5).

Сводки пересчитываются из сырых строк (`carriers2_rows.jsonl`), вердикты — заново
по протоколу `reports/2026-10-22-carriers2-plan.md`. Без строк (свежий клон)
проверяется внутренняя согласованность артефакта.

Запуск: `python e02b_verify_carriers2.py` из корня репозитория.
"""
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve()
EXP = HERE.parents[1]
OUT = EXP / "carriers2_exploratory.json"
ROWS = EXP / "carriers2_rows.jsonl"

IOU_MIN = 0.5
SIGN_MIN = 11
REPEATS = 12
DEAD_ALIVE = 0.05
MASS_TOL = 0.01
AB5_MEDIAN = -0.60

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

check(artifact.get("protocol") == "reports/2026-10-22-carriers2-plan.md",
      "артефакт ссылается на замороженный протокол")
check(artifact.get("steps") == 2000, "шагов 2000")
check(artifact.get("repeats") == REPEATS, f"повторов {REPEATS}")

models = {m["family"]: m for m in artifact.get("models") or [] if m.get("ch7")}
struct2 = models.get("WP4_R-9_s2000_seed42")
check(struct2 is not None, "есть модель struct_2 с секцией H-CH-7")

rows_by = {}
for row in rows:
    rows_by.setdefault((row["section"], row["family"], row.get("condition")), []).append(row)

if struct2:
    for cond, summary in struct2["ch7"].items():
        check(summary.get("n") == REPEATS, f"struct_2 {cond}: n={REPEATS}")
        if not has_rows:
            continue
        subset = rows_by.get(("H-CH-7", "WP4_R-9_s2000_seed42", cond), [])
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

# --- H-CH-7 вердикт ----------------------------------------------------------
if struct2:
    none_st = struct2["ch7"].get("none", {})
    open_st = struct2["ch7"].get("visible_zeroed_alive_open", {})
    if none_st.get("body_returned", 0) < SIGN_MIN:
        expected = {"applicable": False}
    elif open_st.get("body_returned", 0) >= SIGN_MIN:
        expected = {"applicable": True, "verdict": "refuted_visible_not_necessary"}
    elif (REPEATS - open_st.get("body_returned", 0)) >= SIGN_MIN:
        expected = {"applicable": True, "verdict": "confirmed_visible_necessary"}
    else:
        expected = {"applicable": True, "verdict": "inconclusive"}
    got = artifact.get("verdict_ch7") or {}
    check(bool(got.get("applicable")) == expected["applicable"],
          f"H-CH-7 applicable={got.get('applicable')} соответствует протоколу")
    if expected.get("verdict"):
        check(got.get("verdict") == expected["verdict"],
              f"H-CH-7 вердикт {got.get('verdict')} соответствует пересчёту ({expected['verdict']})")
    print("[verify] H-CH-7:", got.get("verdict"), "—", (got.get("reason") or "")[:150])

# --- H-AB-5 ------------------------------------------------------------------
ab5 = next((m["ab5"] for m in artifact.get("models") or [] if m.get("ab5")), None)
check(ab5 is not None, "есть секция H-AB-5")
if ab5:
    pairs = ab5.get("pairs") or []
    check(len(pairs) == REPEATS, f"H-AB-5: пар {len(pairs)}")
    valid = [p for p in pairs if p.get("valid")]
    for pair in valid:
        gap = abs(pair["removed_fraction_left"] - pair["removed_fraction_right"])
        check(gap <= MASS_TOL + 1e-9, f"H-AB-5 пара {pair['pair']}: масса выровнена (gap={gap:.4f})")
        check(0.45 <= pair["removed_fraction_left"] <= 0.75,
              f"H-AB-5 пара {pair['pair']}: q в заявленном диапазоне")
        recomputed = round(pair["iou_left"] - pair["iou_right"], 4)
        check(abs(recomputed - pair["diff"]) < 1e-9,
              f"H-AB-5 пара {pair['pair']}: diff пересчитан {recomputed:+.4f}")
    diffs = [p["diff"] for p in valid]
    signs = [1 if d > 0 else (-1 if d < 0 else 0) for d in diffs]
    check({str(k): v for k, v in Counter(signs).items()} == ab5.get("sign_counts"),
          "H-AB-5: знаки сходятся")
    median = float(sorted(diffs)[len(diffs) // 2]) if len(diffs) % 2 else (
        float((sorted(diffs)[len(diffs) // 2 - 1] + sorted(diffs)[len(diffs) // 2]) / 2)
        if diffs else 0.0
    )
    # медиана в артефакте округлена до 4 знаков — сравниваем с этим допуском
    check(abs(median - ab5.get("median_diff", 0.0)) < 1e-3,
          f"H-AB-5: медиана {ab5.get('median_diff')} пересчитана {round(median, 4)}")
    sign_ok = bool(signs) and Counter(signs).most_common(1)[0][1] >= SIGN_MIN and -1 in Counter(signs)
    median_ok = median <= AB5_MEDIAN
    expected_verdict = "confirmed_dose_response" if (sign_ok and median_ok) else "not_confirmed"
    check(ab5.get("verdict") == expected_verdict,
          f"H-AB-5 вердикт {ab5.get('verdict')} соответствует критерию ({expected_verdict})")
    print(f"[verify] H-AB-5: медиана {ab5.get('median_diff')}, "
          f"знаки {ab5.get('sign_counts')}, валидных {ab5.get('n_valid')} -> {ab5.get('verdict')}")

print()
if errors:
    print(f"ИТОГ: {len(errors)} ошибок, {len(warnings)} предупреждений")
    for err in errors:
        print("  -", err)
    sys.exit(1)
print(f"ИТОГ: 0 ошибок, {len(warnings)} предупреждений")
