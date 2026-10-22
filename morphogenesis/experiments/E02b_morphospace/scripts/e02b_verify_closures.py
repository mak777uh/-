"""Независимая проверка артефактов E02b closures (H-CH-2/3/4, H-AB-2).

Правило то же, что у `e02b_verify_exploratory.py`: сводки **пересчитываются из
сырых строк** (`closures_rows.jsonl`), а не читаются из harness-полей; вердикты
переписываются здесь заново по протоколу
`reports/2026-10-21-e02b-closures-plan.md`. Если артефакт и скрипт разойдутся,
проверка это поймает.

Запуск: `python e02b_verify_closures.py` (из корня репозитория).
"""
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve()
EXP = HERE.parents[1]
OUT = EXP / "closures_exploratory.json"
ROWS = EXP / "closures_rows.jsonl"

DEAD_ALIVE = 0.05
IOU_MIN = 0.5
SIGN_MIN = 11
REPEATS = 12
MASS_TOL = 0.01

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


def load_json(path):
    if not path.exists():
        print(f"SKIP {path.name}: нет артефакта")
        return None
    return json.load(open(path, encoding="utf-8"))


def load_rows(path):
    if not path.exists():
        print(f"SKIP {path.name}: нет строк")
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


artifact = load_json(OUT)
rows = load_rows(ROWS)
if artifact is None:
    sys.exit("нет артефакта — проверять нечего")

# `*_rows.jsonl` намеренно не едет в git (.gitignore): это локальные сырые строки,
# как веса. На свежем клоне сверка сводок со строками невозможна, поэтому она
# пропускается, а проверки внутренней согласованности артефакта остаются.
has_rows = bool(rows)
print(f"[verify] строк={len(rows)} моделей={len(artifact.get('models') or [])}")
if not has_rows:
    warn(False, f"нет {ROWS.name}: сверка сводок со строками пропущена (файл локальный)")

# ---------------------------------------------------------------- структура
check(
    artifact.get("protocol") == "reports/2026-10-21-e02b-closures-plan.md",
    "артефакт ссылается на замороженный протокол",
)
check(artifact.get("steps") == 2000, "шагов 2000")
check(artifact.get("repeats") == REPEATS, f"повторов {REPEATS}")
model_entries = {m["family"]: m for m in artifact.get("models") or []}
check(len(model_entries) == 3, "три модели в артефакте")

rows_by = {}
for row in rows:
    rows_by.setdefault((row["section"], row["family"]), []).append(row)

# ---------------------------------------------------------------- H-CH-2
for family, entry in model_entries.items():
    ch2 = entry.get("ch2") or {}
    check(bool(ch2), f"{family}: есть секция H-CH-2")
    none = ch2.get("none") or {}
    # Контроль none — ворота интерпретации, а не ошибка прогона: если прототип не
    # воспроизводит СВОЙ рисунок, то «сломан/не сломан рисунок» для этой модели
    # не определено. Так у R-9 seed101: класс стабилен (struct_1 12/12), рисунок —
    # нет (H-CH-1 уже это фиксировал). Модель исключается из вердикта, но
    # остаётся в отчёте.
    if none.get("same_pattern") == REPEATS:
        print(f"OK   {family}: контроль none держит рисунок {REPEATS}/{REPEATS}")
    else:
        warn(
            False,
            f"{family}: контроль none {none.get('same_pattern')}/{none.get('n')} — "
            "рисунок не самовоспроизводим, модель исключается из интерпретации H-CH-2/3",
        )
        entry["_baseline_valid"] = False
    for cond, summary in ch2.items():
        if not has_rows:
            continue
        subset = [
            r for r in rows_by.get(("H-CH-2", family), []) if r["condition"] == cond
        ]
        recomputed = sum(1 for r in subset if r["iou"] >= IOU_MIN)
        alive = sum(1 for r in subset if r["alive_fraction"] >= DEAD_ALIVE)
        check(
            len(subset) == summary.get("n"),
            f"{family} {cond}: n={summary.get('n')} совпадает со строками ({len(subset)})",
        )
        check(
            recomputed == summary.get("same_pattern"),
            f"{family} {cond}: same_pattern {summary.get('same_pattern')} пересчитан как {recomputed}",
        )
        check(
            alive == summary.get("alive"),
            f"{family} {cond}: alive {summary.get('alive')} пересчитан как {alive}",
        )
        check(
            dict(Counter(r["final_class"] for r in subset)) == summary.get("classes"),
            f"{family} {cond}: классы сходятся",
        )

# ---------------------------------------------------------------- H-CH-3
for family, entry in model_entries.items():
    ch3 = entry.get("ch3") or {}
    if not has_rows:
        check(ch3.get("n") == REPEATS, f"{family} H-CH-3: n={ch3.get('n')} (ожидалось {REPEATS})")
        continue
    subset = rows_by.get(("H-CH-3", family), [])
    check(ch3.get("n") == len(subset), f"{family} H-CH-3: n сходится")
    identity = sum(1 for r in subset if r["best_d4_index"] == 0 and r["best_d4_iou"] >= IOU_MIN)
    check(
        identity == ch3.get("identity_orientation"),
        f"{family} H-CH-3: identity {ch3.get('identity_orientation')} пересчитан как {identity}",
    )
    hist = {str(k): v for k, v in Counter(int(r["best_d4_index"]) for r in subset).items()}
    check(hist == ch3.get("d4_histogram"), f"{family} H-CH-3: гистограмма D4 сходится")

# ---------------------------------------------------------------- H-CH-4
for family, entry in model_entries.items():
    ch4 = entry.get("ch4") or {}
    if not has_rows:
        check(ch4.get("n") == REPEATS, f"{family} H-CH-4: n={ch4.get('n')} (ожидалось {REPEATS})")
        continue
    subset = rows_by.get(("H-CH-4", family), [])
    check(ch4.get("n") == len(subset), f"{family} H-CH-4: n сходится")
    recovered = sum(1 for r in subset if r["iou"] >= IOU_MIN)
    check(
        recovered == ch4.get("same_pattern"),
        f"{family} H-CH-4: same_pattern {ch4.get('same_pattern')} пересчитан как {recovered}",
    )

# ---------------------------------------------------------------- H-AB-2
ab2 = None
for entry in model_entries.values():
    if entry.get("ab2"):
        ab2 = entry["ab2"]
check(ab2 is not None, "есть секция H-AB-2")
if ab2:
    pairs = ab2.get("pairs") or []
    check(len(pairs) == REPEATS, f"H-AB-2: пар {len(pairs)} (ожидалось {REPEATS})")
    valid_pairs = [p for p in pairs if p.get("valid")]
    for pair in valid_pairs:
        gap = abs(pair["removed_fraction_left"] - pair["removed_fraction_right"])
        check(
            gap <= MASS_TOL + 1e-9,
            f"H-AB-2 пара {pair['pair']}: масса выровнена (gap={gap:.4f})",
        )
        recomputed = round(pair["iou_left"] - pair["iou_right"], 4)
        check(
            abs(recomputed - pair["diff"]) < 1e-9,
            f"H-AB-2 пара {pair['pair']}: diff пересчитан {recomputed:+.4f}",
        )
    signs = [1 if p["diff"] > 0 else (-1 if p["diff"] < 0 else 0) for p in valid_pairs]
    counts = {str(k): v for k, v in Counter(signs).items()}
    check(counts == ab2.get("sign_counts"), f"H-AB-2: знаки сходятся {counts}")
    check(len(valid_pairs) == ab2.get("n_valid"), "H-AB-2: число валидных пар сходится")
    dominant = Counter(signs).most_common(1)[0] if signs else (0, 0)
    expected = (
        "confirmed_structural_asymmetry"
        if dominant[1] >= SIGN_MIN
        else "refuted_asymmetry_is_mass"
    )
    check(
        ab2.get("verdict") == expected,
        f"H-AB-2: вердикт {ab2.get('verdict')} соответствует критерию (пересчёт: {expected})",
    )
    mean_diff = round(float(sum(p["diff"] for p in valid_pairs) / len(valid_pairs)), 4) if valid_pairs else 0.0
    check(
        abs(mean_diff - ab2.get("mean_diff", 0.0)) < 1e-9,
        f"H-AB-2: средняя разность {ab2.get('mean_diff')} пересчитана {mean_diff}",
    )

# ---------------------------------------------------------------- вердикты
# H-CH-2: подтверждена, если хотя бы одно условие (кроме none) роняет рисунок.
for family, entry in model_entries.items():
    ch2 = entry.get("ch2") or {}
    broken = [
        cond for cond, summary in ch2.items()
        if cond != "none" and summary.get("same_pattern", 0) < SIGN_MIN
    ]
    if family == "WP4_R-9_s2000_seed42":
        verdict = "confirmed_specific_channels" if broken else "refuted_not_channel_specific"
        entry["_ch2_verdict_recomputed"] = verdict
        print(f"[verify] H-CH-2 struct_2: ломают {len(broken)} условий -> {verdict}")

for family, entry in model_entries.items():
    ch3 = entry.get("ch3") or {}
    if family == "WP4_R-9_s2000_seed42":
        verdict = (
            "confirmed_orientation_returns"
            if ch3.get("identity_orientation", 0) >= SIGN_MIN
            else "refuted_orientation_not_identity"
        )
        entry["_ch3_verdict_recomputed"] = verdict
        print(f"[verify] H-CH-3 struct_2: {ch3.get('identity_orientation')}/12 -> {verdict}")

for family, entry in model_entries.items():
    ch4 = entry.get("ch4") or {}
    if family == "WP4_R-9_s2000_seed42":
        verdict = (
            "confirmed_at_least_one_channel_needed"
            if ch4.get("same_pattern", 0) < SIGN_MIN
            else "refuted_alive_channel_carries_shape"
        )
        entry["_ch4_verdict_recomputed"] = verdict
        print(f"[verify] H-CH-4 struct_2: {ch4.get('same_pattern')}/12 -> {verdict}")

print()
if errors:
    print(f"ИТОГ: {len(errors)} ошибок, {len(warnings)} предупреждений")
    for err in errors:
        print("  -", err)
    sys.exit(1)
print(f"ИТОГ: 0 ошибок, {len(warnings)} предупреждений")
