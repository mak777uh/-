"""Независимая проверка артефакта E02b alive-open (H-CH-6).

Как и `e02b_verify_closures.py`: сводки пересчитываются из сырых строк
(`alive_open_rows.jsonl`), вердикт переписывается заново по протоколу
`reports/2026-10-22-alive-open-plan.md`. Если строк нет (свежий клон — они
локальные), проверяется внутренняя согласованность артефакта.

Запуск: `python e02b_verify_alive_open.py` из корня репозитория.
"""
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve()
EXP = HERE.parents[1]
OUT = EXP / "alive_open_exploratory.json"
ROWS = EXP / "alive_open_rows.jsonl"

IOU_MIN = 0.5
SIGN_MIN = 11
REPEATS = 12
DEAD_ALIVE = 0.05

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
    warn(False, f"нет {ROWS.name}: сверка сводок со строками пропущена (файл локальный)")

check(artifact.get("protocol") == "reports/2026-10-22-alive-open-plan.md",
      "артефакт ссылается на замороженный протокол")
check(artifact.get("steps") == 2000, "шагов 2000")
check(artifact.get("repeats") == REPEATS, f"повторов {REPEATS}")

models = {m["family"]: m for m in artifact.get("models") or []}
check("WP4_R-9_s2000_seed42" in models, "есть модель struct_2")
check("untrained_current_arch" in models, "есть контроль необученной архитектуры")

rows_by = {}
for row in rows:
    rows_by.setdefault((row["family"], row["condition"]), []).append(row)

for family, entry in models.items():
    check(entry.get("proto_class") in {"struct_2", "struct_1"},
          f"{family}: класс прототипа {entry.get('proto_class')}")
    for cond, summary in (entry.get("conditions") or {}).items():
        check(summary.get("n") == REPEATS, f"{family} {cond}: n={REPEATS}")
        check(summary.get("classes"), f"{family} {cond}: классы записаны")
        check(0.0 <= summary.get("mean_body_iou", -1) <= 1.0,
              f"{family} {cond}: mean_body_iou в [0,1]")
        if not has_rows:
            continue
        subset = rows_by.get((family, cond), [])
        check(len(subset) == summary.get("n"),
              f"{family} {cond}: n сходится со строками ({len(subset)})")
        body = sum(1 for r in subset if r["body_iou"] >= IOU_MIN)
        texture = sum(1 for r in subset if r["texture_iou"] >= IOU_MIN)
        alive = sum(1 for r in subset if r["alive_fraction"] >= DEAD_ALIVE)
        check(body == summary.get("body_returned"),
              f"{family} {cond}: body_returned {summary.get('body_returned')} пересчитан как {body}")
        check(texture == summary.get("texture_returned"),
              f"{family} {cond}: texture_returned {summary.get('texture_returned')} пересчитан как {texture}")
        check(alive == summary.get("alive"),
              f"{family} {cond}: alive {summary.get('alive')} пересчитан как {alive}")
        check(dict(Counter(r["final_class"] for r in subset)) == summary.get("classes"),
              f"{family} {cond}: классы сходятся")
        mean_body = round(float(sum(r["body_iou"] for r in subset) / len(subset)), 4)
        check(abs(mean_body - summary.get("mean_body_iou", 0.0)) < 1e-6,
              f"{family} {cond}: средний body_iou сходится ({mean_body})")

# --- вердикт по протоколу -----------------------------------------------------
st = models.get("WP4_R-9_s2000_seed42")
verdict = artifact.get("verdict") or {}
if st:
    none_st = (st.get("conditions") or {}).get("none", {})
    open_st = (st.get("conditions") or {}).get("alive_open", {})
    gate_ok = none_st.get("body_returned", 0) >= SIGN_MIN
    if not gate_ok:
        expected = {"applicable": False}
    elif open_st.get("body_returned", 0) >= SIGN_MIN:
        expected = {"applicable": True, "verdict": "refuted_body_rederived"}
    elif (REPEATS - open_st.get("body_returned", 0)) >= SIGN_MIN:
        expected = {"applicable": True, "verdict": "confirmed_body_carries_geometry"}
    else:
        expected = {"applicable": True, "verdict": "inconclusive"}
    check(bool(verdict.get("applicable")) == expected["applicable"],
          f"вердикт applicable={verdict.get('applicable')} соответствует протоколу")
    if expected.get("verdict"):
        check(verdict.get("verdict") == expected["verdict"],
              f"вердикт {verdict.get('verdict')} соответствует пересчёту ({expected['verdict']})")
    print("[verify] H-CH-6:", verdict.get("verdict"), "—", (verdict.get("reason") or "")[:160])

print()
if errors:
    print(f"ИТОГ: {len(errors)} ошибок, {len(warnings)} предупреждений")
    for err in errors:
        print("  -", err)
    sys.exit(1)
print(f"ИТОГ: 0 ошибок, {len(warnings)} предупреждений")
